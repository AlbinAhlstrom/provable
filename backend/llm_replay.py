"""
Replay: a run that names recorded runs is answered from them wherever it asks exactly what they asked.

Working on one stage used to cost a whole kickstart each time: every other stage asked the model again what it had
already answered, for the same pitch, word for word. The run recorder keeps every question and its answer
(`logs/runs/<id>/trace/`), so a run can be pointed at them instead: `replaying([...])`, which a kickstart request
asks for with `replay` (`entrypoints/routers/onboarding.py`).

- A question is the same when everything the model would see is: the stage, the prompt, the answer's schema or JSON
  mode, the model and the effort. Change one stage's prompt and that call goes to the model; a stage after it whose
  input changed with it does too, so nothing stale comes back.
- A question asked more than once gets its answers in the order they were given; once they are used up, the model
  answers.
- Never replayed: a question with screenshots (the trace keeps their paths, not the pictures) and a call that failed
  (it holds no answer).
- A replayed call is in the trace like any other, marked with the run it came from and at no cost
  (`run_recorder.llm_totals` counts them), so a replayed run can be replayed in turn.

- A stage named live (`replaying(runs, live=[...])`) is always asked of the model, while the rest is replayed: the
  stage is sampled again on the same recorded input, so the variance that is its own shows apart from what came
  before it.

Replay answers what one run of the model said. It says nothing about how often a stage answers well: measure that
with live calls.
"""

import contextlib
import hashlib
import json
import os
import threading
from typing import Any, Dict, Iterator, List, Optional, Sequence

_lock = threading.Lock()
_active: List[str] = []
_live: List[str] = []   # stages asked of the model though recorded
_answers: Dict[str, List[str]] = {}   # question key -> recorded answers not yet given, in the order they were given


def key(stage: str, prompt: str, json_mode: bool, json_schema: Optional[Dict[str, Any]], model: str,
        effort: Optional[str]) -> str:
    question = {"stage": stage, "prompt": prompt, "json_mode": bool(json_mode), "json_schema": json_schema,
                "model": model, "effort": effort or None}
    return hashlib.sha256(json.dumps(question, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _load(run_id: str) -> Dict[str, List[str]]:
    """The answered questions of one recorded run, by key, in the order they were asked."""
    import run_recorder
    trace = os.path.join(run_recorder.runs_root(), run_id, "trace")
    if not os.path.isdir(trace):
        raise ValueError(f"there is no recorded run to replay named {run_id} (looked in {trace})")
    found: Dict[str, List[str]] = {}
    for name in sorted(os.listdir(trace)):
        with open(os.path.join(trace, name), encoding="utf-8") as f:
            entry = json.load(f)
        asked, meta, answer = entry.get("input") or {}, entry.get("meta") or {}, entry.get("output")
        options = asked.get("options") or {}
        if entry.get("kind") != "llm" or entry.get("error") or meta.get("error") or options.get("images"):
            continue
        if not isinstance(answer, str) or not answer.strip() or not meta.get("model"):
            continue
        found.setdefault(key(str(asked.get("stage")), str(asked.get("prompt")), bool(options.get("json_mode")),
                             options.get("json_schema"), meta["model"], meta.get("reasoning_effort")), []).append(answer)
    return found


def active() -> List[str]:
    """The runs being replayed."""
    return list(_active)


def live() -> List[str]:
    """The stages asked of the model while the rest is replayed."""
    return list(_live)


@contextlib.contextmanager
def replaying(run_ids: Optional[Sequence[str]], live: Optional[Sequence[str]] = None) -> Iterator[None]:
    """Answers the questions inside the block from `run_ids` (none: nothing is replayed), except those of the `live`
    stages. Raises ValueError, before anything is asked, when a run is not recorded."""
    global _active, _answers, _live
    run_ids = [run_id for run_id in (run_ids or []) if run_id]
    if not run_ids:
        yield
        return
    loaded: Dict[str, List[str]] = {}
    for run_id in run_ids:
        for question, answers in _load(run_id).items():
            loaded.setdefault(question, []).extend(answers)
    with _lock:
        before = (_active, _answers, _live)
        _active, _answers, _live = list(run_ids), loaded, list(live or [])
    try:
        yield
    finally:
        with _lock:
            _active, _answers, _live = before


def answer(stage: str, prompt: str, json_mode: bool, json_schema: Optional[Dict[str, Any]],
           images: Optional[List[str]], model: str, effort: Optional[str]) -> Optional[str]:
    """The recorded answer to this question, or None when the model is to be asked."""
    if images or not _active or stage in _live:
        return None
    with _lock:
        recorded = _answers.get(key(stage, prompt, json_mode, json_schema, model, effort))
        return recorded.pop(0) if recorded else None
