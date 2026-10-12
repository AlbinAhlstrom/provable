"""A test proves its own arrangement before it acts (the RED gate's Given check).

A test writer planned one state, typed another (two coordinates swapped in the data), and expected what the planned
state gives. On a class without behaviour every test fails, so the gate let it through and the first reader able to
notice was the code writer. The writer now asserts the facts its expectation rests on, each with a message that
begins "Given:", and the run the gate already makes stops a test whose arrangement is not the one it states.
"""
import os

import pytest

from onboarding.router_engine import BusinessSpec
from service_layer import tdd_machine

HALL = '''from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Hall:
    id: str
    seats: List[Dict[str, Any]] = field(default_factory=list)
'''

# The plan in the comment and the expectation agree (row 3 is full); the data puts the taken seats in number 3
SWAPPED = '''from src.domain.hall import Hall

TAKEN = {(number, 3) for number in range(1, 5)}


def test_a_full_row_is_closed():
    hall = Hall(id="h1")
    hall.seats = [{"row": row, "number": number, "taken": (row, number) in TAKEN}
                  for row in range(1, 5) for number in range(1, 5)]
    assert all(seat["taken"] for seat in hall.seats if seat["row"] == 3), "Given: every seat in row 3 is taken"
    # Row 3 has no free seat left, so it is closed
    assert hall.closed_rows() == [3]
'''
MEANT = SWAPPED.replace("{(number, 3) for", "{(3, number) for")


def _report(message):
    return {"tests": [{"outcome": "failed", "call": {"outcome": "failed", "crash": {"message": message}}}]}


def test_a_test_whose_arrangement_is_not_what_it_states_is_no_valid_red():
    """Verify the gate tells a broken arrangement from missing behaviour.

    id: TST-RED-GIVEN-001
    Given: A failing test run whose assertion message begins "Given:", and one that fails on an ordinary assertion
    When: The RED gate judges each
    Then: The first is refused, naming the fact that did not hold; the second is a valid RED
    """
    refused = tdd_machine.evaluate_red_gate_result(
        1, _report("AssertionError: Given: every seat in row 3 is taken\nassert False"))
    assert refused["status"] == "REJECTED_GIVEN" and not refused["approved"]
    assert "every seat in row 3 is taken" in refused["reason"]

    assert tdd_machine.evaluate_red_gate_result(1, _report("AssertionError: assert [] == [3]"))["approved"]


@pytest.mark.slow
def test_a_broken_arrangement_goes_back_to_its_writer_before_any_code(tmp_path, monkeypatch):
    """Verify the slip is caught by the run the gate already makes, and costs the writer its one regeneration.

    id: TST-RED-GIVEN-002
    Given: A first test whose data contradicts the fact it states about it, and a second with the data as meant
    When: The RED phase runs
    Then: The writer is asked again with the fact that did not hold and its own test; the second test is approved
          as a valid RED and is the one locked
    """
    domain = tmp_path / "src" / "domain"
    domain.mkdir(parents=True)
    (domain / "hall.py").write_text(HALL, encoding="utf-8")
    spec = BusinessSpec(spec_id="SPEC-001", title="A full row is closed", description="d",
                        given_when_then="Given a row with every seat taken When rows are listed Then it is closed",
                        target_aggregate="Hall", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False,
                        priority="High")
    asked = []

    def write_test(spec, *args, rejection_feedback="", **kwargs):
        asked.append(rejection_feedback)
        return SWAPPED if len(asked) == 1 else MEANT
    monkeypatch.setattr(tdd_machine, "generate_red_test", write_test)

    red = tdd_machine.run_red_phase(spec, tdd_machine.locate_domain_target(spec, str(tmp_path)), str(tmp_path), "")

    assert len(asked) == 2 and "Given: every seat in row 3 is taken" in asked[1] and "TAKEN = {(number, 3)" in asked[1]
    assert red.verdict == "approved" and red.test_code == MEANT
    assert [a["approved"] for a in red.attempts] == [False, True]


def test_the_test_writer_is_asked_to_prove_its_arrangement():
    """Verify the prompt asks for the checks the gate reads, in the form it reads them.

    id: TST-RED-GIVEN-003
    Given: The red_test_generation prompt
    When: It is read
    Then: It asks for the facts of the arrangement to be asserted before the When, with a message beginning "Given:"
    """
    path = os.path.join(os.path.dirname(tdd_machine.__file__), "..", "prompts", "red_test_generation.md")
    text = open(path, encoding="utf-8").read()
    assert '"Given: ' in text and "before the When" in text
