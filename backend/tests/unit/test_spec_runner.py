"""The kickstart runs the rule deck's behaviour specs itself (backend/onboarding/spec_runner.py).

The actions' methods give an app its basic behaviour; the specs are its rules (a move must be legal, a stylist cannot
be double-booked). Left for the user to run one by one, a fresh app enforces none of them.
"""
from onboarding.router_engine import BusinessSpec, SpecKind
from onboarding.spec_runner import SpecRun, run_behaviour_specs


def _spec(spec_id, kind=SpecKind.BEHAVIOR.value):
    return BusinessSpec(spec_id=spec_id, title=f"Rule {spec_id}", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="Match", kind=kind)


def test_behaviour_specs_run_one_after_another_in_deck_order():
    """Verify every behaviour spec goes through the executor, in order, and presentation specs are left alone.

    id: TST-SPECRUN-001
    Given: Two behaviour specs with a presentation spec between them, and an executor that fulfils everything
    When: The specs are run
    Then: The executor saw the two behaviour specs in order and both are fulfilled
    """
    seen = []

    def execute(spec):
        seen.append(spec.spec_id)
        return {"success": True, "status": "FULFILLED"}

    result = run_behaviour_specs([_spec("SPEC-001"), _spec("SPEC-002", SpecKind.PRESENTATION.value), _spec("SPEC-003")], execute)
    assert isinstance(result, SpecRun) and seen == ["SPEC-001", "SPEC-003"]
    assert result.fulfilled == ["SPEC-001", "SPEC-003"] and result.unfulfilled == [] and result.success


def test_a_spec_that_does_not_reach_green_is_named_with_its_reason_and_the_rest_still_run():
    """Verify one dead end neither hides itself nor stops the specs after it.

    id: TST-SPECRUN-002
    Given: Three specs: the first dead-ends, the second's executor raises (a provider error), the third is fulfilled
    When: The specs are run
    Then: The third is fulfilled, and the result is a failure naming the other two with why each stopped
    """
    def execute(spec):
        if spec.spec_id == "SPEC-001":
            return {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "error": "assert turn == 'Black'"}
        if spec.spec_id == "SPEC-002":
            raise RuntimeError("RED test generation failed: quota")
        return {"success": True, "status": "FULFILLED"}

    result = run_behaviour_specs([_spec("SPEC-001"), _spec("SPEC-002"), _spec("SPEC-003")], execute)
    assert result.fulfilled == ["SPEC-003"] and not result.success
    assert [u["spec_id"] for u in result.unfulfilled] == ["SPEC-001", "SPEC-002"]
    assert "SPEC-001" in result.error and "assert turn == 'Black'" in result.error and "quota" in result.error


def test_a_deck_without_behaviour_specs_is_skipped():
    """Verify nothing runs when there is no behaviour spec.

    id: TST-SPECRUN-003
    Given: Only a presentation spec
    When: The specs are run
    Then: The executor is never called and the result says why it was skipped
    """
    result = run_behaviour_specs([_spec("SPEC-001", SpecKind.PRESENTATION.value)], lambda spec: 1 / 0)
    assert result.success and result.skipped
