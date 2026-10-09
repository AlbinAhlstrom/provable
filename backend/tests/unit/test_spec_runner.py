"""The kickstart runs the rule deck's behaviour specs itself (backend/onboarding/spec_runner.py).

The actions' methods give an app its basic behaviour; the specs are its rules (a move must be legal, a stylist cannot
be double-booked). Left for the user to run one by one, a fresh app enforces none of them.
"""
from onboarding.router_engine import BusinessSpec, SpecKind
from onboarding.spec_runner import SpecRun, run_behaviour_specs


def _spec(spec_id, kind=SpecKind.BEHAVIOR.value):
    return BusinessSpec(spec_id=spec_id, title=f"Rule {spec_id}", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="Match", kind=kind)


def _each(answer):
    """An executor that settles the specs one by one with `answer(spec)`."""
    def execute(batch, done):
        for spec in batch:
            done(spec, answer(spec))
    return execute


def test_the_behaviour_specs_are_handed_over_together_in_deck_order():
    """Verify every behaviour spec reaches the executor in one batch, and presentation specs are left alone.

    id: TST-SPECRUN-001
    Given: Two behaviour specs with a presentation spec between them, and an executor that fulfils everything
    When: The specs are run
    Then: The executor was given the two behaviour specs at once, in order, and both are fulfilled
    """
    batches = []

    def execute(batch, done):
        batches.append([spec.spec_id for spec in batch])
        for spec in reversed(batch):
            done(spec, {"success": True, "status": "FULFILLED"})

    result = run_behaviour_specs([_spec("SPEC-001"), _spec("SPEC-002", SpecKind.PRESENTATION.value), _spec("SPEC-003")], execute)
    assert isinstance(result, SpecRun) and batches == [["SPEC-001", "SPEC-003"]]
    assert result.fulfilled == ["SPEC-001", "SPEC-003"] and result.unfulfilled == [] and result.success


def test_a_spec_that_does_not_reach_green_is_named_with_its_reason_and_the_rest_stand():
    """Verify one dead end neither hides itself nor takes the other specs with it.

    id: TST-SPECRUN-002
    Given: Three specs: the first dead-ends, the second is fulfilled, and the executor then raises (a provider
           error) before settling the third
    When: The specs are run
    Then: The second is fulfilled, and the result is a failure naming the other two with why each stopped
    """
    def execute(batch, done):
        done(batch[0], {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "error": "assert turn == 'Black'"})
        done(batch[1], {"success": True, "status": "FULFILLED"})
        raise RuntimeError("GREEN synthesis failed: quota")

    result = run_behaviour_specs([_spec("SPEC-001"), _spec("SPEC-002"), _spec("SPEC-003")], execute)
    assert result.fulfilled == ["SPEC-002"] and not result.success
    assert [u["spec_id"] for u in result.unfulfilled] == ["SPEC-001", "SPEC-003"]
    assert "SPEC-001" in result.error and "assert turn == 'Black'" in result.error and "quota" in result.error


def test_a_deck_without_behaviour_specs_is_skipped():
    """Verify nothing runs when there is no behaviour spec.

    id: TST-SPECRUN-003
    Given: Only a presentation spec
    When: The specs are run
    Then: The executor is never called and the result says why it was skipped
    """
    result = run_behaviour_specs([_spec("SPEC-001", SpecKind.PRESENTATION.value)], lambda batch, done: 1 / 0)
    assert result.success and result.skipped


def test_only_behaviour_specs_get_a_drafted_test():
    """Verify the tests written ahead are for the same specs the loop will run.

    id: TST-SPECRUN-DRAFT
    Given: Two behaviour specs with a presentation spec between them; and a deck with no behaviour spec
    When: Their tests are drafted
    Then: The writer is given the two behaviour specs and its answer is returned; for the other deck it is not called
    """
    from onboarding.spec_runner import draft_behaviour_tests

    seen = []

    def write(batch):
        seen.append([spec.spec_id for spec in batch])
        return {spec.spec_id: "test" for spec in batch}

    deck = [_spec("SPEC-001"), _spec("SPEC-002", SpecKind.PRESENTATION.value), _spec("SPEC-003")]
    assert draft_behaviour_tests(deck, write) == {"SPEC-001": "test", "SPEC-003": "test"}
    assert seen == [["SPEC-001", "SPEC-003"]]
    assert draft_behaviour_tests([_spec("SPEC-002", SpecKind.PRESENTATION.value)], lambda batch: 1 / 0) == {}
