"""
Page rebuild: write a generated app's page again, against the domain it already has.

A kickstart spends most of its time and nearly all of its tokens on the domain's rules (the TDD loop). A change to
how pages are planned, written, audited or reviewed needs none of that redone:

    kickstart      pitch -> decomposition -> skeleton -> actions -> rules -> UX plan -> page -> QA -> visual review
    page rebuild                                                             UX plan -> page -> QA -> visual review

The rebuild reads what the kickstart decided (`PageBrief`, from the kickstart state) and leaves the domain, its tests,
the seed records and the action protocol exactly as they are. The stages and gates are the kickstart's own
(`synthesis_stages.py`, `page_gates.py`), so a rebuilt page is planned, written and judged the same way.

It answers questions about the page only. Whether a change holds for another product, or touches what the domain
does, still takes a kickstart.
"""

import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from onboarding.intent import ProductIntent
from onboarding.page_gates import PageGates, run_page_gates
from onboarding.router_engine import BusinessSpec, DomainStructureSchema
from onboarding.synthesis_stages import SynthesisOutcome, run_presentation_stage, run_ux_plan_stage
from run_recorder import current_run


class PageBriefError(RuntimeError):
    """The page cannot be rebuilt: what it is written from is missing."""


@dataclass
class PageBrief:
    """What a kickstart decided before it wrote the page."""
    pitch: str
    structure: DomainStructureSchema
    inbox_specs: List[BusinessSpec] = field(default_factory=list)
    action_manifest: Dict[str, Any] = field(default_factory=dict)
    intent: Optional[ProductIntent] = None

    @classmethod
    def from_state(cls, state: Any) -> "PageBrief":
        """Reads the brief from a `KickstartState`."""
        if not state.structure:
            raise PageBriefError("there is no decomposition to write the page from: run a kickstart first "
                                 "(a build from before the decomposition was kept cannot be rebuilt)")
        if not (state.action_manifest or {}).get("actions"):
            raise PageBriefError("there is no action protocol to write the page against: the kickstart did not get that far")
        return cls(pitch=state.business_pitch,
                   structure=DomainStructureSchema.model_validate(state.structure),
                   inbox_specs=[BusinessSpec.model_validate(spec) for spec in state.inbox_specs],
                   action_manifest=dict(state.action_manifest),
                   intent=ProductIntent.from_dict(state.intent) if state.intent else None)


def _has_domain_code(workspace_dir: str) -> bool:
    domain_dir = os.path.join(workspace_dir, "src", "domain")
    return os.path.isdir(domain_dir) and any(
        name.endswith(".py") and name != "__init__.py" for name in os.listdir(domain_dir))


def rebuild_page(
    brief: PageBrief,
    workspace_dir: str,
    ux: Optional[Callable[..., str]] = None,
    presentation: Optional[Callable[..., Dict[str, Any]]] = None,
    gates: Optional[Callable[..., PageGates]] = None,
) -> Dict[str, Any]:
    """Plans, writes and judges the page again. Returns the kickstart's result shape for the stages it ran."""
    if not _has_domain_code(workspace_dir):
        raise PageBriefError(f"there is no domain code in {workspace_dir} to write the page against: "
                             "the workspace was reset since the kickstart")
    if ux is None:
        from onboarding.ux_planner import plan_ux_blueprint as ux
    if presentation is None:
        from onboarding.presentation_projection_synthesizer import synthesize_and_write_presentation_projection as presentation
    if gates is None:
        gates = run_page_gates

    started = time.time()
    master = brief.structure.master_entity()
    outcome = SynthesisOutcome(engine={"success": True, "action_manifest": brief.action_manifest})
    outcome.ux_blueprint = run_ux_plan_stage(
        ux, pitch=brief.pitch, structure=brief.structure, master_name=getattr(master, "name", "") or "",
        intent=brief.intent, inbox_specs=brief.inbox_specs, workspace_dir=workspace_dir)
    run_presentation_stage(presentation, outcome, pitch=brief.pitch, structure=brief.structure,
                           inbox_specs=brief.inbox_specs, workspace_dir=workspace_dir, intent=brief.intent)
    judged = gates(workspace_dir=workspace_dir, pitch=brief.pitch, presentation=outcome.presentation,
                   ux_blueprint=outcome.ux_blueprint)

    return {
        "success": True,
        "created_files": list(outcome.presentation.get("files", [])),
        "timing_breakdown": {**outcome.timings, **judged.timings, "total": round(time.time() - started, 2)},
        "stage_failures": outcome.failures + judged.failures,
        "run_id": current_run().id if current_run() else None,
        "qa": judged.qa,
    }
