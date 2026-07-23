#!/usr/bin/env python3
"""
update_json.py — Capture git diff for a ticket branch and update its requirement status to 'Review'.
"""

import os
import sys
import json
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(ROOT, "workspace")
REQ_FILE = os.path.join(ROOT, "src", "requirements.json")

target_id = sys.argv[1] if len(sys.argv) > 1 else "REQ-756"
ticket_branch = f"ticket/{target_id}"

try:
    diff_res = subprocess.run(
        ["git", "diff", "main", ticket_branch],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True
    )
    diff = diff_res.stdout
except Exception as e:
    print(f"Error fetching git diff: {e}")
    diff = ""

if os.path.exists(REQ_FILE):
    with open(REQ_FILE, "r", encoding="utf-8") as f:
        reqs = json.load(f)

    updated = False
    for req in reqs:
        if req["id"] == target_id:
            req["status"] = "Review"
            req["proposedCode"] = diff
            updated = True
            print(f"Updated {target_id} status to Review with proposed diff ({len(diff)} bytes).")

    if updated:
        with open(REQ_FILE, "w", encoding="utf-8") as f:
            json.dump(reqs, f, indent=2)
else:
    print(f"Requirements file not found at {REQ_FILE}")
