#!/usr/bin/env python3
"""Summarize a pipeline trace directory (see backend/pipeline_trace.py).

Usage:
    PROVABLE_TRACE_DIR=logs/trace  <start the backend as usual>, then use the app
    python scripts/trace_report.py logs/trace [--full N]

Prints one line per traced step in call order (indented by nesting) with duration and any
error, then per-step call counts. `--full N` prints the complete input/output of step N.
"""
import collections
import glob
import json
import os
import sys


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    directory = args[0]
    files = sorted(glob.glob(os.path.join(directory, "*.json")))
    entries = [json.load(open(f, encoding="utf-8")) for f in files]

    if "--full" in args:
        n = int(args[args.index("--full") + 1])
        for e in entries:
            if e["seq"] == n:
                print(json.dumps(e, indent=2, ensure_ascii=False))
        return

    counts = collections.Counter()
    for e in entries:
        counts[e["step"]] += 1
        marker = "LLM " if e["kind"] == "llm" else "    "
        err = f"  !! {e['error']}" if e.get("error") else ""
        print(f"{e['seq']:03d} {marker}{'  ' * e['depth']}{e['step']}  ({e['duration_s']}s){err}")
    print("\ncalls per step:")
    for step, n in counts.most_common():
        print(f"  {n:3d}  {step}")


if __name__ == "__main__":
    main()
