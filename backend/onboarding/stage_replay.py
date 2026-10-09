"""Stage replay: send a recorded LLM call to another model and score its answer against the recorded one.

A recorded run (`run_recorder.py`) keeps every LLM call's stage, full prompt, options and answer. Replaying one call
on a cheaper model, with the exact input the expensive model saw, isolates what that single stage loses when the
model is swapped: nothing upstream differs, so any difference in the answer comes from the model.

Scores are objective and generic: is the answer well-formed in the way the recorded one was (JSON that parses, every
file marker present), and how much of its content agrees with the recorded answer. They say how close a cheap answer
is to the expensive one, not whether either is right: the gates of the pipeline (tests, build, QA) judge that.
Nothing is retried or repaired here: a provider error is reported as the run's error, with no answer.
"""

import glob
import json
import os
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

_MARKER = re.compile(r"^<<<(\w+)>>>\s*$", re.MULTILINE)


@dataclass
class RecordedCall:
    seq: int
    stage: str
    prompt: str
    options: Dict[str, Any]
    output: str
    model: Optional[str]
    duration_s: float
    completion_tokens: Optional[int]


@dataclass
class Run:
    output: str
    duration_s: float
    completion_tokens: Optional[int]
    error: Optional[str]


@dataclass
class Score:
    valid: bool
    agreement: float


@dataclass
class StageSummary:
    stage: str
    model: str
    samples: int
    valid_rate: float
    mean_agreement: float
    mean_duration_s: float
    speedup: float
    errors: List[str] = field(default_factory=list)


def load_llm_calls(trace_dir: str) -> List[RecordedCall]:
    """The LLM calls of a trace folder, in the order they were made."""
    calls = []
    for path in sorted(glob.glob(os.path.join(trace_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            entry = json.load(f)
        if entry.get("kind") != "llm" or not isinstance(entry.get("input"), dict):
            continue
        meta = entry.get("meta") or {}
        calls.append(RecordedCall(
            seq=entry.get("seq", 0), stage=entry["input"].get("stage", "general"),
            prompt=entry["input"].get("prompt", ""), options=dict(entry["input"].get("options") or {}),
            output=entry.get("output") if isinstance(entry.get("output"), str) else "",
            model=meta.get("model"), duration_s=float(entry.get("duration_s") or 0.0),
            completion_tokens=meta.get("completion_tokens")))
    return sorted(calls, key=lambda c: c.seq)


@contextmanager
def _model_for(stage: str, model: str):
    name = f"LLM_MODEL_{stage.upper()}"
    before = os.environ.get(name)
    os.environ[name] = model
    try:
        yield
    finally:
        if before is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = before


def replay(call: RecordedCall, model: str, samples: int = 1, llm: Optional[Callable[..., str]] = None,
           error_of: Optional[Callable[[], Optional[str]]] = None) -> List[Run]:
    """Sends the recorded prompt and options to `model` `samples` times. `llm` and `error_of` default to the
    pipeline's own LLM wrapper and its last-error reader."""
    if llm is None:
        import agent_orchestrator
        llm = agent_orchestrator.call_gemini
        error_of = error_of or (lambda: agent_orchestrator.LAST_LLM_ERROR)
    runs = []
    for _ in range(samples):
        started = time.time()
        with _model_for(call.stage, model):
            output = llm(call.prompt, stage=call.stage, **call.options)
        elapsed = round(time.time() - started, 3)
        error = None if output else ((error_of() if error_of else None) or "empty answer")
        runs.append(Run(output or "", elapsed, _tokens_of_last_call(), error))
    return runs


def _tokens_of_last_call() -> Optional[int]:
    import pipeline_trace
    meta = getattr(pipeline_trace._local, "llm_meta", None) or {}
    tokens = meta.get("completion_tokens")
    return tokens if isinstance(tokens, int) else None


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text.strip())
    except (ValueError, TypeError):
        return _NOT_JSON


_NOT_JSON = object()


def _leaves(node: Any, path: str = "") -> Dict[str, Any]:
    if isinstance(node, dict):
        out: Dict[str, Any] = {}
        for key, value in node.items():
            out.update(_leaves(value, f"{path}.{key}"))
        return out
    if isinstance(node, list):
        out = {}
        for i, value in enumerate(node):
            out.update(_leaves(value, f"{path}[{i}]"))
        return out
    return {path: node}


def _words(text: str) -> set:
    return set(re.findall(r"\w+", text.lower()))


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


def score(reference: str, answer: str) -> Score:
    """How well-formed `answer` is by the reference's own form, and how much of it agrees with the reference."""
    if not (answer or "").strip():
        return Score(False, 0.0)
    ref_json = _parse_json(reference)
    if ref_json is not _NOT_JSON:
        got = _parse_json(answer)
        if got is _NOT_JSON:
            return Score(False, 0.0)
        ref_leaves, got_leaves = _leaves(ref_json), _leaves(got)
        union = set(ref_leaves) | set(got_leaves)
        same = sum(1 for k in union if k in ref_leaves and k in got_leaves and ref_leaves[k] == got_leaves[k])
        return Score(True, same / len(union) if union else 1.0)
    markers = set(_MARKER.findall(reference))
    if markers and not markers <= set(_MARKER.findall(answer)):
        return Score(False, _jaccard(_words(reference), _words(answer)))
    return Score(True, _jaccard(_words(reference), _words(answer)))


def summarise(call: RecordedCall, model: str, runs: List[Run]) -> StageSummary:
    scored = [(r, score(call.output, r.output) if not r.error else Score(False, 0.0)) for r in runs]
    valid = [s for _, s in scored if s.valid]
    mean_duration = sum(r.duration_s for r in runs) / len(runs) if runs else 0.0
    return StageSummary(
        stage=call.stage, model=model, samples=len(runs),
        valid_rate=len(valid) / len(runs) if runs else 0.0,
        mean_agreement=sum(s.agreement for s in valid) / len(valid) if valid else 0.0,
        mean_duration_s=mean_duration,
        speedup=call.duration_s / mean_duration if mean_duration else 0.0,
        errors=sorted({r.error for r in runs if r.error}))
