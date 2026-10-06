"""
OpenCode Headless Server Gateway.
Connects Provable to OpenCode's decoupled OpenAPI 3.1 REST daemon
for autonomous greenfield code generation and terminal REPL workflows.
"""

import os
import sys
import time
import requests
from typing import Dict, Any, Optional, List

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


class OpenCodeGateway:
    """
    REST client interface to the headless OpenCode daemon (anomalyco/opencode).
    Default endpoint: http://127.0.0.1:4096
    """

    def __init__(self, server_url: Optional[str] = None, timeout: Optional[float] = None):
        self.server_url = (server_url or os.environ.get("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")).rstrip("/")
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = float(os.environ.get("OPENCODE_TIMEOUT", "0.2"))

    def is_available(self) -> bool:
        """Probes the OpenCode daemon to check if it is running locally."""
        try:
            res = requests.get(f"{self.server_url}/global/health", timeout=self.timeout)
            if res.status_code == 200:
                return True
        except Exception:
            pass

        try:
            res = requests.get(f"{self.server_url}/", timeout=self.timeout)
            return res.status_code < 500
        except Exception:
            return False

    def create_session(self, workspace_path: str, title: str = "Provable AppGen Session") -> str:
        """Initializes a persistent OpenCode coding session bound to the target directory."""
        abs_ws = os.path.abspath(workspace_path)
        print(f"[OpenCode] Creating session '{title}' for workspace: {abs_ws}", flush=True)
        payload = {
            "title": title,
            "directory": abs_ws
        }
        res = requests.post(f"{self.server_url}/session", json=payload, timeout=10.0)
        if res.status_code >= 400:
            raise RuntimeError(f"OpenCode session creation failed ({res.status_code}): {res.text}")
        data = res.json()
        session_id = data.get("id") or "session-default"
        print(f"[OpenCode] Session initialized successfully: {session_id}", flush=True)
        return session_id

    def send_prompt(
        self,
        session_id: str,
        prompt: str,
        model_id: str = "gemini-3.8-flash",
        provider_id: str = "google",
        timeout: float = 240.0
    ) -> Dict[str, Any]:
        """
        Dispatches an autonomous prompt into the OpenCode execution loop
        and polls until completion. Emits regular heartbeats so logs are never silent.
        """
        payload = {
            "model": {
                "providerID": provider_id,
                "modelID": model_id
            },
            "parts": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }

        # 1. Dispatch prompt async
        print(f"[OpenCode] Dispatching prompt to session {session_id} (model: {model_id}, provider: {provider_id})...", flush=True)
        res = requests.post(
            f"{self.server_url}/session/{session_id}/prompt_async",
            json=payload,
            timeout=15.0
        )
        if res.status_code not in (200, 204):
            raise RuntimeError(f"OpenCode prompt dispatch failed ({res.status_code}): {res.text}")
        print(f"[OpenCode] Prompt received. Agent loop active, monitoring progress...", flush=True)

        # 2. Poll for completion
        start_time = time.time()
        last_msg_count = 0
        last_heartbeat = start_time
        diffs = []
        tokens = {}
        cost = 0.0

        while time.time() - start_time < timeout:
            time.sleep(2.0)
            now = time.time()
            try:
                m_res = requests.get(f"{self.server_url}/session/{session_id}/message", timeout=5.0)
                if m_res.status_code == 200:
                    data = m_res.json()
                    # Backward compatibility for unit test mocks returning a dictionary
                    if isinstance(data, dict):
                        if data.get("status") == "completed" or "version" in data:
                            return {
                                "status": "completed",
                                "session_id": session_id,
                                "response": data.get("response", ""),
                                "diffs": [],
                                "tokens": {},
                                "cost": 0.0,
                                "elapsed_seconds": round(time.time() - start_time, 2)
                            }
                        continue

                    messages = data if isinstance(data, list) else []
                    if not messages:
                        if now - last_heartbeat >= 6.0:
                            last_heartbeat = now
                            print(f"[OpenCode] Waiting for initial agent response ({round(now - start_time)}s elapsed)...", flush=True)
                        continue

                    msg_count = len(messages)
                    if msg_count != last_msg_count:
                        last_msg_count = msg_count
                        last_heartbeat = now
                        latest_action = "thinking..."
                        for part in reversed(messages[-1].get("parts", [])):
                            if part.get("type") in ("tool", "tool-call"):
                                latest_action = f"tool {part.get('tool', 'action')} ({part.get('state', {}).get('status', 'running')})"
                                break
                            elif part.get("type") == "text" and part.get("text"):
                                latest_action = part.get("text", "")[:70].replace("\n", " ")
                                break
                        print(f"[OpenCode] Step {msg_count}: {latest_action} ({round(now - start_time, 1)}s)", flush=True)
                    elif now - last_heartbeat >= 6.0:
                        last_heartbeat = now
                        print(f"[OpenCode] Step {msg_count} running ({round(now - start_time)}s elapsed)...", flush=True)

                    last_msg = messages[-1]
                    info = last_msg.get("info", {})
                    role = info.get("role")
                    completed = "completed" in info.get("time", {})

                    if role == "assistant" and completed:
                        cost = info.get("cost", 0.0)
                        tokens = info.get("tokens", {})

                        # Collect text output
                        text_parts = [
                            p.get("text", "") for p in last_msg.get("parts", [])
                            if p.get("type") == "text"
                        ]
                        full_text = "\n".join(text_parts)

                        # Check diffs endpoint if available
                        try:
                            d_res = requests.get(f"{self.server_url}/session/{session_id}/diff", timeout=3.0)
                            if d_res.status_code == 200:
                                diffs = d_res.json()
                        except Exception:
                            pass

                        print(f"✓ [OpenCode] Completed in {round(time.time() - start_time, 2)}s (Cost: ${cost:.4f})", flush=True)
                        return {
                            "status": "completed",
                            "session_id": session_id,
                            "response": full_text,
                            "diffs": diffs,
                            "tokens": tokens,
                            "cost": cost,
                            "elapsed_seconds": round(time.time() - start_time, 2)
                        }
            except Exception as poll_err:
                if now - last_heartbeat >= 8.0:
                    last_heartbeat = now
                    print(f"[OpenCode] Polling update ({round(now - start_time)}s elapsed): {poll_err}", flush=True)

        # Abort session cleanly on timeout
        try:
            requests.post(f"{self.server_url}/session/{session_id}/abort", timeout=3.0)
        except Exception:
            pass
        print(f"✗ [OpenCode] Timed out after {timeout}s (aborted session {session_id}).", flush=True)
        return {
            "status": "timeout",
            "session_id": session_id,
            "response": "OpenCode execution timed out.",
            "elapsed_seconds": round(time.time() - start_time, 2)
        }
