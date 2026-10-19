"""
The domain round: a kickstart writes the actions' methods and the rule deck's rules in one pass of the test loop.

There used to be two passes. The actions' methods were written first (one test and one code answer per class), and
when they existed the rule deck ran through the loop again: its tests were judged against the class the first pass
left, and its code answer rewrote that class. The second pass could not start before the first had finished, and
together they were most of a kickstart's duration.

Nothing in the second depends on the first. The action protocol names every action with its parameters and what it
changes, and the deck holds every rule, before either pass starts. So they are one batch
(`service_layer/tdd_batch.py`):

- The first tests of a class are written in one answer (`first_tests.py`): what a new object holds, one test per
  rule, and one per action that no rule is about. They share one builder for each situation the contract wrote,
  so no two arrange the same situation differently.
- Each class gets one code answer for all of it, judged test by test, with the loop's one retry.
- A class's refusals are written by code before anything else, each with the contract's sentence fixed inside it
  (`action_protocol.write_refusals`): the code raises them and the page shows the sentence as the contract wrote it.
- Afterwards the code is compared with the action protocol (`check_action_contract`): an action still without a
  method fails by name. Nothing is stubbed.

Only the deck's rules are counted as rules (the progress a person watches) and stored as rules (`on_rule`); the
actions' specs are the round's own.

The running app keeps the records made while the app was built (`skeleton_builder.forget_saved_records`): the preview
opens during the build and makes its first record with the class the skeleton wrote, which knows nothing of the
starting state the round gives it. What was saved under a class the round changed is removed when the round ends, and
the class's file is marked changed after that, so the running API restarts without what it held in memory.
"""

import os

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from onboarding.action_behaviour import ActionBehaviour, specs_of_actions
from onboarding.action_protocol import check_action_contract, write_refusals
from onboarding.router_engine import BusinessSpec
from onboarding.skeleton_builder import forget_saved_records
from onboarding.spec_runner import RuleProgress, SpecRun, behaviour_rules, run_behaviour_specs
from pipeline_trace import traced

Settle = Callable[[BusinessSpec, Dict[str, Any]], None]
Execute = Callable[[List[BusinessSpec], Settle], Any]


@dataclass
class DomainRound:
    """What the round delivered: the methods behind the actions, and which rules the app now enforces."""
    behaviour: ActionBehaviour = field(default_factory=ActionBehaviour)
    specs: SpecRun = field(default_factory=SpecRun)


def _class_sources(workspace_dir: str) -> Dict[str, str]:
    folder = os.path.join(workspace_dir, "src", "domain")
    if not os.path.isdir(folder):
        return {}
    sources = {}
    for name in os.listdir(folder):
        if name.endswith(".py"):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                sources[name] = f.read()
    return sources


def _forget_records_of_changed_classes(workspace_dir: str, before: Dict[str, str]) -> None:
    folder = os.path.join(workspace_dir, "src", "domain")
    for name, source in _class_sources(workspace_dir).items():
        if before.get(name) != source and forget_saved_records(workspace_dir, name[:-len(".py")]):
            os.utime(os.path.join(folder, name))  # the running API restarts and reads nothing saved


@traced("domain.round")
def run_domain_round(manifest: Optional[Dict[str, Any]], deck: List[BusinessSpec], workspace_dir: str, execute: Execute,
                     report: Optional[Callable[[RuleProgress], None]] = None,
                     on_rule: Optional[Settle] = None) -> DomainRound:
    """Hands the actions' specs and the deck's behaviour rules to `execute` (the TDD batch) as one batch. `execute`
    tells its second argument each spec's result as it is settled. `report` is told how far the rules have come;
    `on_rule` is told each rule's result (the caller owns where it is stored)."""
    before = _class_sources(workspace_dir)
    try:
        return _round(manifest, deck, workspace_dir, execute, report, on_rule)
    finally:
        _forget_records_of_changed_classes(workspace_dir, before)


def _round(manifest: Optional[Dict[str, Any]], deck: List[BusinessSpec], workspace_dir: str, execute: Execute,
           report: Optional[Callable[[RuleProgress], None]], on_rule: Optional[Settle]) -> DomainRound:
    write_refusals(manifest, workspace_dir)  # the contract's refusals, each with its sentence, before any test or code
    proved = {(spec.target_aggregate, spec.action) for spec in behaviour_rules(deck) if spec.action}
    actions, runs = specs_of_actions(manifest, workspace_dir, proved=proved)
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
    if not runs and not proved:  # an action a rule proves has no run, and is checked against the code all the same
        done.behaviour.skipped = "the action protocol offers no action"
        return done
    contract = check_action_contract(workspace_dir, manifest)
    done.behaviour.implemented, done.behaviour.missing = contract["implemented"], contract["missing"]
    return done
