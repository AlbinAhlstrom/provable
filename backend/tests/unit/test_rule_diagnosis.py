"""Where the fault of a red rule lies is found before anything is changed (onboarding/rule_diagnosis.py)."""
import copy
import json
import os

import pytest

import agent_orchestrator
from onboarding import product_contract as pc
from onboarding import rule_diagnosis as rd
from test_product_contract import CONTRACT

BOOKING = '''from dataclasses import dataclass


@dataclass
class Booking:
    """A booking."""
    id: str
    guests: int = 2
    status: str = "confirmed"

    def create_booking(self, table_id: str, guests: int) -> None:
        """Book a table."""
        self._check(guests)
        self.status = "confirmed"

    def expire_hold(self) -> None:
        self.status = "cancelled"

    def _check(self, guests: int) -> None:
        if guests > self._most():
            raise ValueError(guests)

    def _most(self) -> int:
        return 8

    def _unused(self) -> int:
        return 0
'''
RULE = {"spec_id": "SPEC-001", "title": "A booking holds its table", "action": "create_booking",
        "target_aggregate": "Booking",
        "given_when_then": "Given two_tables_free, When create_booking(table_id of Table 1, guests 2), Then a Booking "
                           "with status confirmed",
        "situation": "`two_tables_free`: two tables and nobody has booked"}
STORED = {"status": "fail", "reason": "AssertionError: Locator expected to be visible", "evidence": "waiting for Table 1",
          "seen": "POST /api/bookings/action answered 200", "source": "def test_booking(app): ..."}


def _contract() -> pc.ProductContract:
    return pc.ProductContract.from_dict(copy.deepcopy(CONTRACT))


def _workspace(tmp_path, unit_test: str = "") -> str:
    os.makedirs(tmp_path / "src" / "domain")
    os.makedirs(tmp_path / "tests" / "unit")
    (tmp_path / "src" / "domain" / "booking.py").write_text(BOOKING, encoding="utf-8")
    if unit_test:
        (tmp_path / "tests" / "unit" / "test_spec_001.py").write_text(unit_test, encoding="utf-8")
    return str(tmp_path)


def test_an_action_is_shown_as_its_method_and_the_methods_it_calls():
    """
    Given: A class with an action that calls a helper, which calls another, and methods the action never reaches
    When: The action is cut out of the class
    Then: The action and the helpers it reaches are shown whole, and nothing else of the class
    """
    shown = rd.method_with_helpers(BOOKING, "create_booking")

    assert "def create_booking" in shown and "def _check" in shown and "def _most" in shown
    assert "def expire_hold" not in shown and "def _unused" not in shown
    assert rd.method_with_helpers(BOOKING, "no_such_action") == ""


def test_the_case_holds_what_the_plan_says_the_method_the_unit_test_and_the_other_rules(tmp_path):
    """
    Given: A red rule about an action, the contract the app was built from and the app's files
    When: The case for its diagnosis is put together
    Then: It holds the rule with its situation, what the test saw, what the plan says the action does, the method,
          the rule's unit test, and the other rules about the same action with the situations they start from;
          a rule about another action or of the page alone is not among them
    """
    workspace = _workspace(tmp_path, unit_test="def test_booking():\n    assert True\n")

    case = rd.case_of(RULE, STORED, _contract(), workspace, run_unit_test=lambda path: "it passes")

    assert case.title == "A booking holds its table" and "two_tables_free" in case.situation
    assert (case.reason, case.seen, case.test) == (STORED["reason"], STORED["seen"], STORED["source"])
    assert "create_booking(table_id: text, guests: whole_number)" in case.action
    assert "creates a Booking with status confirmed" in case.action
    assert "def create_booking" in case.method and "def expire_hold" not in case.method
    assert (case.unit_test, case.unit_test_said) == ("def test_booking():\n    assert True\n", "it passes")
    assert len(case.others) == 1 and case.others[0].startswith("- No more than eight guests: Given `two_tables_free`: two tables")
    assert "TooManyGuestsError, nothing changes" in case.others[0]


def test_a_rule_of_the_page_alone_is_the_pages_fault_and_nothing_is_asked(tmp_path):
    """
    Given: A red rule that names no action
    When: It is diagnosed
    Then: The fault is the page's, and no model was asked
    """
    asked = []
    rule = {**RULE, "action": ""}

    diagnosis = rd.diagnose_rule(rule, STORED, _contract(), _workspace(tmp_path), ask=lambda case: asked.append(case))

    assert diagnosis.fault == rd.PAGE and asked == []


def test_the_diagnosis_is_one_call_held_to_its_schema(monkeypatch, tmp_path):
    """
    Given: A model that works each rule through against the plan, finds one that does not hold, and names another
           fault all the same
    When: A case is diagnosed
    Then: One call was made for the stage `rule_diagnosis` with the diagnosis schema, its prompt holds the method and
          what the app held, and the fault is the rules', with the rule that does not hold named
    """
    calls = []
    answer = {"checked": [{"rule": "A booking holds its table", "closing": "none", "leaves": "confirmed", "holds": True},
                          {"rule": "No more than eight guests", "closing": "none", "leaves": "refused", "holds": False}],
              "fault": "logic", "why": "One rule keeps the booking open after the action that settles it."}
    monkeypatch.setattr(agent_orchestrator, "call_gemini",
                        lambda prompt, stage="general", **k: calls.append((prompt, stage, k)) or json.dumps(answer))
    case = rd.case_of(RULE, STORED, _contract(), _workspace(tmp_path), run_unit_test=lambda path: "it passes")

    diagnosis = rd.diagnose(case)

    (prompt, stage, options), = calls
    assert stage == "rule_diagnosis" and options["json_schema"] is rd.DIAGNOSIS_SCHEMA
    assert "def create_booking" in prompt and STORED["seen"] in prompt and "No more than eight guests" in prompt
    assert (diagnosis.fault, diagnosis.rules) == (rd.RULES, ["No more than eight guests"])
    assert diagnosis.why.startswith("One rule keeps")


@pytest.mark.parametrize("raw, reason", [
    ("", "APITimeoutError"),
    ("not json", "not valid JSON"),
    ('{"checked": [], "fault": "weather", "why": "x"}', "weather"),
])
def test_a_diagnosis_that_was_not_delivered_fails_with_the_reason(monkeypatch, tmp_path, raw, reason):
    """
    Given: A provider that answers nothing, something that is no JSON, or a fault that is none of the four
    When: A case is diagnosed
    Then: It fails by name with the reason, after one call
    """
    calls = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: calls.append(1) or raw)
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", "APITimeoutError: timed out", raising=False)
    case = rd.case_of(RULE, STORED, None, _workspace(tmp_path), run_unit_test=lambda path: "")

    with pytest.raises(rd.NoDiagnosis, match=reason):
        rd.diagnose(case)
    assert len(calls) == 1
