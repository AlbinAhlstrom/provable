"""The stages between the skeleton and QA, run alongside each other where nothing forces an order.

    spec_review      ─┐
    seed_data        ─┤
    ux_plan          ─┼─ start together (the UX plan also gives the app on screen its colours)
    action_protocol  ─┘→ action_behaviour ─┬→ presentation (needs the action protocol, the domain and the UX plan)
                                           └→ behaviour_specs (the rule deck, alongside the presentation)

All of them read the same decomposition and the skeleton on disk. The action protocol names the actions; the
behaviour stage writes the methods behind them (`action_behaviour.py`), so the presentation is written against a
domain that already does what the page will ask of it. The presentation also needs the UX plan, which carries the
page's visual direction. While the page is written, the rule deck's behaviour specs run through the TDD loop
(`spec_runner.py`); the stages return once both are done, so QA audits a domain that no longer changes. Seed data and the spec review used to queue in front of the presentation, the slowest step, and
added their full duration to every kickstart.

The stage functions are injected so the ordering policy is testable without an LLM. Each stage keeps its own record
(run_recorder) and its own failure reason; a stage that does not deliver is listed in `failures`, never dropped.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pipeline_trace
from onboarding.action_behaviour import ActionBehaviour
from onboarding.app_inventory import remove_unreachable
from onboarding.draft_theme import THEME_FILE, parse_draft_theme, write_draft_theme
from onboarding.seed_data import SEED_FILE
from onboarding.spec_runner import SpecRun
from run_recorder import stage

THEME_FILES = (THEME_FILE.replace(os.sep, "/"), "frontend/" + THEME_FILE.replace(os.sep, "/"))


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
    behaviour: Optional[Callable[..., ActionBehaviour]] = None,
    specs: Optional[Callable[[List[Any], Callable[[Any], None]], SpecRun]] = None,
) -> SynthesisOutcome:
    """Runs the four stages and returns what each delivered. `on_action_manifest` receives the manifest of a
    successful action protocol (the caller stores it). `specs` runs the rule deck's behaviour specs (the caller owns
    where a spec's status is stored) and tells its second argument how far it has come, which the stage keeps as its
    `rules` note for the build progress; without it they stay pending. An exception in any stage propagates once all
    have finished."""
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
    if behaviour is None:
        from onboarding.action_behaviour import implement_actions as behaviour

    outcome = SynthesisOutcome()
    master = structure.master_entity() if hasattr(structure, "master_entity") else None
    master_name = getattr(master, "name", "") or ""

    def fail(stage_name: str, handle: Any, reason: Any) -> None:
        outcome.failures.append({"stage": stage_name, "error": str(reason)})
        handle.fail(str(reason))

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
        with stage("ux_plan", owns=THEME_FILES) as handle:
            blueprint = ux(pitch=pitch, structure=structure, master_name=master_name, intent=intent,
                           inbox_specs=inbox_specs)
            handle.note("has_visual_direction", "### 6. Visual Direction" in (blueprint or ""))
            # The app is on screen before its page is written: it takes the plan's colours now (draft_theme.py)
            theme = parse_draft_theme(blueprint)
            if theme is None:
                handle.note("draft_theme", "the visual direction has no complete token line; the draft keeps its neutral colours")
            else:
                write_draft_theme(workspace_dir, theme)
                handle.note("draft_theme", asdict(theme))
            return blueprint

    def run_rule_specs() -> None:
        # The domain's rules, on top of the methods the behaviour stage wrote. Overlaps the presentation, so it
        # declares the files it writes.
        with stage("behaviour_specs", owns=("src/domain", "tests/unit", "tests/pending")) as handle:
            if specs is None:
                return handle.skip("no spec executor was given; the specs stay pending")
            if not outcome.engine.get("success") or not outcome.behaviour.success:
                return handle.skip("the actions the specs build on are not implemented")
            started = time.time()
            outcome.specs = specs(inbox_specs, lambda rules: handle.note("rules", asdict(rules)))
            outcome.timings["5c_behaviour_specs"] = round(time.time() - started, 2)
            handle.note("fulfilled", outcome.specs.fulfilled)
            if outcome.specs.skipped:
                handle.skip(outcome.specs.skipped)
            elif not outcome.specs.success:
                handle.note("unfulfilled", outcome.specs.unfulfilled)
                fail("behaviour_specs", handle, outcome.specs.error)

    def protocol_then_presentation(ux_plan: Any, pool: ThreadPoolExecutor) -> None:
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

        # The methods behind those actions, written now so the page is built against the class as it really is
        started = time.time()
        with stage("action_behaviour") as handle:
            if not outcome.engine.get("success"):
                handle.skip("there is no action protocol to implement")
            else:
                outcome.behaviour = behaviour(outcome.engine.get("action_manifest") or {}, workspace_dir, rules=inbox_specs)
                outcome.timings["5a_action_behaviour"] = round(time.time() - started, 2)
                handle.note("implemented", outcome.behaviour.implemented)
                handle.note("runs", outcome.behaviour.runs)
                if outcome.behaviour.skipped:
                    handle.skip(outcome.behaviour.skipped)
                elif not outcome.behaviour.success:
                    handle.note("missing", outcome.behaviour.missing)
                    fail("action_behaviour", handle, outcome.behaviour.error)

        alongside.append(pool.submit(pipeline_trace.bind_context(run_rule_specs)))

        # Interactive presentation projection & React shell
        outcome.ux_blueprint = ux_plan.result()
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
                fail("presentation", handle, outcome.presentation.get("error") or "no files were written")
            else:
                # The page replaced the skeleton's app; the scaffold it no longer imports would only mislead later edits
                outcome.removed_scaffold = remove_unreachable(workspace_dir)
                if outcome.removed_scaffold:
                    handle.note("removed_scaffold", outcome.removed_scaffold)
                    # A component the page never imports went with the scaffold: QA and the visual review are
                    # handed the files that are still there
                    outcome.presentation["files"] = [
                        path for path in outcome.presentation.get("files", [])
                        if os.path.exists(path if os.path.isabs(path) else os.path.join(workspace_dir, path))]

    with ThreadPoolExecutor(max_workers=4, thread_name_prefix="synthesis") as pool:
        alongside = [pool.submit(pipeline_trace.bind_context(task)) for task in (review_specs, seed_content)]
        ux_plan = pool.submit(pipeline_trace.bind_context(plan_ux))
        try:
            protocol_then_presentation(ux_plan, pool)
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
