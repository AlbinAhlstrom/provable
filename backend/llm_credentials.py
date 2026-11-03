"""Whose key the LLM calls spend, and which secrets the engine keeps from the code it runs.

A hosted engine (CLERK_ISSUER set) spends the signed-in user's own key. Held like run_options.py and llm_replay.py, one
holder for the whole process, because a run's calls come from pool threads that a context variable would not reach. So
the holder is exclusive: while one user's work runs, another user's writing request is refused (EngineBusy) rather than
let it replace the key under that run. `entrypoints/llm_lease.py` holds a request's key, background work included.

A local engine (no CLERK_ISSUER) has no holder: the settings decide, as they always did.

seal_environment moves the secrets out of os.environ, so that no subprocess inherits them: generated code runs on the
same machine as the engine, written from a pitch anyone signed in may send.
"""

import contextlib
import os
import sys
import threading
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional

KEY_SECRET_SETTING = "PROVABLE_KEY_SECRET"  # encrypts the users' keys at rest (adapters/llm_key_store.py)
SECRET_SETTINGS = ("LLM_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "CLAUDE_API_KEY", KEY_SECRET_SETTING)


class EngineBusy(Exception):
    """Another user's work holds the engine."""


@dataclass(frozen=True)
class Credential:
    user_id: str
    provider: str = ""
    api_key: str = ""
    house: bool = False  # runs on the operator's settings (LLM_HOUSE_USERS)


_lock = threading.Lock()
_held: Optional[Credential] = None
_holds = 0
_sealed: Dict[str, str] = {}


def enforced() -> bool:
    """True on a hosted engine, where every user brings their own key."""
    return bool(os.environ.get("CLERK_ISSUER", "").strip())


def current() -> Optional[Credential]:
    with _lock:
        return _held


def acquire(credential: Credential) -> Credential:
    """Holds `credential` until as many releases follow; a request of the same user joins the hold already there."""
    global _held, _holds
    with _lock:
        if _held is not None and _held.user_id != credential.user_id:
            raise EngineBusy("Another build is running on this engine. Try again when it is done.")
        _held = _held or credential
        _holds += 1
        return _held


def release(credential: Credential) -> None:
    global _held, _holds
    with _lock:
        _holds -= 1
        if _holds <= 0:
            _held, _holds = None, 0


@contextlib.contextmanager
def holding(credential: Credential) -> Iterator[Credential]:
    held = acquire(credential)
    try:
        yield held
    finally:
        release(held)


def reset() -> None:
    global _held, _holds, _sealed
    with _lock:
        _held, _holds, _sealed = None, 0, {}


def setting(name: str) -> str:
    """A secret setting, wherever it is kept now."""
    return _sealed.get(name) or os.environ.get(name) or ""


def seal_environment() -> None:
    """On a hosted engine: takes the secrets out of what subprocesses inherit and bars them from reading this process."""
    if not enforced():
        return
    for name in SECRET_SETTINGS:
        value = os.environ.pop(name, None)
        if value:
            _sealed[name] = value
    if sys.platform == "linux":
        import ctypes
        PR_SET_DUMPABLE = 4
        if ctypes.CDLL(None, use_errno=True).prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), "could not bar other processes from reading the engine's memory")


def secret_values() -> List[str]:
    """Every secret a text written to disk must not contain."""
    held = current()
    values = [setting(name) for name in SECRET_SETTINGS] + [held.api_key if held else ""]
    return [value for value in values if len(value) > 8]
