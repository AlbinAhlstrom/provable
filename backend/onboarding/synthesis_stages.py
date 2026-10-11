"""The stages between the skeleton and QA, run alongside each other where nothing forces an order.

    spec_review      ─┐
    seed_data        ─┤
    ux_plan          ─┼─ start together (the UX plan also gives the app on screen its colours and outline)
    action_protocol  ─┘─┬→ presentation (needs the action protocol and the UX plan) ─┬→ page_revisit
                        └→ behaviour_specs (the actions and the rule deck, one round) ─┘

All of them read the same decomposition and the skeleton on disk. The action protocol names the actions and fixes
what a page needs to know of them: their parameters, the values the fields take, what a new object holds. So the
page is written at once, while the domain round writes the methods behind the actions and the deck's rules in one
pass of the test loop (`domain_round.py`): every first test side by side, then one code answer per class. It used
to be two passes, the rules waiting for the actions. Writing the methods can change what a class holds, so the
fields are compared afterwards (`page_contract.py`), and only a class that gained or lost one sends the page back to
be written again, once, for the classes as they are. The presentation also needs the UX plan, which carries the
page's visual direction. The stages return once everything is done, so QA audits a domain that no longer changes.
Seed data and the spec review used to queue in front of the presentation, the slowest step, and added their full
duration to every kickstart.

The stage functions are injected so the ordering policy is testable without an LLM. Each stage keeps its own record
(run_recorder) and its own failure reason; a stage that does not deliver is listed in `failures`, never dropped.
"""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pipeline_trace
from onboarding.action_behaviour import ActionBehaviour
from onboarding.domain_round import DomainRound
from onboarding.app_inventory import remove_unreachable
from onboarding.draft_theme import THEME_FILE, DraftTheme, parse_draft_layout, parse_draft_theme, write_draft_theme
from onboarding.page_contract import FieldChange, domain_fields, field_changes
from onboarding.seed_data import SEED_FILE
from onboarding.spec_runner import SpecRun
from run_recorder import stage

THEME_FILES = (THEME_FILE.replace(os.sep, "/"), "frontend/" + THEME_FILE.replace(os.sep, "/"))
DOMAIN_FILES = ("src/domain", "tests/unit", "tests/pending")  # what the TDD loop writes, beside the page's files


@dataclass
class SynthesisOutcome:
    spec_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    engine: Dict[str, Any] = field(default_factory=dict)        # the action protocol stage's result
    seed: Dict[str, Any] = field(default_factory=dict)
    presentation: Dict[str, Any] = field(default_factory=dict)
    failures: List[Dict[str, str]] = field(default_factory=list)
    timings: Dict[str, float] = field(default_factory=dict)
    files: List[str] = field(default_factory=list)              # every file the stages report having written
    ux_blueprint: str = ""                                      # the UX plan, including the visual direction
    removed_scaffold: List[str] = field(default_factory=list)   # skeleton files the written page no longer reaches
    behaviour: ActionBehaviour = field(default_factory=ActionBehaviour)  # the methods behind the manifest's actions
    specs: SpecRun = field(default_factory=SpecRun)             # which rule specs the kickstart fulfilled
    page_revisit: List[str] = field(default_factory=list)       # what the classes changed under the page, if anything


def _fail(outcome: SynthesisOutcome, stage_name: str, handle: Any, reason: Any) -> None:
    outcome.failures.append({"stage": stage_name, "error": str(reason)})
    handle.fail(str(reason))


