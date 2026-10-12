"""The struggle corpus: where recorded pipeline runs got stuck, grouped so the commonest cause is fixed first.

A struggle is a moment a run's own record says something went wrong: a verifying step rejected what a generating
step produced, a step raised, a stage failed. `build` reads the run folders the recorder wrote
(`run_recorder.py`, `logs/runs/<id>/`) and groups the struggles by the step that reported them and the verdict it
gave. Each entry holds how often it happened against how often the step ran, the runs, models and commits it was
seen on, the LLM call that came nearest before it (the prompt to read first) and its latest examples.

The corpus outlives the runs it was built from: the recorder prunes old run folders, so a run is counted once and
its counts stay. An entry's `review` block is written by whoever traced the cause, never by `build`.

It only reads and reports. It calls no model and changes no prompt; read it with `scripts/struggle_corpus.py`.
"""

import collections
import glob
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

import run_recorder

REASON_LIMIT = 400
EXAMPLES_KEPT = 3
_VERSION = 1

Verdict = Tuple[str, str]


@dataclass(frozen=True)
class Struggle:
    step: str
    signal: str
    reason: str
    nearest_llm: str
    trace_file: str


@dataclass(frozen=True)
class RunStruggles:
    run_id: str
    label: str
    commit: str
    model: str
    checks: Dict[str, int]
    struggles: Tuple[Struggle, ...]


def corpus_path() -> str:
    default = os.path.join(os.path.dirname(run_recorder.runs_root()), "struggle_corpus.json")
    return os.environ.get("PROVABLE_STRUGGLE_CORPUS") or default


def _red_gate(output: Dict[str, Any]) -> List[Verdict]:
    return [] if output.get("approved") else [(output.get("status"), output.get("reason"))]


def _page_test(output: Dict[str, Any]) -> List[Verdict]:
    if output.get("status") == "pass":
        return []
    signal = "control_not_found" if output.get("control_not_found") else output.get("status")
    return [(signal, output.get("reason"))]


def _qa_gate(output: Dict[str, Any]) -> List[Verdict]:
    if not output.get("passed"):
        return [(output.get("verdict"), json.dumps(output.get("defects"), ensure_ascii=False))]
    if output.get("attempts"):
        return [("reworked", json.dumps(output.get("reworked"), ensure_ascii=False))]
    return []


def _visual_review(output: Dict[str, Any]) -> List[Verdict]:
    could_not_look = [("error", output["error"])] if output.get("error") else []
    return could_not_look + [("not_repaired", problem) for problem in output.get("not_repaired") or []]


def _spec_review(output: Dict[str, Any]) -> List[Verdict]:
    return [("conflict", conflict.get("reason")) for conflict in output.get("conflicts") or []]


def _reconsidered_test(output: Dict[str, Any]) -> List[Verdict]:
    return [("first_test_wrong", (output.get("red_eval") or {}).get("reason"))]


def _rule_fix(output: Dict[str, Any]) -> List[Verdict]:
    return [] if output.get("status") == "fixed" else [(output.get("status"), output.get("reason"))]


# The steps that judge another step's work, and how each one's recorded output says "rejected".
_VERDICTS: Dict[str, Callable[[Dict[str, Any]], List[Verdict]]] = {
    "tdd.red_gate": _red_gate,
    "tdd.reconsider_test": _reconsidered_test,
    "page_test.run": _page_test,
    "page_test.prove": _page_test,
    "qa.gate": _qa_gate,
    "visual.review": _visual_review,
    "engine.spec_review": _spec_review,
    "rule_fix.fix": _rule_fix,
}


