#!/usr/bin/env python3
"""Replay one recorded run's LLM calls on other models, stage by stage, and compare with what the recorded model wrote.

Usage:
    python scripts/stage_replay.py <run> --models gpt-x-mini,gpt-x-nano [--samples 3] [--stages ux_planning,...]

<run> is a run id or folder under logs/runs/ (default: the latest). Each recorded LLM call is sent again with its exact
prompt and options to each model; the table shows, per stage and model, how often the answer was well-formed, how much of
it agrees with the recorded answer, and how much faster it was. Results are also written to logs/replays/<run>.json.
Needs an LLM key and network access to the provider; every call costs money.
"""
import argparse
import dataclasses
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from onboarding import stage_replay as sr  # noqa: E402
import trace_report  # noqa: E402  (scripts/ is on sys.path when run as a script)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", nargs="?")
    parser.add_argument("--models", required=True)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--stages", default="")
    args = parser.parse_args()

    folder, trace_dir = trace_report.resolve(args.run)
    wanted = {s for s in args.stages.split(",") if s}
    calls = [c for c in sr.load_llm_calls(trace_dir) if c.output and (not wanted or c.stage in wanted)]
    models = [m for m in args.models.split(",") if m]
    rows = []
    print(f"{'stage':32} {'model':22} {'valid':>6} {'agree':>6} {'secs':>6} {'speedup':>8}")
    for call in calls:
        for model in models:
            summary = sr.summarise(call, model, sr.replay(call, model, args.samples))
            rows.append({"seq": call.seq, "recorded_model": call.model, "recorded_duration_s": call.duration_s,
                         **dataclasses.asdict(summary)})
            print(f"{call.stage[:32]:32} {model[:22]:22} {summary.valid_rate:6.0%} {summary.mean_agreement:6.2f} "
                  f"{summary.mean_duration_s:6.1f} {summary.speedup:7.1f}x"
                  + (f"  ERR {summary.errors[0][:80]}" if summary.errors else ""), flush=True)
    out_dir = os.path.join(ROOT, "logs", "replays")
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.basename((folder or trace_dir).rstrip("/\\"))
    with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


if __name__ == "__main__":
    main()
