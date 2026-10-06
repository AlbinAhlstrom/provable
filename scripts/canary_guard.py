#!/usr/bin/env python3
"""
Canary Guard: Automated Antigravity Lifecycle Hook for Context Integrity.
Fires on the 'Stop' event (when terminationReason == "model_stop").

Enforces that every assistant response ends with or contains the Canary:
    [🛡️ Clanker Active]

Features:
- Stateless 1-retry loop breaker: inspects transcript for prior retry injections
- Non-blocking on tool steps, system stops, or non-model terminations
- Zero external dependencies (standard library only)
"""

import sys
import json
import os
from pathlib import Path

CANARY_TAG = "[🛡️ Clanker Active]"
WARNING_SIGNATURE = "CRITICAL CANARY MISSING"


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "allow"}))
            return

        payload = json.loads(raw_input)
    except Exception:
        # Fail open on input parse error to avoid breaking toolchain
        print(json.dumps({"decision": "allow"}))
        return

    termination_reason = payload.get("terminationReason", "")
    # Only enforce canary when model deliberately attempts to stop and yield to user
    if termination_reason != "model_stop":
        print(json.dumps({"decision": "allow"}))
        return

    transcript_path = payload.get("transcriptPath")
    if not transcript_path or not os.path.exists(transcript_path):
        print(json.dumps({"decision": "allow"}))
        return

    try:
        steps = []
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        steps.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if not steps:
            print(json.dumps({"decision": "allow"}))
            return

        # Find the latest model response with textual content
        last_model_content = ""
        last_model_idx = -1
        for idx in range(len(steps) - 1, -1, -1):
            step = steps[idx]
            if step.get("source") == "MODEL" and step.get("content"):
                last_model_content = step.get("content", "")
                last_model_idx = idx
                break

        # If no model content exists (e.g. purely tool calls), allow stop
        if not last_model_content:
            print(json.dumps({"decision": "allow"}))
            return

        # Check if the canary tag is present in the response
        if CANARY_TAG in last_model_content:
            print(json.dumps({"decision": "allow"}))
            return

        # Canary is missing: check for 1-retry loop protection
        # Look backwards from last_model_idx for prior canary warning in the recent trajectory
        prior_retry_detected = False
        for idx in range(last_model_idx - 1, max(-1, last_model_idx - 10), -1):
            step = steps[idx]
            content = step.get("content", "")
            # If we hit the user's explicit prompt, stop scanning
            if step.get("source") == "USER_EXPLICIT" or step.get("type") == "USER_INPUT":
                break
            if WARNING_SIGNATURE in content:
                prior_retry_detected = True
                break

        if prior_retry_detected:
            # 1 retry already failed; allow stop to prevent infinite loop / freezing
            print(json.dumps({"decision": "allow"}))
            return

        # First failure: force continuation with warning
        response = {
            "decision": "continue",
            "reason": (
                f"{WARNING_SIGNATURE}: You failed to append '{CANARY_TAG}' "
                f"at the end of your response. Protocol violation. "
                f"Append '{CANARY_TAG}' to conclude your turn."
            )
        }
        print(json.dumps(response))

    except Exception:
        # Fallback to allow stop on unexpected script error
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
