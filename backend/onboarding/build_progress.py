"""
Build progress: what a running kickstart has delivered so far, for the Studio to show while it runs.

A kickstart answers once everything is done, but its page is written long before that: the rules, the QA audit and the
visual review come after. So the Studio shows the app as soon as there is a page, and says what is still being built.
Nothing is tracked for this: the run recorder already holds every stage of the running build with its status, and this
module reads that out as a typed report.

- `draft_ready` turns true when the skeleton is written: from then on the workspace serves an app that can be
  shown, first as the skeleton's draft (the records under plain names, in the plan's colours once decided).
- `page_ready` turns true when the presentation stage delivered: the draft has been replaced by the written page.
- `rules` is what the spec runner reports after every behaviour spec (`spec_runner.RuleProgress`).
- `opening` lists the stages that come before there is anything to show: the build's front and the skeleton. The
  Studio shows them as steps on the pitch view, without a bar.
- `stages` lists every stage after that from the start, the ones not begun as `pending`, each with a `weight`: its
  usual share of the time those stages take (`stage_timing`, learned from the recorded builds). `fraction` is how
  far the stage has come: all the way once it ended, and while it runs the time it has spent against the time it
  usually takes. `percent` is the weighted sum: how far the build has come since its first draft, and
  `since_draft_s` is how long ago that was.
- The checks made on the finished app (`FINAL_CHECKS`: the QA audit and the visual review) are not part of that
  wait. They are listed apart as `final_checks`, and `ready` turns true once every stage that builds the app has
  ended: the app can be used while it is checked, and a check may still change the page.
- A build opens with one of two fronts (`kickstart_front.py`): the product contract, or intent, expansion and
  decomposition. Once one of them has begun, the other's stages are not part of the build's road.
- A long stage that is one call says nothing while it runs, so it is given `phases` (`STAGE_PHASES`): the parts of
  its work, in the order someone waiting would expect them, each with the length it is expected to seem to have.
  `phase` is the one it is in. The phases before the last are over well before the stage usually ends
  (`PHASES_DONE_BY`), and the last one holds until it does. Their lengths vary a little from build to build
  (`PHASE_JITTER`, drawn from the run's id, so every report of one build agrees). It is pacing for someone waiting,
  not a report from inside the call.
- Only a kickstart is a build. A single spec execution changes an app that already exists.
"""

import random
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import run_recorder
from onboarding.spec_runner import RuleProgress
from onboarding.stage_timing import average_durations, expected_durations, stage_weights

# What each stage is doing, as a step someone waiting for their app reads at a glance
STAGE_LABELS = {
    "contract": "Planning the product",
    "intent": "Reading the prompt",
    "expansion": "Writing the specification",
    "decomposition": "Defining the data model",
    "skeleton": "Setting up the API",
    "persistence": "Saving rules",
    "shell_and_acceptance": "Preparing workspace",
    "spec_review": "Reviewing rules",
    "seed_data": "Writing starting content",
    "ux_plan": "Planning layout and theme",
    "action_protocol": "Defining actions",
    "presentation": "Building page",
    "page_revisit": "Aligning page with actions",
    "behaviour_specs": "Testing rules",
    "qa": "Checking phone, tablet and desktop",
    "visual_review": "Reviewing design",
}
# The parts of a stage's work, for a stage that is one long call, each with its length against the others'. The last
# one holds until the stage ends, so its length is not given: it names what the build turns to next.
STAGE_PHASES: Dict[str, List[Tuple[str, float]]] = {
    "contract": [
        ("Reading the prompt", 1.0),
        ("Defining actions", 2.0),
        ("Writing rules", 3.0),
        ("Planning layout", 2.0),
        ("Selecting theme", 1.5),
        ("Building page", 0.0),
    ],
}
PHASES_DONE_BY = 0.7   # the share of the stage's usual time by which every phase but the last is over
PHASE_JITTER = 0.35    # how far a phase's length may be from its given one, either way, in one build
PHASE_SECONDS = 5.0    # a phase's mean length when no recorded build says how long its stage takes
FRONTS = (("contract",), ("intent", "expansion", "decomposition"))  # a build opens with one of these
DRAFT_STAGE = "skeleton"
PAGE_STAGE = "presentation"
RULES_STAGE = "behaviour_specs"
FINAL_CHECKS = ("qa", "visual_review")  # made on the finished app; they may still change the page


@dataclass
class StageProgress:
    name: str
    label: str
    status: str                    # pending | running | ok | failed | skipped
    error: Optional[str] = None
    weight: float = 0.0            # the stage's usual share of a build, 0..1; all stages sum to 1
    fraction: float = 0.0          # how far the stage has come, 0..1
    phases: List[str] = field(default_factory=list)  # the parts of its work, when it has any to name
    phase: int = 0                 # the part it is in; past the last one once the stage ended


