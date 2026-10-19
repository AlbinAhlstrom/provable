"""One folder per pipeline run, so any run can be diagnosed or compared after the fact.

A recorded run (a kickstart, or one spec execution) writes to `logs/runs/<timestamp>_<kind>_<label>/`:

    run.json        what ran: kind, label, start time, git commit (and whether the tree was dirty), model settings
    trace/          one JSON per traced step and LLM call (input, output, duration, model, tokens), see pipeline_trace.py
    summary.json    the verdict: status (ok | degraded | error), every stage with its outcome, when it started and
                    the files it changed (with their line counts), a file -> last-writing-stage provenance map, how
                    much of the wall time the stages cover, LLM totals, and the run's result
    workspace/      a copy of the generated `src/` and `tests/` plus QA screenshots, kept after the next run overwrites them

`logs/runs/LATEST` names the newest run. Recording is on by default; PROVABLE_RUNS_DIR moves the folder,
PROVABLE_RUNS_KEEP (default 30, 0 keeps all) bounds how many of the newest runs are kept (the newest run of each kind per commit and any run a kept run replays stay too) and PROVABLE_RECORD_RUNS=0 switches it off.
Nothing here ever changes pipeline behaviour: failures to write are printed and swallowed, pipeline errors propagate.
"""

import contextlib
import functools
import hashlib
import inspect
import json
import os
import platform
import re
import shutil
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional

import llm_cost
import pipeline_trace

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))
_SNAPSHOT_DIRS = ("src", "tests")
_SKIP_DIRS = {"node_modules", "__pycache__", ".git", "dist"}
_RESULT_KEYS = ("success", "status", "error", "stage_failures", "spec_conflicts", "timing_breakdown", "qa",
                "attempts", "files_updated", "phase", "rolled_back", "verification_models", "app_inventory")

_current: Optional["Run"] = None


def _enabled() -> bool:
    return os.environ.get("PROVABLE_RECORD_RUNS", "1") != "0"


def runs_root() -> str:
    return os.environ.get("PROVABLE_RUNS_DIR") or os.path.join(_REPO_ROOT, "logs", "runs")


def current_run() -> Optional["Run"]:
    return _current


def _write_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=repr)


def _git_info() -> Dict[str, Any]:
    def git(*args: str) -> Optional[str]:
        try:
            res = subprocess.run(["git", *args], cwd=_REPO_ROOT, capture_output=True, text=True, timeout=10)
            return res.stdout.rstrip() if res.returncode == 0 else None  # a porcelain line may start with a space
        except Exception:
            return None
    status = git("status", "--porcelain")
    return {"commit": git("rev-parse", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(status) if status is not None else None,
            "dirty_files": [ln[3:] for ln in status.splitlines()][:50] if status else []}


def _llm_settings() -> Dict[str, Any]:
    import llm_provider
    import llm_replay
    connection = llm_provider.connection()
    base = connection.base_url
    return {"model": connection.model, "provider": os.environ.get("LLM_PROVIDER") or None,
            "stage_models": llm_provider.stage_models(),
            "reasoning_effort": os.environ.get("LLM_REASONING_EFFORT", "low"),
            "replay": llm_replay.active(),
            "replay_live": llm_replay.live(),
            "base_url_host": re.sub(r"^https?://([^/]+).*", r"\1", base) if base else None}


def _fingerprint(workspace_dir: Optional[str]) -> Dict[str, tuple]:
    """rel path -> (size, mtime_ns) of the generated sources; cheap enough to take around every stage."""
    prints: Dict[str, tuple] = {}
    if not workspace_dir:
        return prints
    for top in _SNAPSHOT_DIRS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(workspace_dir, top)):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for name in filenames:
                full = os.path.join(dirpath, name)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                prints[os.path.relpath(full, workspace_dir).replace(os.sep, "/")] = (st.st_size, st.st_mtime_ns)
    return prints


