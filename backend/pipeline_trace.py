"""Opt-in I/O tracing for the generation pipeline.

A recorded run (run_recorder.py) points the tracer at its own folder automatically. Otherwise, set
PROVABLE_TRACE_DIR=<dir> and every traced step (and every LLM call) writes one JSON file
`<seq>_<step>.json` with its input, output, duration, nesting depth and the chain of traced
callers. Files are numbered in call-start order, so sorting them reproduces the pipeline's
execution tree. With neither a recorded run nor the variable the decorators are pass-through. An LLM call's `meta` (model, token
counts, finish reason, error) is recorded through record_llm_meta; the tracer adds the prompt and response sizes and the
completion tokens per second.

Every entry holds `t_offset_s` (seconds since the trace began) and its thread, so steps that ran at the same time can be
laid out on one timeline. The caller chain is per thread: hand work to a thread pool through bind_context(fn) and the
worker's steps stay attached to the step that started them.

API keys, the engine's and the held user's (llm_credentials.py), are scrubbed from everything that is written.
"""

import dataclasses
import functools
import json
import os
import re
import threading
import time
from typing import Any, Callable

import llm_credentials

_lock = threading.Lock()
_seq = 0
_local = threading.local()

_active_dir = ""  # set by run_recorder for the duration of a recorded run
_epoch = time.time()  # what t_offset_s counts from; restarted with every recorded run


def trace_dir() -> str:
    return _active_dir or os.environ.get("PROVABLE_TRACE_DIR", "")


def set_trace_dir(directory: str) -> None:
    """Direct the trace into `directory` (a recorded run's folder) and restart the numbering; "" switches it off."""
    global _active_dir, _seq, _epoch
    with _lock:
        _active_dir = directory
        _seq = 0
        _epoch = time.time()


def bind_context(fn: Callable) -> Callable:
    """`fn`, to be run in another thread under the calling thread's chain of traced steps."""
    chain = list(_stack())

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        _local.stack = list(chain)
        try:
            return fn(*args, **kwargs)
        finally:
            _local.stack = []  # pool threads are reused
    return wrapper


def record_llm_meta(**fields: Any) -> None:
    """Called by the LLM wrapper for the call in flight on this thread: model, tokens, finish reason, error."""
    _local.llm_meta = fields


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
    for secret in llm_credentials.secret_values():
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
    start = time.time()
    entry = {"seq": seq, "step": name, "kind": kind, "depth": len(stack), "caller_chain": [s for s in stack],
             "started_at": time.strftime("%H:%M:%S"), "t_offset_s": round(start - _epoch, 3),
             "thread": threading.current_thread().name, "input": input_payload}
    stack.append(name)
    _local.llm_meta = None
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
        if kind == "llm" and getattr(_local, "llm_meta", None):
            entry["meta"] = _llm_meta(_local.llm_meta, input_payload, entry.get("output"), entry["duration_s"])
        try:
            _write(seq, name, entry)
        except Exception as write_err:  # tracing must never break the pipeline
            print(f"[trace] could not write {name}: {write_err}")


def _llm_meta(reported: dict, input_payload: Any, output: Any, duration_s: float) -> dict:
    """What the wrapper reported plus what only the tracer sees: sizes in characters and the output speed."""
    meta = dict(reported)
    meta["prompt_chars"] = len(input_payload.get("prompt") or "") if isinstance(input_payload, dict) else None
    meta["response_chars"] = len(output) if isinstance(output, str) else None
    tokens = meta.get("completion_tokens")
    if isinstance(tokens, int) and duration_s > 0:
        meta["completion_tok_per_s"] = round(tokens / duration_s, 1)
    return meta


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
                    {"stage": stage, "prompt": prompt, "options": kwargs})
    return wrapper
