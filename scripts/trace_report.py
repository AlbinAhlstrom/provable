#!/usr/bin/env python3
"""Read a recorded pipeline run (see backend/run_recorder.py). Runs live in logs/runs/<id>/.

Usage:
    python scripts/trace_report.py                     report on the latest run
    python scripts/trace_report.py <run> [--full N]    <run> is a run id, a run folder or a bare trace folder
    python scripts/trace_report.py --list              one line per recorded run, newest last
    python scripts/trace_report.py --compare A B       what changed between two runs (code version, stages, files)

The report shows the verdict, where the wall time went, each stage (when it started, status, time, the files it wrote
with their line counts, why it failed), what the visual review saw and repaired, the generated frontend's files that nothing imports,
LLM totals per stage (with hidden reasoning tokens and output speed) and the traced call tree on a timeline.
`--full N` prints the complete input/output of traced step N (the prompt and the raw answer for an LLM call).
"""
import collections
import glob
import json
import os
import sys

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "runs")
RUNS = os.environ.get("PROVABLE_RUNS_DIR") or os.path.abspath(RUNS)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve(arg):
    """-> (run folder or None, trace folder). Accepts nothing (latest), a run id, a run folder or a trace folder."""
    if arg is None:
        latest = os.path.join(RUNS, "LATEST")
        if not os.path.exists(latest):
            sys.exit(f"No recorded runs in {RUNS}. Start a kickstart (the app records every run).")
        arg = open(latest, encoding="utf-8").read().strip()
    folder = arg if os.path.isdir(arg) else os.path.join(RUNS, arg)
    if not os.path.isdir(folder):
        sys.exit(f"No such run or folder: {arg}")
    if os.path.exists(os.path.join(folder, "run.json")):
        return folder, os.path.join(folder, "trace")
    return None, folder


def traces(trace_dir):
    return [_load(f) for f in sorted(glob.glob(os.path.join(trace_dir, "*.json")))]


def list_runs():
    for name in sorted(d for d in os.listdir(RUNS) if os.path.isdir(os.path.join(RUNS, d))) if os.path.isdir(RUNS) else []:
        path = os.path.join(RUNS, name, "summary.json")
        if os.path.exists(path):
            s = _load(path)
            print(f"{s['status']:9} {s['duration_s']:7.1f}s  {s['llm']['calls']:3d} LLM calls  {name}")
        else:
            print(f"{'(open)':9} {'':8}  {'':14}  {name}")