def _line_count(path: str) -> Optional[int]:
    try:
        with open(path, encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return None


def _owned(path: str, owns: tuple) -> bool:
    return any(path == o or path.startswith(o.rstrip("/") + "/") for o in owns)


class StageHandle:
    """One pipeline stage's outcome. Created by stage_begin(); finish with ok(), fail(reason) or skip(reason).
    A handle left open when the run ends is closed as ok, or as failed when an exception ended the run.

    The files a stage changed are whatever differs in the workspace between its start and its end. Stages that run at
    the same time would each be credited with the other's files, so a concurrent stage declares what it `owns`
    (workspace-relative files or folders, `()` for a stage that writes nothing): it is credited with exactly those, and
    the stages open alongside it are not."""

    def __init__(self, run: Optional["Run"], name: str, owns: Optional[tuple] = None):
        self._run = run
        self.owns = owns
        self._t0 = time.time()
        self._t1: Optional[float] = None
        # Which stages were open alongside which is decided on the monotonic high-resolution clock: time.time() ticks
        # coarsely on Windows, and two stages that open and close within one tick must still be ordered correctly.
        self._c0 = time.perf_counter()
        self._c1: Optional[float] = None
        self.record: Dict[str, Any] = {"name": name, "status": "running", "error": None, "notes": {},
                                       "started_at": time.strftime("%H:%M:%S"),
                                       "t_offset_s": round(self._t0 - run.started, 3) if run else 0.0,
                                       "files_changed": []}
        self._before = _fingerprint(run.workspace_dir) if run else {}
        self._closed = False

    def note(self, key: str, value: Any) -> None:
        self.record["notes"][key] = value

    def _close(self, status: str, reason: Optional[str]) -> None:
        if self._closed:
            return
        self._closed = True
        self._t1 = time.time()
        self._c1 = time.perf_counter()
        self.record.update(status=status, error=reason, duration_s=round(self._t1 - self._t0, 3))
        if self._run:
            after = _fingerprint(self._run.workspace_dir)
            changes = [{"path": p, "change": "added" if p not in self._before else "modified"}
                       for p, fp in after.items() if self._before.get(p) != fp]
            changes += [{"path": p, "change": "deleted"} for p in self._before if p not in after]
            changes = [c for c in changes if self._credited(c["path"])]
            for change in changes:
                self._run.measure(change)
            self.record["files_changed"] = sorted(changes, key=lambda c: c["path"])
            if status == "failed":
                print(f"[Run:{self._run.id}] stage '{self.record['name']}' failed: {reason}", flush=True)

    def _credited(self, path: str) -> bool:
        if self.owns is not None:
            return _owned(path, self.owns)
        alongside = [h for h in self._run.stages if h is not self and h.owns and (h._c1 is None or h._c1 >= self._c0)]
        return not any(_owned(path, h.owns) for h in alongside)

    def ok(self) -> None:
        self._close("ok", None)

    def fail(self, reason: str) -> None:
        self._close("failed", str(reason))

    def skip(self, reason: str) -> None:
        self._close("skipped", str(reason))


def stage_begin(name: str, owns: Optional[tuple] = None) -> StageHandle:
    """Start a stage in the active run (inert when none is active). Stages are listed in start order. A stage that
    runs at the same time as another passes `owns` (see StageHandle)."""
    handle = StageHandle(_current, name, owns)
    if _current:
        _current.stages.append(handle)
    return handle


@contextlib.contextmanager
def stage(name: str, owns: Optional[tuple] = None):
    """Context-manager form of stage_begin: an exception marks the stage failed and propagates."""
    handle = stage_begin(name, owns)
    try:
        yield handle
    except BaseException as exc:
        handle.fail(f"{type(exc).__name__}: {exc}")
        raise
    else:
        handle.ok()  # no-op when the body already closed the handle with fail() or skip()


class Run:
    def __init__(self, kind: str, label: str, workspace_dir: Optional[str]):
        self.kind = kind
        self.label = label
        self.workspace_dir = workspace_dir
        self.started = time.time()
        stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(self.started))
        slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:40] or "run"
        self.id = base_id = f"{stamp}_{kind}_{slug}"
        suffix = 1
        while os.path.exists(os.path.join(runs_root(), self.id)):  # two runs inside one second keep separate folders
            suffix += 1
            self.id = f"{base_id}-{suffix}"
        self.dir = os.path.join(runs_root(), self.id)
        self.trace_dir = os.path.join(self.dir, "trace")
        self.stages: List[StageHandle] = []
        self.result: Dict[str, Any] = {}
        self.error: Optional[str] = None
        self._lines: Dict[str, int] = {}  # last known line count of each generated file

    def measure(self, change: Dict[str, Any]) -> None:
        """Adds the file's line count to a change record, and by how much the stage grew or shrank it."""
        path = change["path"]
        if change["change"] == "deleted":
            self._lines.pop(path, None)
            return
        lines = _line_count(os.path.join(self.workspace_dir, path))
        if lines is None:
            return
        change["lines"] = lines
        if change["change"] == "modified" and path in self._lines:
            change["delta"] = lines - self._lines[path]
        self._lines[path] = lines

    def _timeline(self, duration_s: float) -> Dict[str, float]:
        """How much of the wall time lies inside a stage (overlapping stages counted once) and how much outside."""
        covered, reach = 0.0, self.started
        for start, end in sorted((h._t0, h._t1 or h._t0) for h in self.stages):
            if end > reach:
                covered += end - max(start, reach)
                reach = end
        covered = min(covered, duration_s)
        return {"in_stages_s": round(covered, 2), "outside_stages_s": round(duration_s - covered, 2),
                "stage_time_sum_s": round(sum(h.record.get("duration_s") or 0 for h in self.stages), 2)}

    def begin(self) -> None:
        os.makedirs(self.trace_dir, exist_ok=True)
        _write_json(os.path.join(self.dir, "run.json"), {
            "id": self.id, "kind": self.kind, "label": self.label,
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.started)),
            "git": _git_info(), "llm": _llm_settings(), "python": platform.python_version(),
            "workspace_dir": self.workspace_dir})
        pipeline_trace.set_trace_dir(self.trace_dir)
        print(f"[Run] recording {self.id} -> {self.dir}", flush=True)

    # ── finishing ────────────────────────────────────────────────────────────
    def _snapshot(self) -> None:
        if not self.workspace_dir or not os.path.isdir(self.workspace_dir):
            return
        snap = os.path.join(self.dir, "workspace")
        ignore = shutil.ignore_patterns(*_SKIP_DIRS)
        for top in _SNAPSHOT_DIRS:
            source = os.path.join(self.workspace_dir, top)
            if os.path.isdir(source):
                shutil.copytree(source, os.path.join(snap, top), ignore=ignore, dirs_exist_ok=True)
        reports = os.path.join(self.workspace_dir, ".qa_reports")
        if os.path.isdir(reports):
            for name in os.listdir(reports):
                path = os.path.join(reports, name)
                if os.path.isfile(path) and os.path.getmtime(path) >= self.started:
                    os.makedirs(os.path.join(snap, "qa_reports"), exist_ok=True)
                    shutil.copy2(path, os.path.join(snap, "qa_reports", name))

    def _provenance(self) -> Dict[str, str]:
        last: Dict[str, str] = {}
        for handle in self.stages:
            for change in handle.record["files_changed"]:
                if change["change"] == "deleted":
                    last.pop(change["path"], None)
                else:
                    last[change["path"]] = handle.record["name"]
        return last

    def finish(self) -> None:
        pipeline_trace.set_trace_dir("")
        for handle in self.stages:  # a stage still open when the run ends is the one the exception interrupted
            handle.fail(self.error) if self.error else handle.ok()
        records = [h.record for h in self.stages]
        failed = [r["name"] for r in records if r["status"] == "failed"]
        result_failures = [f.get("stage") for f in self.result.get("stage_failures") or []]
        if self.error:
            status = "error"
        elif failed or result_failures or self.result.get("success") is False:
            status = "degraded"
        else:
            status = "ok"
        duration_s = round(time.time() - self.started, 2)
        summary = {
            "id": self.id, "kind": self.kind, "label": self.label, "status": status, "error": self.error,
            "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_s": duration_s, "timeline": self._timeline(duration_s),
            "stages": records, "failed_stages": sorted(set(failed) | {s for s in result_failures if s}),
            "provenance": self._provenance(), "llm": llm_totals(self.trace_dir), "result": self.result,
        }
        try:
            self._snapshot()
        except Exception as err:
            print(f"[Run] could not snapshot the workspace: {err}", flush=True)
        _write_json(os.path.join(self.dir, "summary.json"), summary)
        with open(os.path.join(runs_root(), "LATEST"), "w", encoding="utf-8") as f:
            f.write(self.id)
        _prune()
        cost = summary["llm"]["cost_sek"]
        print(f"[Run] {status.upper()}: {self.id} ({summary['duration_s']}s, {summary['llm']['calls']} LLM calls, "
              f"{'cost unknown' if cost is None else f'{cost:.2f} SEK'}). "
              f"Report: python scripts/trace_report.py", flush=True)


