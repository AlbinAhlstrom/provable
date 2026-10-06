#!/usr/bin/env python3
"""
backend/scripts/run_kickstart_live.py
CLI test harness for executing Provable's normal kickstart pipeline
with real-time unbuffered progress logging.
"""

import os
import sys
import time
import argparse

# Enforce immediate line buffering on stdout and stderr
os.environ["PYTHONUNBUFFERED"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass

# Add backend directory to sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services


def parse_args():
    parser = argparse.ArgumentParser(description="Run Provable live kickstart pipeline with unbuffered logs.")
    parser.add_argument(
        "--pitch",
        type=str,
        default="An interactive Tic-Tac-Toe game with winning condition checks, turn alternation, and score tracking.",
        help="Domain pitch text describing the application."
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=os.path.join(BACKEND_DIR, "..", "workspace_benchmarks", "test_live_kickstart"),
        help="Target workspace path."
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="full",
        choices=["full", "fast", "no_agent"],
        help="Kickstart execution mode."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-3.8-flash",
        help="Model ID for OpenCode autonomous refinement."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    os.environ["OPENCODE_MODEL"] = args.model
    workspace_dir = os.path.abspath(args.workspace)
    os.makedirs(workspace_dir, exist_ok=True)

    print(f"[{time.strftime('%H:%M:%S')}] 🚀 Live Kickstart Runner Started", flush=True)
    print(f"[{time.strftime('%H:%M:%S')}] Target Workspace: {workspace_dir}", flush=True)
    print(f"[{time.strftime('%H:%M:%S')}] Mode: {args.mode} | Model: {args.model}", flush=True)
    print(f"[{time.strftime('%H:%M:%S')}] Pitch: {args.pitch}", flush=True)

    uow = SqliteUnitOfWork()
    start_time = time.time()

    try:
        res = services.kickstart_domain_and_scaffold(
            pitch=args.pitch,
            uow=uow,
            workspace_dir=workspace_dir,
            mode=args.mode
        )
        elapsed = round(time.time() - start_time, 2)
        print(f"\n[{time.strftime('%H:%M:%S')}] ✅ Kickstart Execution Successful in {elapsed}s", flush=True)
        print(f"[{time.strftime('%H:%M:%S')}] Domain Name: {res.get('domain_name')}", flush=True)
        print(f"[{time.strftime('%H:%M:%S')}] Aggregates: {[a.get('name') for a in res.get('aggregates', [])]}", flush=True)
        print(f"[{time.strftime('%H:%M:%S')}] Created Files: {len(res.get('created_files', []))}", flush=True)
        for cf in res.get('created_files', [])[:10]:
            print(f"  • {cf}", flush=True)
        if len(res.get('created_files', [])) > 10:
            print(f"  ... and {len(res.get('created_files', [])) - 10} more files", flush=True)

    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        print(f"\n[{time.strftime('%H:%M:%S')}] ❌ Kickstart Execution Failed after {elapsed}s: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
