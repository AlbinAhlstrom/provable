"""
Stage timing: how long each stage of a build usually takes, learned from the recorded runs.

The Studio's progress bar gives every stage a length in proportion to its usual share of a build. No table of
durations is kept by hand: the run recorder writes a summary of every finished run (`logs/runs/<id>/summary.json`), and
the averages are read from the kickstarts among them that went well. The recorder keeps a bounded number of runs, so
the averages follow the pipeline as it changes.

- A weight is a stage's share of the summed stage time, not of the clock: stages that run side by side each keep
  their own length.
- With no recorded build every stage weighs the same.
- A stage the recorded builds never ran is treated as an average stage.
"""

import json
import os
from typing import Dict, List, Optional

import run_recorder

BUILD_KIND = "kickstart"
_COUNTED = ("ok", "skipped")  # a skipped stage took the (near-zero) time it took; a failed one says nothing usual


def average_durations(root: Optional[str] = None) -> Dict[str, float]:
    """Each stage's mean duration in seconds over the recorded builds that went well; empty when there are none."""
    root = root or run_recorder.runs_root()
    taken: Dict[str, List[float]] = {}
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        try:
            with open(os.path.join(root, name, "summary.json"), encoding="utf-8") as f:
                summary = json.load(f)
        except (OSError, ValueError):
            continue  # a run still in progress has no summary yet; one cut off while writing cannot be read
        if summary.get("kind") != BUILD_KIND or summary.get("status") != "ok":
            continue
        for stage in summary.get("stages") or []:
            if stage.get("status") in _COUNTED and isinstance(stage.get("duration_s"), (int, float)):
                taken.setdefault(stage["name"], []).append(float(stage["duration_s"]))
    return {name: sum(seconds) / len(seconds) for name, seconds in taken.items()}


def expected_durations(names: List[str], averages: Dict[str, float]) -> Dict[str, float]:
    """How long each of the named stages is expected to take; empty when nothing is known about any of them."""
    known = [averages[name] for name in names if name in averages]
    if not known:
        return {}
    typical = sum(known) / len(known)
    return {name: averages.get(name, typical) for name in names}


def stage_weights(names: List[str], averages: Dict[str, float]) -> Dict[str, float]:
    """Each named stage's share of a build, summing to one."""
    expected = expected_durations(names, averages)
    total = sum(expected.values())
    if not total:
        return {name: 1 / len(names) for name in names}
    return {name: expected[name] / total for name in names}