def show_run(folder, trace_dir):
    meta, summary = _load(os.path.join(folder, "run.json")), None
    if os.path.exists(os.path.join(folder, "summary.json")):
        summary = _load(os.path.join(folder, "summary.json"))
    git = meta["git"]
    print(f"RUN {meta['id']}")
    print(f"  pitch/label : {meta['label'][:100]}")
    print(f"  code        : {git.get('branch')} {str(git.get('commit'))[:9]}{' (uncommitted changes: ' + ', '.join(git['dirty_files'][:5]) + ')' if git.get('dirty') else ''}")
    print(f"  model       : {meta['llm']['model']}  effort={meta['llm']['reasoning_effort']}  {meta['llm'].get('stage_model_overrides') or ''}")
    if not summary:
        print("  (no summary.json: the run did not finish, e.g. the backend was stopped mid-run)")
    else:
        print(f"  VERDICT     : {summary['status'].upper()} in {summary['duration_s']}s"
              + (f"  error: {summary['error']}" if summary.get("error") else ""))
        timeline = summary.get("timeline")
        if timeline:
            print(f"  wall time   : {timeline['in_stages_s']}s inside stages, {timeline['outside_stages_s']}s outside any stage; "
                  f"stage times add up to {timeline['stage_time_sum_s']}s "
                  f"({max(timeline['stage_time_sum_s'] - timeline['in_stages_s'], 0):.1f}s saved by running stages side by side)")
        print("\nSTAGES   (start = seconds after the run began)")
        for st in summary["stages"]:
            mark = {"ok": "ok     ", "failed": "FAILED ", "skipped": "skipped"}.get(st["status"], st["status"])
            notes = {k: v for k, v in (st.get("notes") or {}).items()
                     if k not in ("components", "warnings", "problems", "edits", "not_repaired")}
            start = f"start {st['t_offset_s']:>6.1f}s" if "t_offset_s" in st else ""
            print(f"  {mark} {st['name']:<22} {start} {st.get('duration_s', 0):>7.1f}s"
                  + (f"  {notes}" if notes else ""))
            if st.get("error"):
                print(f"          why: {str(st['error'])[:400]}")
            for change in st["files_changed"][:12]:
                size = f"  {change['lines']} lines" if "lines" in change else ""
                size += f" ({change['delta']:+d})" if "delta" in change else ""
                print(f"          {change['change']:<8} {change['path']}{size}")
            if len(st["files_changed"]) > 12:
                print(f"          ... and {len(st['files_changed']) - 12} more")
            for problem in (st.get("notes") or {}).get("problems") or []:
                print(f"          saw: {str(problem)[:200]}")
            for edit in (st.get("notes") or {}).get("edits") or []:
                mark_edit = f"repaired ({edit['occurrences']}x)" if edit.get("applied") else f"not applied: {edit.get('reason')}"
                print(f"          {mark_edit}  {edit.get('file')}: '{edit.get('find')}' -> '{edit.get('replace')}'"[:260])
            for missed in (st.get("notes") or {}).get("not_repaired") or []:
                print(f"          not repaired: {str(missed)[:200]}")
            for warning in (st.get("notes") or {}).get("warnings") or []:
                print(f"          warning: {str(warning)[:300]}")
        result = summary.get("result") or {}
        for conflict in result.get("spec_conflicts") or []:
            print(f"  spec conflict: {conflict}")
        show_inventory(result.get("app_inventory"))
        llm = summary["llm"]
        print(f"\nLLM  {llm['calls']} calls, {llm['errors']} errors, {llm['prompt_tokens']} prompt + "
              f"{llm['completion_tokens']} completion tokens"
              + (f" + {llm['reasoning_tokens']} hidden reasoning" if llm.get("reasoning_tokens") else "")
              + f", {llm['total_s']}s summed over calls (calls overlap, so this can exceed the wall time)")
        for stage_name, b in sorted(llm["by_stage"].items(), key=lambda kv: -kv[1]["total_s"]):
            speed = f"{b['completion_tokens'] / b['total_s']:>5.0f} tok/s" if b["total_s"] else ""
            print(f"  {stage_name:<34} {b['calls']:2d} calls {b['total_s']:>7.1f}s {b['prompt_tokens']:>7} in {b['completion_tokens']:>6} out"
                  + (f" {b['reasoning_tokens']:>6} reasoning" if b.get("reasoning_tokens") else "") + f" {speed}"
                  + (f"  {b['errors']} ERRORS" if b["errors"] else ""))
    print("\nTRACE")
    show_trace(traces(trace_dir))
    print(f"\nFolder: {folder}   (--full N prints one step; the generated app is in workspace/)")


def show_inventory(inventory):
    """The generated frontend: how much of it the served app reaches, and the files nothing imports."""
    if not inventory:
        return
    files = inventory["files"]
    print(f"\nFRONTEND  {len(files)} source files, {inventory['reachable_lines']} lines reached from {inventory['entry']}, "
          f"{inventory['unreachable_lines']} lines in {len(inventory['unreachable'])} file(s) nothing imports")
    if not inventory.get("entry_found", True):
        print(f"  !! {inventory['entry']} does not exist")
    for path in inventory["unreachable"]:
        print(f"  unreachable  {path}  {files[path]} lines")
    for path, lines in sorted(files.items(), key=lambda kv: -kv[1])[:5]:
        if path not in inventory["unreachable"]:
            print(f"  largest      {path}  {lines} lines")


def _hint(entry):
    """What a step worked on, when its first argument is a file."""
    args = (entry.get("input") or {}).get("args") or [] if isinstance(entry.get("input"), dict) else []
    first = args[0] if args else None
    return f" [{os.path.basename(first)}]" if isinstance(first, str) and os.path.splitext(first)[1] and len(first) < 300 else ""


def show_trace(entries):
    counts = collections.Counter()
    for e in entries:
        counts[e["step"]] += 1
        marker = "LLM " if e["kind"] == "llm" else "    "
        meta = e.get("meta") or {}
        err = e.get("error") or meta.get("error")
        tokens = f" {meta.get('prompt_tokens')}+{meta.get('completion_tokens')}tok" if meta.get("prompt_tokens") else ""
        tokens += f" +{meta['reasoning_tokens']} reasoning" if meta.get("reasoning_tokens") else ""
        tokens += f" {meta['completion_tok_per_s']:.0f}tok/s" if meta.get("completion_tok_per_s") else ""
        at = f"+{e['t_offset_s']:>6.1f}s " if "t_offset_s" in e else ""
        print(f"  {e['seq']:03d} {at}{marker}{'  ' * e['depth']}{e['step']}{_hint(e)}  ({e['duration_s']}s{tokens})" + (f"  !! {err}" if err else ""))
    print("\ncalls per step:")
    for step, n in counts.most_common(8):
        print(f"  {n:3d}  {step}")


