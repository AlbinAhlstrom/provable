"""Opt-in I/O tracing for the generation pipeline.

Set PROVABLE_TRACE_DIR=<dir> and every traced step (and every LLM call) writes one JSON file
`<seq>_<step>.json` with its input, output, duration, nesting depth and the chain of traced
callers. Files are numbered in call-start order, so sorting them reproduces the pipeline's
execution tree. When the variable is unset the decorators are pass-through.

API keys found in the environment are scrubbed from everything that is written.
"""

import dataclasses
import functools
import json
import os
import re
import threading
import time
from typing import Any, Callable

_lock = threading.Lock()
_seq = 0
_local = threading.local()

_SECRET_ENV_NAMES = ("LLM_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")


def trace_dir() -> str:
    return os.environ.get("PROVABLE_TRACE_DIR", "")


def _next_seq() -> int:
    global _seq
    with _lock:
        _seq += 1
        return _seq


def _stack() -> list:
    if not hasattr(_local, "stack"):
        _local.stack = []
    return _local.stack


def _jsonable(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    for attr in ("model_dump", "to_dict", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    return repr(obj)


def _scrub(text: str) -> str:
    for name in _SECRET_ENV_NAMES:
        secret = os.environ.get(name)
        if secret and len(secret) > 8:
            text = text.replace(secret, "[REDACTED]")
    return text


def _write(seq: int, name: str, payload: dict) -> None:
    directory = trace_dir()
    os.makedirs(directory, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name)
    body = _scrub(json.dumps(payload, indent=2, default=_jsonable, ensure_ascii=False))
    with open(os.path.join(directory, f"{seq:03d}_{safe}.json"), "w", encoding="utf-8") as f:
        f.write(body)


def _run(name: str, kind: str, fn: Callable, args: tuple, kwargs: dict, input_payload: Any) -> Any:
    seq = _next_seq()
    stack = _stack()
    entry = {"seq": seq, "step": name, "kind": kind, "depth": len(stack), "caller_chain": [s for s in stack],
             "started_at": time.strftime("%H:%M:%S"), "input": input_payload}
    stack.append(name)
    start = time.time()
    try:
        result = fn(*args, **kwargs)
        entry["output"] = result
        return result
    except BaseException as exc:
        entry["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        stack.pop()
        entry["duration_s"] = round(time.time() - start, 3)
        try:
            _write(seq, name, entry)
        except Exception as write_err:  # tracing must never break the pipeline
            print(f"[trace] could not write {name}: {write_err}")


def traced(name: str) -> Callable:
    """Trace a deterministic pipeline step: records its arguments and return value."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not trace_dir():
                return fn(*args, **kwargs)
            return _run(name, "step", fn, args, kwargs, {"args": list(args), "kwargs": kwargs})
        return wrapper
    return decorator


def traced_llm(fn: Callable) -> Callable:
    """Trace an LLM call `fn(prompt, stage=...)`: records the stage, full prompt and raw response."""
    @functools.wraps(fn)
    def wrapper(prompt: str, stage: str = "general", *args, **kwargs):
        if not trace_dir():
            return fn(prompt, stage=stage, *args, **kwargs)
        return _run(f"llm.{stage}", "llm", lambda: fn(prompt, stage=stage, *args, **kwargs), (), {},
                    {"stage": stage, "prompt": prompt})
    return wrapper