@dataclass
class BuildProgress:
    building: bool = False
    run_id: str = ""
    elapsed_s: float = 0.0
    draft_ready: bool = False     # the skeleton is written: the app can be shown, as a first draft
    page_ready: bool = False      # the page is written
    opening: List[StageProgress] = field(default_factory=list)  # what comes before the first draft; no share of the bar
    stages: List[StageProgress] = field(default_factory=list)   # what comes after it
    rules: Optional[RuleProgress] = None
    percent: float = 0.0          # how far the build has come since its first draft, by the stages' weights
    since_draft_s: float = 0.0    # how long ago the first draft was written
    ready: bool = False           # everything that builds the app has ended; only the final checks may still run
    final_checks: List[StageProgress] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_averages: Tuple[str, Dict[str, float]] = ("", {})  # the recorded builds are read once per running build


def _usual_durations(run: "run_recorder.Run") -> Dict[str, float]:
    global _averages
    if _averages[0] != run.dir:
        _averages = (run.dir, average_durations())
    return _averages[1]


def _label(name: str) -> str:
    return STAGE_LABELS.get(name) or name.replace("_", " ").capitalize()


def _other_fronts(begun: Dict[str, Any]) -> List[str]:
    """The stages of the fronts this build does not run; none while it has not opened yet."""
    running = [front for front in FRONTS if any(name in begun for name in front)]
    return [name for front in FRONTS if running and front not in running for name in front]


def phase_ends(lengths: List[float], usual: Optional[float], seed: str) -> List[float]:
    """When each phase but the last is over, in seconds into the stage. `lengths` are those phases' given lengths."""
    draw = random.Random(seed)
    varied = [length * draw.uniform(1 - PHASE_JITTER, 1 + PHASE_JITTER) for length in lengths]
    total = PHASES_DONE_BY * usual if usual else PHASE_SECONDS * len(lengths)
    ends, spent = [], 0.0
    for length in varied:
        spent += length / sum(varied) * total
        ends.append(spent)
    return ends


def _stage(name: str, record: Optional[Dict[str, Any]], spent: float, usual: Optional[float], weight: float, seed: str) -> StageProgress:
    stage = StageProgress(name=name, label=_label(name), status=record["status"] if record else "pending",
                          error=record.get("error") if record else None, weight=weight,
                          phases=[label for label, _ in STAGE_PHASES.get(name, ())])
    if stage.status == "running":
        stage.fraction = min(max(spent, 0.0) / usual, 1.0) if usual else 0.0
        if stage.phases:
            ends = phase_ends([length for _, length in STAGE_PHASES[name][:-1]], usual, seed)
            stage.phase = sum(1 for end in ends if spent >= end)
    elif stage.status != "pending":
        stage.fraction = 1.0
        stage.phase = len(stage.phases)
    return stage


def current_progress(now: Optional[float] = None) -> BuildProgress:
    """The running kickstart's progress, or an idle report when none runs."""
    run = run_recorder.current_run()
    if run is None or run.kind != "kickstart":
        return BuildProgress()
    now = time.time() if now is None else now
    records = [handle.record for handle in list(run.stages)]  # stages open and close on the pipeline's threads while this reads
    begun = {record["name"]: record for record in records}
    fronts = [name for front in FRONTS for name in front]
    opening = [name for name in fronts if name not in _other_fronts(begun)] + [DRAFT_STAGE]
    names = [name for name in list(STAGE_LABELS) + [n for n in begun if n not in STAGE_LABELS]
             if name not in fronts and name != DRAFT_STAGE and name not in FINAL_CHECKS]
    averages = _usual_durations(run)
    weights, expected = stage_weights(names, averages), expected_durations(names + opening, averages)

    def stage(name: str) -> StageProgress:
        record = begun.get(name)
        spent = now - run.started - record["t_offset_s"] if record else 0.0
        return _stage(name, record, spent, expected.get(name), weights.get(name, 0.0), run.id)

    progress = BuildProgress(building=True, run_id=run.id, elapsed_s=round(now - run.started, 1))
    progress.opening = [stage(name) for name in opening]
    progress.stages = [stage(name) for name in names]
    progress.percent = round(100 * sum(stage.weight * stage.fraction for stage in progress.stages), 1)
    for name in FINAL_CHECKS:
        record = begun.get(name)
        progress.final_checks.append(StageProgress(name=name, label=_label(name), status=record["status"] if record else "pending",
                                                   error=record.get("error") if record else None))
    progress.ready = (all(stage.status not in ("pending", "running") for stage in progress.opening + progress.stages)
                      or any(check.status != "pending" for check in progress.final_checks))
    draft = begun.get(DRAFT_STAGE, {})
    progress.draft_ready = draft.get("status") == "ok"
    if progress.draft_ready:
        progress.since_draft_s = round(max(now - run.started - draft["t_offset_s"] - draft["duration_s"], 0.0), 1)
    progress.page_ready = begun.get(PAGE_STAGE, {}).get("status") == "ok"
    rules = begun.get(RULES_STAGE, {}).get("notes", {}).get("rules")
    if rules:
        progress.rules = RuleProgress(**rules)  # kept as plain data: notes go into the run's summary
    return progress
