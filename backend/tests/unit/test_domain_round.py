"""The domain is written in one round (backend/onboarding/domain_round.py, ADR-011).

A kickstart used to run the test loop twice: once for the actions' methods and, when those were written, once more
for the rule deck, whose code answer rewrote the class the first had just written. Both are known before either
starts (the action protocol names the actions, the deck holds the rules), so they are one batch: every first test is
written side by side, and each class gets one code answer for all of it.
"""
import os

from onboarding.action_behaviour import ActionBehaviour
from onboarding.domain_round import DomainRound, run_domain_round
from onboarding.router_engine import BusinessSpec, DomainStructureSchema, EntitySpec, SpecKind
from onboarding.skeleton_builder import build_and_write_skeleton

STRUCTURE = DomainStructureSchema(domain_name="Salon", entities=[
    EntitySpec(name="Appointment", is_aggregate_root=True, attributes=[
        {"name": "id", "type": "string"}, {"name": "status", "type": "string"}]),
    EntitySpec(name="Stylist", attributes=[{"name": "id", "type": "string"}, {"name": "name", "type": "string"}]),
])

MANIFEST = {
    "actions": [
        {"name": "confirm_booking", "aggregate": "Appointment", "performed_by": "audience",
         "params": ["guest_name"], "description": "The guest confirms the held slot"},
        {"name": "set_availability", "aggregate": "Stylist", "performed_by": "other", "params": ["available"],
         "description": "The salon marks a stylist as available or away"},
    ],
    "starting_states": [{"aggregate": "Appointment", "description": "status is 'held'"}],
}


def _rule(spec_id, kind=SpecKind.BEHAVIOR.value):
    return BusinessSpec(spec_id=spec_id, title=f"Rule {spec_id}", description="d", given_when_then="g",
                        target_aggregate="Appointment", kind=kind)


def _workspace(tmp_path):
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    return str(tmp_path)


def _loop(methods=(), failing=()):
    """A stand-in for the batch loop: writes `methods` (class, name) as GREEN would and settles every spec."""
    batches = []

    def execute(batch, done):
        batches.append([s.spec_id for s in batch])
        for aggregate, name in methods:
            with open(os.path.join(execute.workspace, "src", "domain", f"{aggregate.lower()}.py"), "a", encoding="utf-8") as f:
                f.write(f"\n    def {name}(self, **params):\n        self.status = '{name}'\n")
        for spec in batch:
            ok = spec.spec_id not in failing
            done(spec, {"success": ok, "status": "FULFILLED" if ok else "REQUIRES_HUMAN_INTERVENTION",
                        "error": "" if ok else "assert status == 'confirmed'", "attempts": [{"attempt": 1}]})

    execute.batches = batches
    return execute


def test_the_actions_and_the_rules_go_through_the_loop_as_one_batch(tmp_path):
    """Verify nothing waits for anything: the loop is called once, with every action's spec and every rule.

    id: TST-ROUND-ONE-BATCH
    Given: A manifest with an action on each of two classes and a starting state, and a deck of two rules the records
           obey with a rule of the page alone between them
    When: The domain round runs
    Then: The loop ran once; its batch holds what a new object holds, one spec per action, then the two rules; the
          page's rule is not in it
    """
    execute = _loop(methods=[("Appointment", "confirm_booking"), ("Stylist", "set_availability")])
    execute.workspace = _workspace(tmp_path)
    deck = [_rule("SPEC-001"), _rule("SPEC-002", SpecKind.PRESENTATION.value), _rule("SPEC-003")]

    done = run_domain_round(MANIFEST, deck, execute.workspace, execute)

    assert execute.batches == [["SPEC-NEW-APPOINTMENT", "SPEC-ACT-APPOINTMENT-CONFIRM_BOOKING",
                                "SPEC-ACT-STYLIST-SET_AVAILABILITY", "SPEC-001", "SPEC-003"]]
    assert isinstance(done, DomainRound) and isinstance(done.behaviour, ActionBehaviour)
    assert done.behaviour.success and sorted(done.behaviour.implemented) == ["confirm_booking", "set_availability"]
    assert done.specs.fulfilled == ["SPEC-001", "SPEC-003"] and done.specs.success


