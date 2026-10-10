"""Running a rule's page test from the Studio: one rule, or every rule of the deck (ADR-010). A run changes no code."""
from service_layer import rule_tests
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services

CARD = {"id": "SPEC-001", "title": "A sent order is locked", "card_type": "LOGIC", "target": "Order", "is_active": True,
        "given_clause": "a sent order", "when_clause": "the customer opens it", "then_clause": "its lines cannot be changed"}


def _deck(*cards):
    uow = FakeUnitOfWork()
    for card in cards:
        services.add_rule_card(dict(card), uow=uow)
    return uow


class _Prover:
    def __init__(self, status="pass", reason=None):
        self.calls, self.status, self.reason = [], status, reason

    def __call__(self, rule, workspace_dir, page_url, stored=None, app=None):
        self.calls.append({"rule": rule, "stored": stored, "page_url": page_url})
        return {"status": self.status, "reason": self.reason, "evidence": "", "source": "def test_x(app): ...",
                "written_for": "x", "written": 0 if stored else 1}


def test_running_a_rule_stores_what_its_page_test_said():
    """
    Given: A deck with one rule and a page test that fails
    When: The rule's test is run
    Then: The outcome is returned and stored on the rule with the time it ran, and the rule itself is unchanged
    """
    uow, prover = _deck(CARD), _Prover("fail", "AssertionError: still enabled")
    result = rule_tests.run_rule_test("SPEC-001", uow=uow, workspace_dir="ws", page_url="http://page", prove=prover)

    assert (result["status"], result["reason"]) == ("fail", "AssertionError: still enabled")
    card = services.get_living_deck(uow=uow)[0]
    assert card["page_test"]["status"] == "fail" and card["page_test"]["ran_at"]
    assert card["status"] == "ACTIVE" or card["status"] == "PENDING"
    assert prover.calls[0]["rule"]["then_clause"] == "its lines cannot be changed"
    assert prover.calls[0]["page_url"] == "http://page"


def test_a_second_run_hands_the_stored_test_back():
    """
    Given: A rule whose page test ran before
    When: It is run again
    Then: The prover is given the stored test, so it is run again and not written again
    """
    uow, prover = _deck(CARD), _Prover()
    rule_tests.run_rule_test("SPEC-001", uow=uow, workspace_dir="ws", page_url="p", prove=prover)
    rule_tests.run_rule_test("SPEC-001", uow=uow, workspace_dir="ws", page_url="p", prove=prover)
    assert prover.calls[0]["stored"] is None
    assert prover.calls[1]["stored"]["source"] == "def test_x(app): ..."


def test_a_test_that_is_itself_wrong_can_be_written_again():
    """
    Given: A rule whose page test ran before
    When: It is run with a rewrite asked for
    Then: The prover is given no stored test, so a new one is written
    """
    uow, prover = _deck(CARD), _Prover()
    rule_tests.run_rule_test("SPEC-001", uow=uow, workspace_dir="ws", page_url="p", prove=prover)
    rule_tests.run_rule_test("SPEC-001", uow=uow, workspace_dir="ws", page_url="p", prove=prover, rewrite=True)
    assert prover.calls[1]["stored"] is None


def test_a_rule_known_only_to_the_inbox_is_run_and_stored_there():
    """
    Given: A spec added to the inbox that has no card in the deck
    When: Its test is run
    Then: The outcome is stored with the spec
    """
    uow, prover = FakeUnitOfWork(), _Prover()
    services.add_inbox_spec({"spec_id": "SPEC-900", "title": "t", "given_when_then": "Given a When b Then c", "status": "PENDING"}, uow=uow)
    rule_tests.run_rule_test("SPEC-900", uow=uow, workspace_dir="ws", page_url="p", prove=prover)
    assert services.get_inbox_specs(uow=uow)[0]["page_test"]["status"] == "pass"
    assert prover.calls[0]["rule"]["given_when_then"] == "Given a When b Then c"


def test_an_unknown_rule_is_reported_and_nothing_runs():
    """
    Given: An empty deck
    When: A rule's test is run
    Then: The answer says the rule was not found
    """
    prover = _Prover()
    result = rule_tests.run_rule_test("SPEC-404", uow=FakeUnitOfWork(), workspace_dir="ws", page_url="p", prove=prover)
    assert (result["status"], prover.calls) == ("not_found", [])


