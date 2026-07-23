#!/usr/bin/env python3
"""
reset_ticket.py — Reset a specific requirement status back to 'Backlog'.
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ_FILE = os.path.join(ROOT, "src", "requirements.json")

target_id = sys.argv[1] if len(sys.argv) > 1 else "REQ-756"

if os.path.exists(REQ_FILE):
    with open(REQ_FILE, "r", encoding="utf-8") as f:
        reqs = json.load(f)

    updated = False
    for req in reqs:
        if req["id"] == target_id:
            req["status"] = "Backlog"
            updated = True
            print(f"Reset {target_id} status to Backlog.")

    if updated:
        with open(REQ_FILE, "w", encoding="utf-8") as f:
            json.dump(reqs, f, indent=2)
    else:
        print(f"Requirement {target_id} not found.")
else:
    print(f"Requirements file not found at {REQ_FILE}")