def test_only_the_rules_are_counted_and_stored_as_rules(tmp_path):
    """Verify the progress a person watches and the deck's stored results are about the deck's rules alone.

    id: TST-ROUND-RULES-ONLY
    Given: A round with three action specs and two rules
    When: It runs with a progress report and a place to store each rule's result
    Then: The progress counts two rules, and only the two rules were stored
    """
    execute = _loop(methods=[("Appointment", "confirm_booking"), ("Stylist", "set_availability")])
    execute.workspace = _workspace(tmp_path)
    progress, stored = [], []

    run_domain_round(MANIFEST, [_rule("SPEC-001"), _rule("SPEC-003")], execute.workspace, execute,
                     report=progress.append, on_rule=lambda spec, result: stored.append(spec.spec_id))

    assert (progress[0].total, progress[-1].done, progress[-1].active) == (2, 2, 2)
    assert stored == ["SPEC-001", "SPEC-003"]


def test_an_action_left_without_a_method_fails_by_name_and_the_rules_still_stand(tmp_path):
    """Verify a page action nothing implements is reported with the loop's own reason, beside the rules' outcome.

    id: TST-ROUND-MISSING
    Given: A loop that fulfils the rule but writes no method for Appointment's action, whose spec it fails
    When: The domain round runs
    Then: The behaviour is not a success, names the action and why its spec stopped; the rule is fulfilled
    """
    execute = _loop(methods=[("Stylist", "set_availability")], failing={"SPEC-ACT-APPOINTMENT-CONFIRM_BOOKING"})
    execute.workspace = _workspace(tmp_path)

    done = run_domain_round(MANIFEST, [_rule("SPEC-001")], execute.workspace, execute)

    assert not done.behaviour.success and [m["action"] for m in done.behaviour.missing] == ["confirm_booking"]
    assert "confirm_booking" in done.behaviour.error and "assert status == 'confirmed'" in done.behaviour.error
    assert done.behaviour.implemented == ["set_availability"] and done.specs.fulfilled == ["SPEC-001"]


def test_a_loop_that_crashes_fails_every_spec_with_the_reason(tmp_path):
    """Verify a provider error is reported on the actions and on the rules, and nothing is retried.

    id: TST-ROUND-CRASH
    Given: A loop that raises
    When: The domain round runs
    Then: The loop was called once, every action's run and every rule carry the error
    """
    calls = []

    def execute(batch, done):
        calls.append(1)
        raise RuntimeError("quota exceeded")

    done = run_domain_round(MANIFEST, [_rule("SPEC-001")], _workspace(tmp_path), execute)

    assert len(calls) == 1
    assert all("quota exceeded" in run["error"] for run in done.behaviour.runs) and len(done.behaviour.runs) == 3
    assert "quota exceeded" in done.specs.error and not done.behaviour.success


def test_a_product_without_rules_still_gets_its_actions(tmp_path):
    """Verify the actions are implemented when the deck has no rule the records obey.

    id: TST-ROUND-NO-RULES
    Given: A deck with only a rule of the page, and a manifest with actions
    When: The domain round runs
    Then: The loop ran with the actions' specs, and the rules are reported as skipped
    """
    execute = _loop(methods=[("Appointment", "confirm_booking"), ("Stylist", "set_availability")])
    execute.workspace = _workspace(tmp_path)

    done = run_domain_round(MANIFEST, [_rule("SPEC-002", SpecKind.PRESENTATION.value)], execute.workspace, execute)

    assert len(execute.batches) == 1 and len(execute.batches[0]) == 3
    assert done.behaviour.success and done.specs.skipped


def test_an_action_of_a_class_that_does_not_exist_is_reported_and_not_sent_to_the_loop(tmp_path):
    """Verify an action whose class the skeleton never built does not stop the others.

    id: TST-ROUND-NO-CLASS
    Given: A manifest with an action on a class the workspace does not have
    When: The domain round runs
    Then: That action's run says so, its spec is not in the batch, and the action is missing
    """
    execute = _loop(methods=[("Appointment", "confirm_booking"), ("Stylist", "set_availability")])
    execute.workspace = _workspace(tmp_path)
    manifest = {**MANIFEST, "actions": MANIFEST["actions"] + [
        {"name": "refund", "aggregate": "Payment", "performed_by": "other", "params": [], "description": "refunds"}]}

    done = run_domain_round(manifest, [], execute.workspace, execute)

    assert not any("PAYMENT" in spec_id for spec_id in execute.batches[0])
    assert [r["status"] for r in done.behaviour.runs if r["aggregate"] == "Payment"] == ["NO_DOMAIN_CLASS"]
    assert [m["action"] for m in done.behaviour.missing] == ["refund"]
