"""
Action behaviour: the kickstart writes the methods behind the actions its page offers.

The action protocol only names the actions (`action_protocol.py`), and the generated API runs an action by calling the
public method of that name on the aggregate. Until that method exists every action answers "Unknown action": the page
looks finished and nothing on it works. So each action is a spec of its own in the kickstart's one pass of the test
loop (`domain_round.py`), beside the deck's rules, and the code is checked against the manifest afterwards
(`check_action_contract`). The page needs the manifest, not the methods; a class whose fields changed while its
methods were written sends the page back once (`page_contract.py`).

- One spec per action, and one for what a newly created object holds (the manifest's `starting_states`): the
  application creates an object and shows it at once, so a class that needs an action to become usable shows up
  empty. A starting state the class's defaults already give has no spec: there is nothing to write, and its test
  would pass on the empty class. Their tests are written side by side with the rules' tests, and the class gets
  one code answer for all.
- An action's spec is one call in the simplest state the action is allowed in. What the action refuses, ignores or
  does from another state is the rules' to prove: repeated here, each case is one more expectation that can be
  wrong, in a test the whole class has to pass.
- An action that a rule of the deck is about has no spec here (`proved`): the rule's test calls it by name with
  every parameter, from a state with every value, and so proves the method exists. Its spec named no value, and a
  test written from it had to make its own up.
- Their tests join the regression suite (`tests/unit/test_spec_act_<aggregate>_<action>.py`), so a later spec that
  refines an action is written knowing it and cannot break it unnoticed.
- An action still without a method afterwards fails by name. Nothing is stubbed.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from onboarding.action_protocol import shared_words, starting_state, starts_whole
from onboarding.router_engine import BusinessSpec
from onboarding.skeleton_builder import to_snake_case


@dataclass
class ActionBehaviour:
    """What implementing the manifest's actions delivered."""
    implemented: List[str] = field(default_factory=list)
    missing: List[Dict[str, str]] = field(default_factory=list)   # {action, aggregate, performed_by}, as the contract check reports
    runs: List[Dict[str, Any]] = field(default_factory=list)      # per spec: {aggregate, spec_id, status, error, attempts}
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


def action_specs(aggregate: str, actions: List[Dict[str, Any]], starting_state: str = "",
                 manifest: Optional[Dict[str, Any]] = None) -> List[BusinessSpec]:
    """Everything the application will ask this aggregate to do, one spec per action, after one for what a new
    object holds before any of it (the application shows a new object at once, so the class starts that way by
    itself). Each carries the words every writer of the class uses alike."""
    words = "".join(f"\n{line}" for line in shared_words(manifest, aggregate))
    specs = []
    if starting_state:
        specs.append(BusinessSpec(
            spec_id=f"SPEC-NEW-{aggregate.upper()}", title=f"A new {aggregate} is ready to use",
            description=(f"The application creates a {aggregate} and shows it at once, before any method is called "
                         f"on it." + words),
            given_when_then=(f"Given nothing but its required fields, When a {aggregate} is created and nothing is "
                             f"called on it, Then {starting_state.rstrip('.')}."),
            target_aggregate=aggregate, category="ACTION"))
    for action in actions:
        params = ", ".join(str(p) for p in action.get("params") or [])
        effect = str(action.get("description") or "the object carries out the action").strip().rstrip(".")
        specs.append(BusinessSpec(
            spec_id=f"SPEC-ACT-{aggregate.upper()}-{str(action['name']).upper()}",
            title=f"{aggregate} carries out {action['name']}",
            description=(f"The application calls this method on {aggregate} by exactly this name and these keyword "
                         f"arguments." + words),
            given_when_then=(f"Given a {aggregate} in the simplest state in which the action is allowed (arrange that "
                             f"by setting its fields), When `{action['name']}({params})` is called once with valid "
                             f"values, Then the object's fields show what the action does from that state. The action "
                             f"in full: {effect}. What it refuses, ignores or does from another state is proved by the "
                             f"other rules, each with a test of its own; this test is the one call."),
            target_aggregate=aggregate, category="ACTION"))
    return specs


def specs_of_actions(manifest: Optional[Dict[str, Any]], workspace_dir: str,
                     proved: Optional[Set[Tuple[str, str]]] = None) -> Tuple[List[BusinessSpec], List[Dict[str, Any]]]:
    """The specs of every action the manifest offers, and one run record per spec for the round to fill in. An
    action of a class the workspace does not have gets a run that says so and no spec. `proved` holds the
    (class, action) pairs a rule of the deck is about: those get no spec."""
    by_aggregate: Dict[str, List[Dict[str, Any]]] = {}
    for action in (manifest or {}).get("actions") or []:
        if isinstance(action, dict) and action.get("name") and action.get("aggregate"):
            waiting = by_aggregate.setdefault(str(action["aggregate"]), [])
            if (str(action["aggregate"]), str(action["name"])) not in (proved or set()):
                waiting.append(action)
    specs: List[BusinessSpec] = []
    runs: List[Dict[str, Any]] = []
    for aggregate, actions in by_aggregate.items():
        if not os.path.exists(os.path.join(workspace_dir, "src", "domain", f"{to_snake_case(aggregate)}.py")):
            runs.append({"aggregate": aggregate, "spec_id": "", "status": "NO_DOMAIN_CLASS",
                         "error": "the decomposition has no such class", "attempts": 0})
            continue
        start = "" if starts_whole(manifest, aggregate) else starting_state(manifest, aggregate)
        for spec in action_specs(aggregate, actions, start, manifest=manifest):
            specs.append(spec)
            runs.append({"aggregate": aggregate, "spec_id": spec.spec_id, "status": "", "error": "", "attempts": 0})
    return specs, runs