def llm_totals(trace_dir: str) -> Dict[str, Any]:
    """The LLM calls of one trace folder, added up overall and per stage: calls, errors, tokens, time and what they
    cost (llm_cost.py). A total that includes a call on a model without a price is None, and the model is named."""
    counters = ("prompt_tokens", "cached_tokens", "completion_tokens", "reasoning_tokens")

    def empty() -> Dict[str, Any]:
        return {"calls": 0, "errors": 0, "replayed": 0, **{c: 0 for c in counters}, "total_s": 0.0, "cost_usd": 0.0}

    totals, by_stage, unpriced, rate = empty(), {}, set(), llm_cost.usd_to_sek()
    for name in sorted(os.listdir(trace_dir)):
        try:
            with open(os.path.join(trace_dir, name), encoding="utf-8") as f:
                entry = json.load(f)
        except Exception:
            continue
        if entry.get("kind") != "llm":
            continue
        meta = entry.get("meta") or {}
        billed = bool(meta.get("prompt_tokens") or meta.get("completion_tokens"))  # a call that failed has no usage
        cost = llm_cost.call_cost_usd(meta) if billed else 0.0
        if cost is None:
            unpriced.add(str(meta.get("model")))
        stage_name = (entry.get("input") or {}).get("stage", "general")
        for target in (totals, by_stage.setdefault(stage_name, empty())):
            target["calls"] += 1
            target["errors"] += 1 if (meta.get("error") or entry.get("error")) else 0
            target["replayed"] += 1 if meta.get("replayed_from") else 0  # answered from a recorded run (llm_replay.py)
            for counter in counters:
                target[counter] += meta.get(counter) or 0
            target["total_s"] = round(target["total_s"] + (entry.get("duration_s") or 0), 3)
            target["cost_usd"] = None if cost is None or target["cost_usd"] is None else target["cost_usd"] + cost
    for target in (totals, *by_stage.values()):
        usd = target["cost_usd"]
        target["cost_usd"] = None if usd is None else round(usd, 6)
        target["cost_sek"] = None if usd is None else round(usd * rate, 4)
    return {**totals, "usd_to_sek": rate, "prices_as_of": llm_cost.PRICES_AS_OF, "unpriced_models": sorted(unpriced),
            "by_stage": by_stage}


