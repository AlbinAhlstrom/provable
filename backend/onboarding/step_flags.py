"""A step's flag: what looked wrong in what it was given.

A step does its task from what it is given, to the best of its ability. Whether its input was right is not its
decision, and it does not act on a doubt by doing another task (a code writer that held a frozen test to be wrong
once answered in words, and a class lost every rule with it). What it may do is say so, in one marked line per
doubt:

    # FLAG <what it is about>: <what looks wrong, and what the step went by instead>

The line is a comment in the answer, so the answer stays the step's ordinary output. `take` reads the lines out as
`Flag`s, records them (the run's summary lists every flag; the trace holds a `step.flags` entry where it was raised)
and returns the answer without them. What a flag leads to is decided by the code that called the step: the code
writer's flag on a test sends that test to its writer (service_layer/tdd_batch.py).
"""
import re
from dataclasses import asdict, dataclass
from typing import List, Tuple

import run_recorder
from pipeline_trace import traced

LINE = re.compile(r"^[ \t]*# FLAG[ \t]+([^\s:]+):[ \t]*(\S.*?)[ \t]*$\n?", re.MULTILINE)


@dataclass(frozen=True)
class Flag:
    step: str   # the step that raised it (its LLM stage)
    about: str  # the piece of its input the doubt concerns, by the name the step was shown it under
    says: str


def take(step: str, answer: str) -> Tuple[str, List[Flag]]:
    """The answer without its flag lines, and the flags it carried."""
    flags = [Flag(step, found.group(1), found.group(2)) for found in LINE.finditer(answer)]
    if not flags:
        return answer, []
    _record(flags)
    return LINE.sub("", answer), flags


@traced("step.flags")
def _record(flags: List[Flag]) -> List[Flag]:
    run = run_recorder.current_run()
    if run is not None:
        run.flags.extend(asdict(flag) for flag in flags)
    return flags