def run_ux_plan_stage(ux: Callable[..., str], *, pitch: str, structure: Any, master_name: str, intent: Optional[Any],
                      inbox_specs: List[Any], workspace_dir: str) -> str:
    """The UX plan as a recorded stage: returns the blueprint and gives the app on screen the plan's colours."""
    with stage("ux_plan", owns=THEME_FILES) as handle:
        blueprint = ux(pitch=pitch, structure=structure, master_name=master_name, intent=intent,
                       inbox_specs=inbox_specs)
        handle.note("has_visual_direction", "### 6. Visual Direction" in (blueprint or ""))
        # The app is on screen before its page is written: it takes the plan's colours and the outline of its
        # main view now (draft_theme.py)
        theme, layout = parse_draft_theme(blueprint), parse_draft_layout(blueprint)
        handle.note("draft_theme", asdict(theme) if theme else
                    "the visual direction has no complete token line; the draft keeps its neutral colours")
        handle.note("draft_layout", asdict(layout) if layout else
                    "the visual direction has no complete layout line; the draft shows no outline of the main view")
        if theme or layout:
            write_draft_theme(workspace_dir, theme or DraftTheme(), layout)
        return blueprint


def run_presentation_stage(presentation: Callable[..., Dict[str, Any]], outcome: SynthesisOutcome, *, pitch: str,
                           structure: Any, inbox_specs: List[Any], workspace_dir: str, intent: Optional[Any]) -> None:
    """The page as a recorded stage, written from `outcome.engine`'s action protocol and `outcome.ux_blueprint`;
    what it delivered (or why it did not) is left in `outcome`."""
    started = time.time()
    with stage("presentation") as handle:
        outcome.presentation = presentation(
            pitch=pitch, structure=structure, inbox_specs=inbox_specs, workspace_dir=workspace_dir,
            action_manifest=outcome.engine.get("action_manifest"), router_code=outcome.engine.get("router_code"),
            ux_blueprint=outcome.ux_blueprint, intent=intent)
        outcome.timings["5b_presentation_projection"] = round(time.time() - started, 2)
        for key in ("component_lines", "omitted"):
            if outcome.presentation.get(key):
                handle.note(key, outcome.presentation[key])
        if not outcome.presentation.get("success"):
            _fail(outcome, "presentation", handle, outcome.presentation.get("error") or "no files were written")
        else:
            _clear_scaffold(outcome, handle, workspace_dir)


def _clear_scaffold(outcome: SynthesisOutcome, handle: Any, workspace_dir: str) -> None:
    """The page replaced the skeleton's app; the scaffold it no longer imports would only mislead later edits."""
    removed = remove_unreachable(workspace_dir)
    if removed:
        outcome.removed_scaffold = outcome.removed_scaffold + [path for path in removed if path not in outcome.removed_scaffold]
        handle.note("removed_scaffold", removed)
        # A component the page never imports went with the scaffold: QA and the visual review are
        # handed the files that are still there
        outcome.presentation["files"] = [
            path for path in outcome.presentation.get("files", [])
            if os.path.exists(path if os.path.isabs(path) else os.path.join(workspace_dir, path))]


def run_page_revisit_stage(presentation: Callable[..., Dict[str, Any]], outcome: SynthesisOutcome,
                           changes: List[FieldChange], *, pitch: str, structure: Any, inbox_specs: List[Any],
                           workspace_dir: str, intent: Optional[Any]) -> None:
    """The page was written while its actions were. When that changed what a class holds (`changes`), the page is
    written once more, for the classes as they are; otherwise the stage is skipped. A second writing that does not
    deliver leaves the first page in place and is reported."""
    with stage("page_revisit") as handle:
        if not outcome.presentation.get("success"):
            return handle.skip("there is no page to revisit")
        if not changes:
            return handle.skip("the classes hold the fields the page was written for")
        outcome.page_revisit = [change.describe() for change in changes]
        handle.note("changed", outcome.page_revisit)
        started = time.time()
        rewritten = presentation(
            pitch=pitch, structure=structure, inbox_specs=inbox_specs, workspace_dir=workspace_dir,
            action_manifest=outcome.engine.get("action_manifest"), router_code=outcome.engine.get("router_code"),
            ux_blueprint=outcome.ux_blueprint, intent=intent)
        outcome.timings["5d_page_revisit"] = round(time.time() - started, 2)
        if not rewritten.get("success"):
            return _fail(outcome, "page_revisit", handle, rewritten.get("error") or "no files were written")
        outcome.presentation = rewritten
        _clear_scaffold(outcome, handle, workspace_dir)