def backfill_costs() -> List[str]:
    """Prices the finished runs whose summary holds no cost yet, from the tokens their trace recorded, at today's
    price table and exchange rate. Returns the ids of the runs it priced."""
    root, priced = runs_root(), []
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        summary_path, trace_dir = os.path.join(root, name, "summary.json"), os.path.join(root, name, "trace")
        if not (os.path.exists(summary_path) and os.path.isdir(trace_dir)):
            continue
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)
        if "cost_sek" in (summary.get("llm") or {}):
            continue
        summary["llm"] = llm_totals(trace_dir)
        _write_json(summary_path, summary)
        priced.append(name)
    return priced


def _prune() -> None:
    """Keeps the newest PROVABLE_RUNS_KEEP runs (0: all), the newest run of each kind for every commit, so each code
    version has a run to compare against, and every run a kept run replays, so resampling never loses its base."""
    keep = int(os.environ.get("PROVABLE_RUNS_KEEP") or 30)
    root = runs_root()
    runs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    if keep <= 0 or len(runs) <= keep:
        return
    records = {run: _run_record(os.path.join(root, run)) for run in runs}
    newest_per_commit = {((r.get("git") or {}).get("commit"), r.get("kind")): run for run, r in records.items()}
    kept = set(runs[-keep:]) | {run for (commit, _), run in newest_per_commit.items() if commit}
    kept |= {name for run in kept for name in (records[run].get("llm") or {}).get("replay") or []}
    for old in runs:
        if old not in kept:
            shutil.rmtree(os.path.join(root, old), ignore_errors=True)


def _run_record(run_dir: str) -> Dict[str, Any]:
    try:
        with open(os.path.join(run_dir, "run.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _summarise(result: Any) -> Dict[str, Any]:
    return {k: result[k] for k in _RESULT_KEYS if k in result} if isinstance(result, dict) else {}


@contextlib.contextmanager
def recorded_run(kind: str, label: str, workspace_dir: Optional[str] = None):
    """Record everything inside the block as one run. Inside an already-recorded run it joins that run."""
    global _current
    if _current is not None or not _enabled():
        yield _current
        return
    run = Run(kind, label, workspace_dir)
    try:
        run.begin()
    except Exception as err:  # recording must never stop the pipeline
        print(f"[Run] recording disabled for this run: {err}", flush=True)
        pipeline_trace.set_trace_dir("")
        yield None
        return
    _current = run
    try:
        yield run
    except BaseException as exc:
        run.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        _current = None
        try:
            run.finish()
        except Exception as err:
            print(f"[Run] could not write the summary: {err}", flush=True)


def recorded(kind: str, label: str) -> Callable:
    """Decorator form: record the call as a run. `label` names the argument used as the run's label; the workspace
    is the call's `workspace_dir` argument, else the configured workspace. The returned dict feeds the verdict."""
    def decorator(fn: Callable) -> Callable:
        signature = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            bound = signature.bind_partial(*args, **kwargs)
            workspace_dir = bound.arguments.get("workspace_dir")
            if not workspace_dir:
                from config_loader import get_workspace_base
                workspace_dir = get_workspace_base()
            owns_run = _current is None
            with recorded_run(kind, str(bound.arguments.get(label, "")), workspace_dir=workspace_dir) as run:
                result = fn(*args, **kwargs)
                if run is not None and owns_run:
                    run.result = _summarise(result)
                return result
        return wrapper
    return decorator