def show_full(trace_dir, n):
    for e in traces(trace_dir):
        if e["seq"] == n:
            print(json.dumps(e, indent=2, ensure_ascii=False))
            return
    sys.exit(f"No traced step {n}")


def compare(a_arg, b_arg):
    runs = []
    for arg in (a_arg, b_arg):
        folder, _ = resolve(arg)
        if not folder:
            sys.exit("--compare needs two recorded runs")
        runs.append((folder, _load(os.path.join(folder, "run.json")), _load(os.path.join(folder, "summary.json"))))
    (fa, ma, sa), (fb, mb, sb) = runs
    print(f"A {ma['id']}\nB {mb['id']}\n")
    print(f"verdict   {sa['status']} -> {sb['status']}")
    print(f"code      {str(ma['git'].get('commit'))[:9]}{'*' if ma['git'].get('dirty') else ''} -> "
          f"{str(mb['git'].get('commit'))[:9]}{'*' if mb['git'].get('dirty') else ''}"
          + ("   (same commit)" if ma["git"].get("commit") == mb["git"].get("commit") and not (ma["git"].get("dirty") or mb["git"].get("dirty")) else ""))
    print(f"model     {ma['llm']['model']} -> {mb['llm']['model']}")
    print(f"duration  {sa['duration_s']}s -> {sb['duration_s']}s")
    print(f"LLM       {sa['llm']['calls']} calls / {sa['llm']['prompt_tokens'] + sa['llm']['completion_tokens']} tok -> "
          f"{sb['llm']['calls']} calls / {sb['llm']['prompt_tokens'] + sb['llm']['completion_tokens']} tok")
    inv_a, inv_b = ((s.get("result") or {}).get("app_inventory") for s in (sa, sb))
    if inv_a or inv_b:
        shown = [f"{i['reachable_lines']} reached + {i['unreachable_lines']} unreachable lines" if i else "(not recorded)"
                 for i in (inv_a, inv_b)]
        print(f"frontend  {shown[0]} -> {shown[1]}")
    sta = {s["name"]: s for s in sa["stages"]}
    stb = {s["name"]: s for s in sb["stages"]}
    print("\nSTAGES")
    for name in list(dict.fromkeys([*sta, *stb])):
        x, y = sta.get(name), stb.get(name)
        line = f"  {name:<22} {x['status'] if x else '-':8} -> {y['status'] if y else '-':8}"
        if x and y:
            line += f"  {x.get('duration_s', 0):.1f}s -> {y.get('duration_s', 0):.1f}s"
        print(line + ("   <-- changed" if (x or {}).get("status") != (y or {}).get("status") else ""))
        if y and y.get("error") and (not x or x.get("error") != y.get("error")):
            print(f"          B why: {str(y['error'])[:300]}")
    files_a, files_b = set(sa["provenance"]), set(sb["provenance"])
    print("\nFILES WRITTEN BY STAGES")
    for path in sorted(files_a | files_b):
        pa, pb = sa["provenance"].get(path), sb["provenance"].get(path)
        if pa != pb:
            print(f"  {path}: {pa or '(not written)'} -> {pb or '(not written)'}")
    print(f"\nDiff the generated apps with:  diff -r \"{os.path.join(fa, 'workspace')}\" \"{os.path.join(fb, 'workspace')}\"")


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        sys.exit(__doc__)
    if "--list" in args:
        return list_runs()
    if "--compare" in args:
        rest = [a for a in args if a != "--compare"]
        if len(rest) != 2:
            sys.exit("usage: trace_report.py --compare A B")
        return compare(*rest)
    full = None
    if "--full" in args:
        i = args.index("--full")
        full = int(args[i + 1])
        args = args[:i] + args[i + 2:]
    folder, trace_dir = resolve(args[0] if args else None)
    if full is not None:
        return show_full(trace_dir, full)
    if folder:
        return show_run(folder, trace_dir)
    show_trace(traces(trace_dir))  # a bare trace folder (PROVABLE_TRACE_DIR)


if __name__ == "__main__":
    main()
