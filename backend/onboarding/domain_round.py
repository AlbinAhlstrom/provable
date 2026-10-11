"""
The domain round: a kickstart writes the actions' methods and the rule deck's rules in one pass of the test loop.

There used to be two passes. The actions' methods were written first (one test and one code answer per class), and
when they existed the rule deck ran through the loop again: its tests were judged against the class the first pass
left, and its code answer rewrote that class. The second pass could not start before the first had finished, and
together they were most of a kickstart's duration.

Nothing in the second depends on the first. The action protocol names every action with its parameters and what it
changes, and the deck holds every rule, before either pass starts. So they are one batch
(`service_layer/tdd_batch.py`):

- Every first test is written side by side: what a new object holds, one test per action, one per rule. Each writer
  is shown the others of its class, so no two arrange the same situation differently.
- Each class gets one code answer for all of it, judged test by test, with the loop's one retry.
- Afterwards the code is compared with the action protocol (`check_action_contract`): an action still without a
  method fails by name. Nothing is stubbed.

Only the deck's rules are counted as rules (the progress a person watches) and stored as rules (`on_rule`); the
actions' specs are the round's own.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from onboarding.action_behaviour import ActionBehaviour, specs_of_actions
from onboarding.action_protocol import check_action_contract
from onboarding.router_engine import BusinessSpec
from onboarding.spec_runner import RuleProgress, SpecRun, behaviour_rules, run_behaviour_specs
from pipeline_trace import traced

Settle = Callable[[BusinessSpec, Dict[str, Any]], None]
Execute = Callable[[List[BusinessSpec], Settle], Any]


@dataclass
class DomainRound:
    """What the round delivered: the methods behind the actions, and which rules the app now enforces."""
    behaviour: ActionBehaviour = field(default_factory=ActionBehaviour)
    specs: SpecRun = field(default_factory=SpecRun)


@traced("domain.round")
def run_domain_round(manifest: Optional[Dict[str, Any]], deck: List[BusinessSpec], workspace_dir: str, execute: Execute,
                     report: Optional[Callable[[RuleProgress], None]] = None,
                     on_rule: Optional[Settle] = None) -> DomainRound:
    """Hands the actions' specs and the deck's behaviour rules to `execute` (the TDD batch) as one batch. `execute`
    tells its second argument each spec's result as it is settled. `report` is told how far the rules have come;
    `on_rule` is told each rule's result (the caller owns where it is stored)."""
    actions, runs = specs_of_actions(manifest, workspace_dir)
    run_of = {run["spec_id"]: run for run in runs if run["spec_id"]}

    def settle_action(spec: BusinessSpec, result: Dict[str, Any]) -> None:
        run_of[spec.spec_id].update(status=str(result.get("status") or ""), error=str(result.get("error") or ""),
                                    attempts=len(result.get("attempts") or []))

    def together(rules: List[BusinessSpec], settle_rule: Settle) -> None:
        def settled(spec: BusinessSpec, result: Dict[str, Any]) -> None:
            if spec.spec_id in run_of:
                return settle_action(spec, result)
            if on_rule is not None:
                on_rule(spec, result)
            settle_rule(spec, result)

        try:
            execute(actions + rules, settled)
        except Exception as err:  # a provider or infrastructure error: reported with its reason, never retried
            for run in run_of.values():
                if not run["status"]:
                    run.update(status="ERROR", error=f"{type(err).__name__}: {err}")
            raise

    done = DomainRound(behaviour=ActionBehaviour(runs=runs))
    if behaviour_rules(deck):
        done.specs = run_behaviour_specs(deck, together, report=report)  # a crash is kept on every rule it left open
    else:
        done.specs = SpecRun(skipped="the deck has no behaviour spec")
        if actions:
            try:
                together([], lambda spec, result: None)
            except Exception:
                pass  # kept on every action's run above
    if not runs:
        done.behaviour.skipped = "the action protocol offers no action"
        return done
    contract = check_action_contract(workspace_dir, manifest)
    done.behaviour.implemented, done.behaviour.missing = contract["implemented"], contract["missing"]
    return done
