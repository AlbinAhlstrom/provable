"""
What one run is asked to do differently from the settings: the options of a kickstart request, held for the run.

- `strict`: no second attempt anywhere. Each step answers once and what it answered stands: a test the RED gate
  refuses is not written again, a class's code is not asked again, a test no code could meet is not reconsidered,
  the plan is not reworked, the page is not written again (for changed classes, a failed build or QA's defects), a
  page test is written once, and the visual review's refused repairs go back to no one. A failure then shows at the
  step that made it, at its first occurrence, and the run takes no time on repairs. What a second attempt would
  have rescued is the measure of that step (the struggle corpus, `scripts/struggle_corpus.py`).
- `model`: every stage on this one model, whatever the provider or the settings give each stage (a baseline: the
  same pipe on a stronger model shows which steps fail for the model and which for the pipe).

Held like a replay (`llm_replay.py`): the kickstart and the rule tests after it run inside `running_with`, one run
at a time, and `run.json` records them (`run_recorder.py`).
"""
import contextlib
import threading
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterator, Optional


@dataclass(frozen=True)
class RunOptions:
    strict: bool = False
    model: Optional[str] = None


_lock = threading.Lock()
_current = RunOptions()


def current() -> RunOptions:
    with _lock:
        return _current


def strict() -> bool:
    return current().strict


def attempts(allowed: int) -> int:
    """How many attempts a step makes that is otherwise allowed `allowed`: one in a strict run."""
    return 1 if strict() else allowed


def recorded() -> Dict[str, Any]:
    return asdict(current())


@contextlib.contextmanager
def running_with(options: RunOptions) -> Iterator[None]:
    """Holds `options` for the block, and what held before after it."""
    global _current
    with _lock:
        before, _current = _current, options
    try:
        yield
    finally:
        with _lock:
            _current = before
