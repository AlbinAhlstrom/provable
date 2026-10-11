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
- `stages` lists every stage of a build from the start, the ones not begun as `pending`, each with a `weight`: its
  usual share of a build's time (`stage_timing`, learned from the recorded builds). `fraction` is how far the stage
  has come: all the way once it ended, and while it runs the time it has spent against the time it usually takes.
  `percent` is the weighted sum: how far the whole build has come.
- The checks made on the finished app (`FINAL_CHECKS`: the QA audit and the visual review) are not part of that
  wait. They are listed apart as `final_checks`, and `ready` turns true once every stage that builds the app has
  ended: the app can be used while it is checked, and a check may still change the page.
- Only a kickstart is a build. A single spec execution changes an app that already exists.
"""

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import run_recorder
from onboarding.spec_runner import RuleProgress
from onboarding.stage_timing import average_durations, expected_durations, stage_weights

# What each stage is doing, in the words of someone waiting for their app
STAGE_LABELS = {
    "contract": "Deciding what the product is and how it looks",
    "intent": "Reading the idea",
    "expansion": "Working out what the product needs",
    "decomposition": "Naming the things the product keeps track of",
    "skeleton": "Setting up the backend and the API",
    "persistence": "Writing the rule deck",
    "shell_and_acceptance": "Preparing the workspace",
    "spec_review": "Checking the rules against each other",
    "seed_data": "Writing starting content",
    "ux_plan": "Planning the page and its look",
    "action_protocol": "Naming what people can do",
    "presentation": "Writing the page",
    "page_revisit": "Matching the page to the finished actions",
    "behaviour_specs": "Writing a test for every action and rule, and making the app pass them",
    "qa": "Checking the page on phone, tablet and desktop",
    "visual_review": "Reviewing how the page looks",
}
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


@dataclass
class BuildProgress:
    building: bool = False
    run_id: str = ""
    elapsed_s: float = 0.0
    draft_ready: bool = False     # the skeleton is written: the app can be shown, as a first draft
    page_ready: bool = False      # the page is written
    stages: List[StageProgress] = field(default_factory=list)
    rules: Optional[RuleProgress] = None
    percent: float = 0.0          # how far the whole build has come, by the stages' weights
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


def current_progress(now: Optional[float] = None) -> BuildProgress:
    """The running kickstart's progress, or an idle report when none runs."""
    run = run_recorder.current_run()
    if run is None or run.kind != "kickstart":
        return BuildProgress()
    now = time.time() if now is None else now
    records = [handle.record for handle in list(run.stages)]  # stages open and close on the pipeline's threads while this reads
    begun = {record["name"]: record for record in records}
    names = [name for name in list(STAGE_LABELS) + [n for n in begun if n not in STAGE_LABELS] if name not in FINAL_CHECKS]
    averages = _usual_durations(run)
    weights, expected = stage_weights(names, averages), expected_durations(names, averages)

    progress = BuildProgress(building=True, run_id=run.id, elapsed_s=round(now - run.started, 1))
    for name in names:
        record = begun.get(name)
        stage = StageProgress(name=name, label=_label(name), status=record["status"] if record else "pending",
                              error=record.get("error") if record else None, weight=weights[name])
        if stage.status == "running":
            spent = now - run.started - record["t_offset_s"]
            stage.fraction = min(max(spent, 0.0) / expected[name], 1.0) if expected.get(name) else 0.0
        elif stage.status != "pending":
            stage.fraction = 1.0
        progress.stages.append(stage)
    progress.percent = round(100 * sum(stage.weight * stage.fraction for stage in progress.stages), 1)
    for name in FINAL_CHECKS:
        record = begun.get(name)
        progress.final_checks.append(StageProgress(name=name, label=_label(name), status=record["status"] if record else "pending",
                                                   error=record.get("error") if record else None))
    progress.ready = (all(stage.status not in ("pending", "running") for stage in progress.stages)
                      or any(check.status != "pending" for check in progress.final_checks))
    progress.draft_ready = begun.get(DRAFT_STAGE, {}).get("status") == "ok"
    progress.page_ready = begun.get(PAGE_STAGE, {}).get("status") == "ok"
    rules = begun.get(RULES_STAGE, {}).get("notes", {}).get("rules")
    if rules:
        progress.rules = RuleProgress(**rules)  # kept as plain data: notes go into the run's summary
    return progress