def run_synthesis_stages(
    *,
    pitch: str,
    structure: Any,
    inbox_specs: List[Any],
    workspace_dir: str,
    intent: Optional[Any],
    on_action_manifest: Callable[[Dict[str, Any]], None],
    review: Optional[Callable[..., Dict[str, Any]]] = None,
    protocol: Optional[Callable[..., Dict[str, Any]]] = None,
    seed: Optional[Callable[..., Dict[str, Any]]] = None,
    presentation: Optional[Callable[..., Dict[str, Any]]] = None,
    ux: Optional[Callable[..., str]] = None,
    domain: Optional[Callable[[Dict[str, Any], List[Any], Callable[[Any], None]], DomainRound]] = None,
) -> SynthesisOutcome:
    """Runs the stages and returns what each delivered. `on_action_manifest` receives the manifest of a
    successful action protocol (the caller stores it). `domain` runs the domain round on that manifest and the rule
    deck (the caller owns how specs are executed and where a rule's status is stored) and tells its third argument
    how far the rules have come, which the stage keeps as its `rules` note for the build progress; without it the
    actions have no methods and the rules stay pending. An exception in any stage propagates once all have
    finished."""
    if review is None:
        from onboarding.spec_review import review_spec_consistency as review
    if protocol is None:
        from onboarding.domain_engine_synthesizer import synthesize_action_protocol as protocol
    if seed is None:
        from onboarding.seed_data import synthesize_seed_data as seed
    if presentation is None:
        from onboarding.presentation_projection_synthesizer import synthesize_and_write_presentation_projection as presentation

    if ux is None:
        from onboarding.ux_planner import plan_ux_blueprint as ux

    outcome = SynthesisOutcome()
    master = structure.master_entity() if hasattr(structure, "master_entity") else None
    master_name = getattr(master, "name", "") or ""

    def fail(stage_name: str, handle: Any, reason: Any) -> None:
        _fail(outcome, stage_name, handle, reason)

    def review_specs() -> None:
        # Specs that contradict each other are reported now, not discovered as a late regression dead end
        with stage("spec_review", owns=()) as handle:
            result = review(inbox_specs, intent=intent)
            if not result["success"]:
                return fail("spec_review", handle, result["error"])
            outcome.spec_conflicts = result["conflicts"]
            for conflict in outcome.spec_conflicts:
                print(f"[Kickstart] ⚠️ Specs {conflict['specs']} contradict each other: {conflict['reason']}", flush=True)
            handle.note("conflicts", len(outcome.spec_conflicts))

    def seed_content() -> None:
        # Starting content for the entities the audience is shown (offerings, credentials...), so the page renders
        # real records from the API instead of the model inventing them as literals
        with stage("seed_data", owns=(SEED_FILE.replace(os.sep, "/"),)) as handle:
            outcome.seed = seed(pitch=pitch, structure=structure, inbox_specs=inbox_specs,
                                workspace_dir=workspace_dir, intent=intent)
            if outcome.seed.get("attempts"):
                handle.note("attempts", len(outcome.seed["attempts"]))
            if outcome.seed.get("skipped"):
                handle.skip(outcome.seed["skipped"])
            elif not outcome.seed.get("success"):
                fail("seed_data", handle, outcome.seed.get("error"))

    def plan_ux() -> str:
        return run_ux_plan_stage(ux, pitch=pitch, structure=structure, master_name=master_name, intent=intent,
                                 inbox_specs=inbox_specs, workspace_dir=workspace_dir)

    def write_domain() -> None:
        # The methods behind the actions and the deck's rules, in one round. Overlaps the presentation, so it
        # declares the files it writes.
        with stage("behaviour_specs", owns=DOMAIN_FILES) as handle:
            if not outcome.engine.get("success"):
                return handle.skip("there is no action protocol to implement")
            if domain is None:
                return handle.skip("no executor was given; the actions have no methods and the rules stay pending")
            started = time.time()
            done = domain(outcome.engine.get("action_manifest") or {}, inbox_specs,
                          lambda rules: handle.note("rules", asdict(rules)))
            outcome.behaviour, outcome.specs = done.behaviour, done.specs
            outcome.timings["5c_domain_round"] = round(time.time() - started, 2)
            handle.note("implemented", outcome.behaviour.implemented)
            handle.note("runs", outcome.behaviour.runs)
            handle.note("fulfilled", outcome.specs.fulfilled)
            reasons = []
            if not outcome.behaviour.success:
                handle.note("missing", outcome.behaviour.missing)
                outcome.failures.append({"stage": "action_behaviour", "error": outcome.behaviour.error})
                reasons.append(outcome.behaviour.error)
            if not outcome.specs.success:
                handle.note("unfulfilled", outcome.specs.unfulfilled)
                outcome.failures.append({"stage": "behaviour_specs", "error": outcome.specs.error})
                reasons.append(outcome.specs.error)
            if reasons:
                handle.fail("; ".join(reasons))

    def design_actions() -> None:
        # Action protocol (the domain class and the action endpoint come from the skeleton + TDD loop)
        started = time.time()
        with stage("action_protocol") as handle:
            outcome.engine = protocol(pitch=pitch, structure=structure, inbox_specs=inbox_specs,
                                      workspace_dir=workspace_dir, intent=intent)
            outcome.timings["5a_domain_engine"] = round(time.time() - started, 2)
            if outcome.engine.get("success"):
                actions = (outcome.engine.get("action_manifest") or {}).get("actions") or []
                handle.note("actions", [a.get("name") for a in actions if isinstance(a, dict)])
                handle.ok()
                on_action_manifest(outcome.engine.get("action_manifest") or {})
            else:
                fail("action_protocol", handle, outcome.engine.get("error"))

    implemented = threading.Event()
    fields: Dict[str, Dict[str, List[str]]] = {}  # what the classes hold: "before" and "after" the round

    def domain_round() -> None:
        try:
            write_domain()
            fields["after"] = domain_fields(workspace_dir)
        finally:
            implemented.set()

    def page_alongside_the_actions(ux_plan: Any, pool: ThreadPoolExecutor) -> None:
        design_actions()
        fields["before"] = domain_fields(workspace_dir)
        alongside.append(pool.submit(pipeline_trace.bind_context(domain_round)))

        # Interactive presentation projection & React shell, written while the actions are
        outcome.ux_blueprint = ux_plan.result()
        page = dict(pitch=pitch, structure=structure, inbox_specs=inbox_specs, workspace_dir=workspace_dir, intent=intent)
        run_presentation_stage(presentation, outcome, **page)

        # One more look when the round changed what a class holds
        implemented.wait()
        changes = field_changes(fields["before"], fields["after"]) if "after" in fields else []
        run_page_revisit_stage(presentation, outcome, changes, **page)

    with ThreadPoolExecutor(max_workers=6, thread_name_prefix="synthesis") as pool:
        alongside = [pool.submit(pipeline_trace.bind_context(task)) for task in (review_specs, seed_content)]
        ux_plan = pool.submit(pipeline_trace.bind_context(plan_ux))
        try:
            page_alongside_the_actions(ux_plan, pool)
        finally:
            crashes = [f.exception() for f in alongside]  # waits for all of them
    for crash in crashes:
        if crash is not None:
            raise crash

    for result in (outcome.engine, outcome.seed, outcome.presentation):
        for path in result.get("files", []):
            if path not in outcome.files:
                outcome.files.append(path)
    return outcome
