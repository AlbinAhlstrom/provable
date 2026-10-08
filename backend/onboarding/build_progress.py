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
- Only a kickstart is a build. A single spec execution changes an app that already exists.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import run_recorder
from onboarding.spec_runner import RuleProgress

# What each stage is doing, in the words of someone waiting for their app
STAGE_LABELS = {
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
    "action_behaviour": "Making each action work",
    "presentation": "Writing the page",
    "behaviour_specs": "Writing the rules, test first",
    "qa": "Checking the page on phone, tablet and desktop",
    "visual_review": "Reviewing how the page looks",
}
DRAFT_STAGE = "skeleton"
PAGE_STAGE = "presentation"
RULES_STAGE = "behaviour_specs"


@dataclass
class StageProgress:
    name: str
    label: str
    status: str                    # running | ok | failed | skipped
    error: Optional[str] = None


@dataclass
class BuildProgress:
    building: bool = False
    run_id: str = ""
    elapsed_s: float = 0.0
    draft_ready: bool = False     # the skeleton is written: the app can be shown, as a first draft
    page_ready: bool = False      # the page is written
    stages: List[StageProgress] = field(default_factory=list)
    rules: Optional[RuleProgress] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def current_progress() -> BuildProgress:
    """The running kickstart's progress, or an idle report when none runs."""
    import time

    run = run_recorder.current_run()
    if run is None or run.kind != "kickstart":
        return BuildProgress()
    progress = BuildProgress(building=True, run_id=run.id, elapsed_s=round(time.time() - run.started, 1))
    for handle in list(run.stages):  # stages open and close on the pipeline's threads while this reads
        record = handle.record
        progress.stages.append(StageProgress(name=record["name"], label=STAGE_LABELS.get(record["name"], record["name"].replace("_", " ").capitalize()),
                                             status=record["status"], error=record.get("error")))
        if record["name"] == DRAFT_STAGE and record["status"] == "ok":
            progress.draft_ready = True
        if record["name"] == PAGE_STAGE and record["status"] == "ok":
            progress.page_ready = True
        if record["name"] == RULES_STAGE and record["notes"].get("rules"):
            progress.rules = RuleProgress(**record["notes"]["rules"])  # kept as plain data: notes go into the run's summary
    return progress
