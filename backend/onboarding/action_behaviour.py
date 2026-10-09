"""
Action behaviour: the kickstart writes the methods behind the actions its page offers.

The action protocol only names the actions (`action_protocol.py`), and the generated API runs an action by calling the
public method of that name on the aggregate. Until that method exists every action answers "Unknown action": the page
looks finished and nothing on it works. So, while the page is written, each aggregate's actions go through the same
TDD loop every later spec uses (a RED test from the action's own description, then GREEN), and the code is checked
against the manifest (`check_action_contract`). The page needs the manifest, not the methods; a class whose fields
changed while its methods were written sends the page back once (`page_contract.py`).

- One spec per aggregate, covering all of its actions: one test file, one implementation.
- The same spec states what a newly created object holds (the manifest's `starting_states`): the application creates
  an object and shows it at once, so a class that needs an action to become usable shows up empty.
- Its test joins the regression suite (`tests/unit/test_spec_act_<aggregate>.py`), so a later spec that refines an
  action is written knowing it and cannot break it unnoticed.
- An action still without a method afterwards fails the stage by name. Nothing is stubbed.

Aggregates run one after another: the loop's regression gate runs the whole `tests/unit` folder, which a second loop
writing its not-yet-passing test there at the same time would fail.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from onboarding.action_protocol import check_action_contract, shared_words, starting_state
from onboarding.router_engine import BusinessSpec
from onboarding.skeleton_builder import to_snake_case
from pipeline_trace import traced


@dataclass
class ActionBehaviour:
    """What implementing the manifest's actions delivered."""
    implemented: List[str] = field(default_factory=list)
    missing: List[Dict[str, str]] = field(default_factory=list)   # {action, aggregate, performed_by}, as the contract check reports
    runs: List[Dict[str, Any]] = field(default_factory=list)      # per aggregate: {aggregate, spec_id, status, error, attempts}
    skipped: str = ""

    @property
    def success(self) -> bool:
        return not self.missing

    @property
    def error(self) -> str:
        if not self.missing:
            return ""
        names = ", ".join(f"{m['aggregate']}.{m['action']}" for m in self.missing)
        reasons = "; ".join(f"{r['aggregate']}: {r['error']}" for r in self.runs if r.get("error"))
        return f"no method implements: {names}" + (f" ({reasons})" if reasons else "")


def action_spec(aggregate: str, actions: List[Dict[str, Any]], starting_state: str = "",
                manifest: Optional[Dict[str, Any]] = None) -> BusinessSpec:
    """The one spec that states everything the application will ask this aggregate to do, and what a new object
    holds before any of it (the application shows a new object at once, so the class starts that way by itself)."""
    scenarios = []
    if starting_state:
        scenarios.append(f"When a {aggregate} is created with only its required fields and nothing is called on it "
                         f"Then {starting_state.rstrip('.')}.")
    for action in actions:
        params = ", ".join(str(p) for p in action.get("params") or [])
        effect = str(action.get("description") or "the object carries out the action").strip().rstrip(".")
        scenarios.append(f"When `{action['name']}({params})` is called with valid values Then {effect}, "
                         f"and the object's fields show it afterwards.")
    return BusinessSpec(
        spec_id=f"SPEC-ACT-{aggregate.upper()}",
        title=f"{aggregate} carries out its actions",
        description=(f"The application calls these methods on {aggregate} by exactly these names and keyword arguments. "
                     f"Each one changes the object as described."
                     + "".join(f"\n{line}" for line in shared_words(manifest, aggregate))),
        given_when_then=(f"Given a {aggregate} in a state where the action is allowed (arrange that by setting its fields). "
                         + " ".join(scenarios) + " One test function per method."),
        target_aggregate=aggregate,
        category="ACTION",
    )


@traced("behaviour.implement_actions")
def implement_actions(
    manifest: Optional[Dict[str, Any]],
    workspace_dir: str,
    run_spec: Optional[Callable[..., Dict[str, Any]]] = None,
    rules: Optional[List[BusinessSpec]] = None,
) -> ActionBehaviour:
    """Runs one TDD loop per aggregate that has actions, then compares the code with the manifest. `rules` is the
    product's rule deck: the writer of the actions' test is shown the rules of its class, which are implemented
    next and must not contradict what its test expects."""
    if run_spec is None:
        # The batch loop with one spec: the same gates as the single loop, and a test that no code answer could
        # meet goes back to its writer once (a test with a slip in it must not cost the build its whole domain)
        from service_layer import tdd_batch

        def run_spec(spec: BusinessSpec, workspace_dir: str, action_manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            return tdd_batch.execute_specs_together([spec], workspace_dir, action_manifest=action_manifest,
                                                    deck=[spec] + list(rules or []))[spec.spec_id]

    by_aggregate: Dict[str, List[Dict[str, Any]]] = {}
    for action in (manifest or {}).get("actions") or []:
        if isinstance(action, dict) and action.get("name") and action.get("aggregate"):
            by_aggregate.setdefault(str(action["aggregate"]), []).append(action)
    if not by_aggregate:
        return ActionBehaviour(skipped="the action protocol offers no action")

    result = ActionBehaviour()
    for aggregate, actions in by_aggregate.items():
        run = {"aggregate": aggregate, "spec_id": "", "status": "", "error": "", "attempts": 0}
        result.runs.append(run)
        if not os.path.exists(os.path.join(workspace_dir, "src", "domain", f"{to_snake_case(aggregate)}.py")):
            run.update(status="NO_DOMAIN_CLASS", error="the decomposition has no such class")
            continue
        spec = action_spec(aggregate, actions, starting_state(manifest, aggregate), manifest=manifest)
        run["spec_id"] = spec.spec_id
        try:
            loop = run_spec(spec, workspace_dir, action_manifest=manifest)
        except Exception as err:  # a provider or infrastructure error: reported with its reason, never retried
            run.update(status="ERROR", error=f"{type(err).__name__}: {err}")
            continue
        run.update(status=str(loop.get("status") or ""), error=str(loop.get("error") or ""),
                   attempts=len(loop.get("attempts") or []))
        print(f"[Compiler:Behaviour] {aggregate}: {run['status']} ({[a['name'] for a in actions]})", flush=True)

    contract = check_action_contract(workspace_dir, manifest)
    result.implemented, result.missing = contract["implemented"], contract["missing"]
    return result
