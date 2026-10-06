"""
Unit test suite for scripts/canary_guard.py Antigravity hook.
Verifies:
1. Allow on non-model_stop termination
2. Allow when canary tag is present
3. Reject (decision: continue) when canary is missing on first failure
4. 1-retry loop protection: allow when retry was already attempted
"""

import subprocess
import sys
import json
import os
import pytest


def run_canary_guard(payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, "scripts/canary_guard.py"],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=os.getcwd()
    )
    assert proc.returncode == 0, f"canary_guard failed with stderr: {proc.stderr}"
    return json.loads(proc.stdout.strip())


def test_canary_guard_allows_non_model_stop(tmp_path):
    result = run_canary_guard({
        "terminationReason": "max_steps_exceeded",
        "transcriptPath": str(tmp_path / "transcript.jsonl")
    })
    assert result == {"decision": "allow"}


def test_canary_guard_allows_when_canary_present(tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({
            "step_index": 1,
            "source": "MODEL",
            "type": "PLANNER_RESPONSE",
            "content": "Here is the response. [🛡️ Clanker Active]"
        }) + "\n",
        encoding="utf-8"
    )

    result = run_canary_guard({
        "terminationReason": "model_stop",
        "transcriptPath": str(transcript)
    })
    assert result == {"decision": "allow"}


def test_canary_guard_triggers_continue_on_missing_canary(tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps({
            "step_index": 1,
            "source": "MODEL",
            "type": "PLANNER_RESPONSE",
            "content": "Here is the response without the tag."
        }) + "\n",
        encoding="utf-8"
    )

    result = run_canary_guard({
        "terminationReason": "model_stop",
        "transcriptPath": str(transcript)
    })
    assert result.get("decision") == "continue"
    assert "CRITICAL CANARY MISSING" in result.get("reason", "")


def test_canary_guard_one_retry_loop_breaker(tmp_path):
    transcript = tmp_path / "transcript.jsonl"
    lines = [
        json.dumps({"step_index": 0, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "hello"}),
        json.dumps({"step_index": 1, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "bad response 1"}),
        json.dumps({"step_index": 2, "source": "SYSTEM", "type": "SYSTEM_MESSAGE", "content": "CRITICAL CANARY MISSING: You failed..."}),
        json.dumps({"step_index": 3, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "bad response 2 still without tag"})
    ]
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = run_canary_guard({
        "terminationReason": "model_stop",
        "transcriptPath": str(transcript)
    })
    # Loop breaker triggers: should allow stop instead of looping
    assert result == {"decision": "allow"}