def test_running_the_deck_runs_every_active_rule_and_counts_the_outcomes():
    """
    Given: A deck with three rules, one of them paused
    When: Every rule's test is run
    Then: The two active rules are run and stored, and the counts say how they ended
    """
    paused = {**CARD, "id": "SPEC-003", "is_active": False}
    uow = _deck(CARD, {**CARD, "id": "SPEC-002"}, paused)
    outcomes = {"SPEC-001": "pass", "SPEC-002": "fail"}

    def prover(rule, workspace_dir, page_url, stored=None, app=None):
        return {"status": outcomes[rule["id"]], "reason": None, "evidence": "", "source": "s", "written_for": "x", "written": 1}

    result = rule_tests.run_all_rule_tests(uow=uow, workspace_dir="ws", page_url="p", prove=prover, describe=lambda ws, url: None)

    assert result["counts"] == {"pass": 1, "fail": 1, "broken": 0}
    assert [r["spec_id"] for r in result["rules"]] == ["SPEC-001", "SPEC-002"]
    stored = {c["id"]: (c.get("page_test") or {}).get("status") for c in services.get_living_deck(uow=uow)}
    assert stored == {"SPEC-001": "pass", "SPEC-002": "fail", "SPEC-003": None}


def test_a_rule_whose_run_crashes_is_broken_and_the_others_still_run():
    """
    Given: A deck with two rules and a prover that raises on the first
    When: Every rule's test is run
    Then: The first is stored as broken with the error, the second with its own outcome
    """
    uow = _deck(CARD, {**CARD, "id": "SPEC-002"})

    def prover(rule, workspace_dir, page_url, stored=None, app=None):
        if rule["id"] == "SPEC-001":
            raise OSError("no browser")
        return {"status": "pass", "reason": None, "evidence": "", "source": "s", "written_for": "x", "written": 1}

    result = rule_tests.run_all_rule_tests(uow=uow, workspace_dir="ws", page_url="p", prove=prover, describe=lambda ws, url: None)
    by_id = {r["spec_id"]: r for r in result["rules"]}
    assert (by_id["SPEC-001"]["status"], by_id["SPEC-002"]["status"]) == ("broken", "pass")
    assert "no browser" in by_id["SPEC-001"]["reason"]


# ── fixing a red rule ────────────────────────────────────────────────────────

def _deck_with_lights(lights):
    """A deck of rules whose page tests ended as given (rule id -> status)."""
    uow = _deck(*[{**CARD, "id": spec_id} for spec_id in lights])
    for spec_id, status in lights.items():
        if status:
            rule_tests.record_page_test(spec_id, {"status": status, "reason": "r", "evidence": "e", "source": f"test of {spec_id}",
                                                  "written_for": "x"}, uow=uow)
    return uow


def test_fixing_a_red_rule_hands_the_fixer_the_green_tests_and_stores_the_new_light():
    """
    Given: A deck with one red rule, two green ones and one that never ran
    When: The red rule is fixed and the fixer reports a kept change
    Then: The fixer was given the red rule's stored test and the two green tests to guard, the rule's test was run
          again and its light is stored green, and the answer names the changed files
    """
    uow = _deck_with_lights({"SPEC-001": "fail", "SPEC-002": "pass", "SPEC-003": "pass", "SPEC-004": None})
    seen = {}

    def fixer(rule, stored, workspace_dir, page_url, green):
        seen.update(rule=rule, stored=stored, green=green)
        return {"status": "fixed", "reason": None, "files": ["src/App.tsx"], "attempts": [{"number": 1, "ok": True}]}

    result = rule_tests.fix_rule_test("SPEC-001", uow=uow, workspace_dir="ws", page_url="p", fixer=fixer, prove=_Prover("pass"))

    assert (result["success"], result["status"], result["files"]) == (True, "fixed", ["src/App.tsx"])
    assert seen["stored"]["status"] == "fail" and seen["rule"]["spec_id"] == "SPEC-001"
    assert seen["green"] == {"SPEC-002": "test of SPEC-002", "SPEC-003": "test of SPEC-003"}
    lights = {c["id"]: (c.get("page_test") or {}).get("status") for c in services.get_living_deck(uow=uow)}
    assert lights["SPEC-001"] == "pass"


def test_a_fix_that_was_not_kept_leaves_the_light_red():
    """
    Given: A red rule and a fixer whose changes were rejected
    When: The rule is fixed
    Then: The answer says why, and the rule's stored test and light are as they were
    """
    uow = _deck_with_lights({"SPEC-001": "fail"})
    prover = _Prover("pass")

    def fixer(rule, stored, workspace_dir, page_url, green):
        return {"status": "not_fixed", "reason": "the page does not build", "files": [], "attempts": []}

    result = rule_tests.fix_rule_test("SPEC-001", uow=uow, workspace_dir="ws", page_url="p", fixer=fixer, prove=prover)

    assert (result["success"], result["reason"]) == (False, "the page does not build")
    assert services.get_living_deck(uow=uow)[0]["page_test"]["status"] == "fail" and prover.calls == []


def test_fixing_an_unknown_rule_is_reported():
    """
    Given: An empty deck
    When: A fix is asked for
    Then: The answer says the rule was not found
    """
    result = rule_tests.fix_rule_test("SPEC-404", uow=FakeUnitOfWork(), workspace_dir="ws", page_url="p", fixer=None)
    assert result["status"] == "not_found"
