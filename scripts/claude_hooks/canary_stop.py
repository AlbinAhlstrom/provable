#!/usr/bin/env python3
"""
Stop hook: context-integrity canary.

Every response must end with the canary tag. If the last assistant message of
the turn lacks it, the stop is blocked once and the model is told to append it.
Port of scripts/canary_guard.py (Antigravity lifecycle hook) to the Claude Code
Stop-hook protocol:
  stdin : {"transcript_path": "...", "stop_hook_active": bool, ...}
  stdout: {"decision": "block", "reason": "..."} to force one more step

Loop breaker: Claude Code sets `stop_hook_active` when it is already continuing
because of a Stop hook, in which case we always allow the stop.
Standard library only. Fails open (never traps a session).
"""
import json
import os
import sys

CANARY_TAG = "[\U0001F6E1️ Clanker Active]"


def _text_of(entry: dict) -> str:
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


def _is_real_user_prompt(entry: dict) -> bool:
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    return any(isinstance(b, dict) and b.get("type") == "text" for b in content or [])


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        return
    payload = json.loads(raw)

    if payload.get("stop_hook_active"):
        return

    path = payload.get("transcript_path")
    if not path or not os.path.exists(path):
        return

    entries = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    last_text = ""
    for entry in reversed(entries):
        if entry.get("isSidechain"):
            continue
        kind = entry.get("type")
        if kind == "assistant":
            text = _text_of(entry)
            if text.strip():
                last_text = text
                break
        elif kind == "user" and _is_real_user_prompt(entry):
            break  # reached the prompt that started this turn: no assistant text yet

    if not last_text or CANARY_TAG in last_text:
        return

    print(json.dumps({
        "decision": "block",
        "reason": (
            f"CRITICAL CANARY MISSING: append the exact tag '{CANARY_TAG}' "
            "at the very end of your response to conclude the turn."
        ),
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open
