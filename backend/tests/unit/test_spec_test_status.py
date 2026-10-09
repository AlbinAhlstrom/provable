import pytest

from onboarding.spec_test_status import SpecTestStatus, derive_test_status, with_test_status
from service_layer import services
from service_layer.unit_of_work import FakeUnitOfWork

CARD = {"id": "S1", "title": "A rule", "card_type": "LOGIC", "target": "global", "status": "PENDING"}


def _stored(status, phase=None, error=None):
    return {"spec_id": "S1", "status": status, "tdd": {"phase": phase, "error": error}}


def test_a_spec_nobody_ran_is_not_run():
    """Verify a spec without a stored result, or one only waiting, reports no test outcome.

    id: TST-STATUS-001
    Given: No stored spec, a pending one and a paused one
    When: The test status is derived
    Then: Each is not_run and carries no reason
    """
    for stored in (None, {"spec_id": "S1", "status": "PENDING"}, {"spec_id": "S1", "status": "PAUSED"},
                   {"spec_id": "S1", "status": "IN_PROGRESS"}):
        assert derive_test_status(stored) == (SpecTestStatus.NOT_RUN, None)


def test_a_fulfilled_spec_passes():
    """Verify a fulfilled spec is a pass whichever loop proved it.

    id: TST-STATUS-002
    Given: A behaviour spec committed by the TDD loop and a presentation spec whose view built
    When: The test status is derived
    Then: Both pass, with no reason
    """
    for phase in ("COMMITTED", "presentation"):
        assert derive_test_status(_stored("FULFILLED", phase)) == (SpecTestStatus.PASS, None)


def test_a_rejected_change_fails_with_the_verdict_as_reason():
    """Verify a spec whose test ran and was not met is a fail.

    id: TST-STATUS-003
    Given: A spec the verifying step rejected after its one retry (phase DEAD_END)
    When: The test status is derived
    Then: It fails and the reason is the verdict
    """
    stored = _stored("REQUIRES_HUMAN_INTERVENTION", "DEAD_END", "Test assertions failed in GREEN phase: 1 failed")
    assert derive_test_status(stored) == (SpecTestStatus.FAIL, "Test assertions failed in GREEN phase: 1 failed")


@pytest.mark.parametrize("status, phase", [
    ("REQUIRES_HUMAN_INTERVENTION", "RED_GATE"),         # the test itself was rejected, or the domain does not import
    ("REQUIRES_HUMAN_INTERVENTION", "REGRESSION_GATE"),  # the regression suite did not finish
    ("REQUIRES_HUMAN_INTERVENTION", "presentation"),     # no view to change, provider or parse error
    ("ERROR", "RED_GEN"), ("ERROR", "GREEN_GEN"), ("ERROR", None),
])
def test_a_run_that_could_not_judge_the_spec_is_broken(status, phase):
    """Verify a run that never reached a verdict on the behaviour is broken, not a fail.

    id: TST-STATUS-004
    Given: Runs that ended before the change was judged
    When: The test status is derived
    Then: Each is broken and keeps its reason
    """
    assert derive_test_status(_stored(status, phase, "why")) == (SpecTestStatus.BROKEN, "why")


def test_the_reason_is_one_line():
    """Verify a multi-line failure is cut to the line that says what went wrong.

    id: TST-STATUS-005
    Given: A reason spanning several lines with a blank first line
    When: The test status is derived
    Then: The reason is its first non-empty line
    """
    stored = _stored("REQUIRES_HUMAN_INTERVENTION", "DEAD_END", "\n  AssertionError: expected 3  \nTraceback ...")
    assert derive_test_status(stored)[1] == "AssertionError: expected 3"


def test_cards_get_their_status_without_changing_the_stored_card():
    """Verify cards are joined with stored results by id and returned as copies.

    id: TST-STATUS-006
    Given: Two cards, one with a stored failing result
    When: with_test_status is applied
    Then: Each returned card carries test_status and test_reason; the input cards are untouched
    """
    other = {**CARD, "id": "S2"}
    out = with_test_status([CARD, other], [_stored("REQUIRES_HUMAN_INTERVENTION", "DEAD_END", "not met")])
    assert [(c["id"], c["test_status"], c["test_reason"]) for c in out] == [("S1", "fail", "not met"), ("S2", "not_run", None)]
    assert "test_status" not in CARD and "test_status" not in other


def test_the_deck_serves_each_card_with_its_test_status():
    """Verify the Living Deck use case reports the outcome of a recorded run on the card.

    id: TST-STATUS-007
    Given: A rule card and a recorded run that passed
    When: The categorized deck is read
    Then: The card carries test_status pass in every grouping, and the stored card is unchanged
    """
    uow = FakeUnitOfWork()
    services.add_rule_card(dict(CARD), uow=uow)
    services.record_tdd_result("S1", {"success": True, "status": "FULFILLED", "phase": "COMMITTED"}, uow=uow)
    deck = services.get_categorized_living_deck(uow=uow)
    assert deck["all_cards"][0]["test_status"] == "pass"
    assert deck["chapters"]["General"][0]["test_status"] == "pass"
    assert deck["logic_cards"]["global"][0]["test_status"] == "pass"
    assert "test_status" not in services.get_living_deck(uow=uow)[0]