def _load(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _verdicts(record: Dict[str, Any], passed_through: set) -> List[Verdict]:
    error = record.get("error")
    if error:
        # An exception is recorded by every step it leaves; it is a struggle of the one that raised it.
        return [] if (error, record["step"]) in passed_through else [(error.split(":", 1)[0], error)]
    reader = _VERDICTS.get(record["step"])
    output = record.get("output")
    return reader(output) if reader and isinstance(output, dict) else []


def _shared_steps(a: Dict[str, Any], b: Dict[str, Any]) -> int:
    shared = 0
    for ours, theirs in zip(a.get("caller_chain") or [], b.get("caller_chain") or []):
        if ours != theirs:
            break
        shared += 1
    return shared


def _nearest_llm(answers: List[Dict[str, Any]], record: Dict[str, Any]) -> str:
    """The LLM call to read first for `record`: of the answers given before it, the one nearest in the call
    tree, then one on its own thread, then the latest (a pool gates on worker threads what one answer wrote).
    It is where to start reading, not a verdict on which prompt is at fault."""
    if not answers:
        return ""
    nearest = max(enumerate(answers), key=lambda item: (
        _shared_steps(item[1], record), item[1].get("thread") == record.get("thread"), item[0]))
    return nearest[1]["step"]


def read_run(folder: str) -> RunStruggles:
    """The struggles one finished run recorded, and how often each step ran (the rate's denominator)."""
    meta = _load(os.path.join(folder, "run.json"))
    summary = _load(os.path.join(folder, "summary.json"))
    files = sorted(glob.glob(os.path.join(folder, "trace", "*.json")))
    records = [(os.path.basename(path), _load(path)) for path in files]
    passed_through = {(record["error"], ancestor) for _, record in records if record.get("error")
                      for ancestor in record.get("caller_chain") or []}

    checks: Dict[str, int] = collections.Counter()
    struggles: List[Struggle] = []
    answers: List[Dict[str, Any]] = []
    for name, record in records:
        step = record["step"]
        checks[step] += 1
        for signal, reason in _verdicts(record, passed_through):
            struggles.append(Struggle(step, str(signal), str(reason or ""), _nearest_llm(answers, record), name))
        if record.get("kind") == "llm":
            answers.append(record)

    for stage in summary.get("stages") or []:
        if stage.get("status") == "skipped":
            continue
        step = f"stage.{stage['name']}"
        checks[step] += 1
        if stage.get("status") == "failed":
            struggles.append(Struggle(step, "failed", str(stage.get("error") or ""), "", "summary.json"))

    return RunStruggles(run_id=meta.get("id") or os.path.basename(folder), label=meta.get("label") or "",
                        commit=(meta.get("git") or {}).get("commit") or "",
                        model=(meta.get("llm") or {}).get("model") or "",
                        checks=dict(checks), struggles=tuple(struggles))


def _new_entry(struggle: Struggle, run: RunStruggles) -> Dict[str, Any]:
    return {"step": struggle.step, "signal": struggle.signal, "occurrences": 0, "runs": [], "labels": [],
            "models": [], "nearest_llm": {}, "first_seen": run.run_id, "last_seen": run.run_id,
            "last_commit": run.commit, "examples": [],
            "review": {"status": "candidate", "cause": "", "knowledge": ""}}


def _add_once(values: List[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def _merge(corpus: Dict[str, Any], run: RunStruggles) -> None:
    corpus["runs"].append(run.run_id)
    for step, count in run.checks.items():
        corpus["checks"][step] = corpus["checks"].get(step, 0) + count
    for struggle in run.struggles:
        entry = corpus["entries"].setdefault(f"{struggle.step}/{struggle.signal}", _new_entry(struggle, run))
        entry["occurrences"] += 1
        entry["last_seen"], entry["last_commit"] = run.run_id, run.commit
        _add_once(entry["runs"], run.run_id)
        _add_once(entry["labels"], run.label)
        _add_once(entry["models"], run.model)
        if struggle.nearest_llm:
            entry["nearest_llm"][struggle.nearest_llm] = entry["nearest_llm"].get(struggle.nearest_llm, 0) + 1
        example = {"run": run.run_id, "trace": struggle.trace_file, "reason": struggle.reason[:REASON_LIMIT]}
        entry["examples"] = (entry["examples"] + [example])[-EXAMPLES_KEPT:]


def build(runs_root: str, path: str) -> Dict[str, Any]:
    """Adds every finished run not yet counted to the corpus at `path`, writes it and returns it."""
    corpus = _load(path) if os.path.exists(path) else {"version": _VERSION, "runs": [], "checks": {}, "entries": {}}
    names = sorted(os.listdir(runs_root)) if os.path.isdir(runs_root) else []
    for name in names:
        folder = os.path.join(runs_root, name)
        if name in corpus["runs"] or not os.path.exists(os.path.join(folder, "summary.json")):
            continue
        _merge(corpus, read_run(folder))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    return corpus


def report_lines(corpus: Dict[str, Any]) -> List[str]:
    """One line per kind of struggle, the most frequent first: how often of how many checks, and what to read."""
    runs, entries = corpus["runs"], corpus["entries"]
    lines = [f"{len(runs)} run{'' if len(runs) == 1 else 's'} read, {len(entries)} kinds of struggle"]
    for entry_id, entry in sorted(entries.items(), key=lambda item: (-item[1]["occurrences"], item[0])):
        nearest = max(entry["nearest_llm"], key=entry["nearest_llm"].get) if entry["nearest_llm"] else "-"
        lines.append(f"{entry['occurrences']:4d} of {corpus['checks'].get(entry['step'], 0):<4d} {entry_id:44} "
                     f"runs={len(entry['runs']):<3d} last={entry['last_seen'][:13]}  nearest_llm={nearest}  "
                     f"[{entry['review']['status']}]")
    return lines
