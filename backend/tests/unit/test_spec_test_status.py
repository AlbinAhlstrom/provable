"""A rule's light comes from its page test and from nothing else (ADR-010)."""
from onboarding.spec_test_status import SpecTestStatus, derive_test_status, with_test_status
from service_layer import rule_tests, services
from service_layer.unit_of_work import FakeUnitOfWork

CARD = {"id": "S1", "title": "A rule", "card_type": "LOGIC", "target": "global", "status": "PENDING"}


def _ran(status, reason=None):
    return {"status": status, "reason": reason, "evidence": reason or "", "source": "def test_x(app): ..."}


def test_a_rule_whose_page_test_never_ran_is_not_run():
    """Verify a rule without a page test reports no outcome, whatever else is stored about it.

    id: TST-STATUS-001
    Given: A rule with nothing stored, one waiting, and one whose domain test passed in the kickstart
    When: The test status is derived
    Then: Each is not_run: a test of the domain class is no proof of a rule
    """
    for stored in (None, {"status": "PENDING"}, {"status": "FULFILLED", "tdd": {"phase": "COMMITTED"}},
                   {"status": "REQUIRES_HUMAN_INTERVENTION", "tdd": {"phase": "DEAD_END", "error": "not met"}}):
        assert derive_test_status(stored) == (SpecTestStatus.NOT_RUN, None)


def test_the_light_is_what_the_page_test_said():
    """Verify each outcome of a page test is shown as it is.

    id: TST-STATUS-002
    Given: Rules whose page test passed, failed and was broken
    When: The test status is derived
    Then: Pass carries no reason; fail and broken carry theirs
    """
    assert derive_test_status({"page_test": _ran("pass")}) == (SpecTestStatus.PASS, None)
    assert derive_test_status({"page_test": _ran("fail", "AssertionError: still enabled")}) == (
        SpecTestStatus.FAIL, "AssertionError: still enabled")
    assert derive_test_status({"page_test": _ran("broken", "Refused: 422")}) == (SpecTestStatus.BROKEN, "Refused: 422")


def test_a_domain_test_that_passed_does_not_turn_a_red_rule_green():
    """Verify the page test decides even when the kickstart fulfilled the rule.

    id: TST-STATUS-003
    Given: A rule fulfilled by the TDD loop whose page test failed
    When: The test status is derived
    Then: It fails
    """
    stored = {"status": "FULFILLED", "tdd": {"phase": "COMMITTED"}, "page_test": _ran("fail", "AssertionError: nothing happened")}
    assert derive_test_status(stored)[0] is SpecTestStatus.FAIL


def test_the_reason_is_one_line():
    """Verify a multi-line failure is cut to the line that says what went wrong.

    id: TST-STATUS-005
    Given: A reason spanning several lines with a blank first line
    When: The test status is derived
    Then: The reason is its first non-empty line
    """
    stored = {"page_test": _ran("fail", "\n  AssertionError: expected 3  \nCall log ...")}
    assert derive_test_status(stored)[1] == "AssertionError: expected 3"


def test_cards_get_their_status_without_changing_the_stored_card():
    """Verify a card's own page test, or the one stored with a spec of its id, becomes its status on a copy.

    id: TST-STATUS-006
    Given: A card carrying a failed page test, a card whose spec carries a passed one, and a card with neither
    When: with_test_status is applied
    Then: Each returned card carries test_status and test_reason; the input cards are untouched
    """
    failed = {**CARD, "page_test": _ran("fail", "not met")}
    by_spec, bare = {**CARD, "id": "S2"}, {**CARD, "id": "S3"}
    out = with_test_status([failed, by_spec, bare], [{"spec_id": "S2", "page_test": _ran("pass")}])
    assert [(c["id"], c["test_status"], c["test_reason"]) for c in out] == [
        ("S1", "fail", "not met"), ("S2", "pass", None), ("S3", "not_run", None)]
    assert "test_status" not in failed and "test_status" not in bare


def test_the_deck_serves_each_card_with_its_test_status():
    """Verify the Living Deck use case reports the outcome of a recorded page test on the card.

    id: TST-STATUS-007
    Given: A rule card, first with a domain test that passed, then with a recorded page test that passed
    When: The categorized deck is read each time
    Then: The card is not_run, then pass in every grouping
    """
    uow = FakeUnitOfWork()
    services.add_rule_card(dict(CARD), uow=uow)
    services.record_tdd_result("S1", {"success": True, "status": "FULFILLED", "phase": "COMMITTED"}, uow=uow)
    assert services.get_categorized_living_deck(uow=uow)["all_cards"][0]["test_status"] == "not_run"

    rule_tests.record_page_test("S1", _ran("pass"), uow=uow)
    deck = services.get_categorized_living_deck(uow=uow)
    assert deck["all_cards"][0]["test_status"] == "pass"
    assert deck["chapters"]["General"][0]["test_status"] == "pass"
    assert deck["logic_cards"]["global"][0]["test_status"] == "pass"
