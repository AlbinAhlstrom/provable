"""A rule the app already enforces is fulfilled, not a dead end (service_layer/hollow_check.py, tdd_machine).

The action stage writes an aggregate's methods before the rule deck runs. A rule those methods already enforce (a
move is refused when it is not that colour's turn) gets a test that passes at once. The RED gate called every such
test a tautology, and the build reported the rule as not enforced. A test that passes at once is now run a second
time against the class with its behaviour emptied out: if it fails there, it does test behaviour, and the behaviour
is already in the class.
"""
import ast
import os

from onboarding.router_engine import BusinessSpec
from service_layer import tdd_machine
from service_layer.hollow_check import hollow_class_source

INVOICE = '''from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Invoice:
    id: str
    status: str = "open"

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)

    def pay(self) -> None:
        """Marks the invoice paid."""
        if self.status == "paid":
            raise ValueError("Invoice is already paid.")
        self.status = "paid"
'''

MEANINGFUL_TEST = '''import pytest
from src.domain.invoice import Invoice


def test_an_invoice_cannot_be_paid_twice():
    invoice = Invoice(id="i1")
    invoice.pay()
    with pytest.raises(ValueError):
        invoice.pay()
'''

TAUTOLOGICAL_TEST = '''from src.domain.invoice import Invoice


def test_an_invoice_starts_open():
    assert Invoice(id="i1").status == "open"
'''


def _spec():
    return BusinessSpec(spec_id="SPEC-007", title="No double payment", description="d",
                        given_when_then="Given a paid invoice When it is paid again Then it is refused",
                        target_aggregate="Invoice", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False, priority="High")


def _workspace(tmp_path):
    domain = tmp_path / "src" / "domain"
    domain.mkdir(parents=True)
    (domain / "invoice.py").write_text(INVOICE, encoding="utf-8")
    return str(tmp_path)


def _no_green(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("the GREEN generator was called for a rule that needed no code")
    monkeypatch.setattr(tdd_machine, "synthesize_green_class_implementation", forbidden)


def test_hollowing_empties_the_behaviour_and_keeps_the_shape():
    """Verify the hollow class has the same fields and method names, and methods that do nothing.

    id: TST-HOLLOW-001
    Given: A class with fields, to_dict and a method that changes state and can raise
    When: The class is hollowed
    Then: The source still parses, the method is there with an empty body (its docstring kept), and the fields and
          to_dict are untouched
    """
    hollow = hollow_class_source(INVOICE, "Invoice")
    cls = next(n for n in ast.parse(hollow).body if isinstance(n, ast.ClassDef))
    pay = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "pay")

    assert isinstance(pay.body[-1], ast.Pass) and "raise" not in ast.unparse(pay)
    assert 'status: str = "open"' in hollow.replace("'", '"') and "return dict(self.__dict__)" in hollow


def test_a_rule_the_class_already_enforces_is_fulfilled_and_keeps_its_test(tmp_path, monkeypatch):
    """Verify a test that passes at once, and fails on the hollow class, fulfils the spec without new code.

    id: TST-HOLLOW-002
    Given: A class that already refuses a second payment, and a test of exactly that
    When: The spec goes through the TDD loop
    Then: It is fulfilled and marked as already satisfied; the test is kept as a regression guard; the class is
          unchanged; no code was generated
    """
    workspace = _workspace(tmp_path)
    monkeypatch.setattr(tdd_machine, "generate_red_test", lambda *a, **k: MEANINGFUL_TEST)
    _no_green(monkeypatch)

    result = tdd_machine.execute_spec_tdd_loop(_spec(), workspace)

    assert result["success"] is True and result["status"] == "FULFILLED" and result["already_satisfied"] is True
    assert os.path.exists(result["test_file"]) and result["test_file"].endswith(os.path.join("tests", "unit", "test_spec_007.py"))
    assert (tmp_path / "src" / "domain" / "invoice.py").read_text(encoding="utf-8") == INVOICE
    assert result["attempts"] == [] and len(result["red_attempts"]) == 1


def test_a_test_that_passes_even_without_behaviour_is_still_a_tautology(tmp_path, monkeypatch):
    """Verify the guard against empty tests holds: passing on the hollow class is not evidence of anything.

    id: TST-HOLLOW-003
    Given: A test that only reads a default value
    When: The spec goes through the TDD loop (the regenerated test is the same)
    Then: The spec is not fulfilled, the reason says the test passes without any behaviour, and the test is not kept
    """
    workspace = _workspace(tmp_path)
    monkeypatch.setattr(tdd_machine, "generate_red_test", lambda *a, **k: TAUTOLOGICAL_TEST)
    _no_green(monkeypatch)

    result = tdd_machine.execute_spec_tdd_loop(_spec(), workspace)

    assert result["success"] is False and result["phase"] == "RED_GATE"
    assert "tautolog" in result["error"].lower() and len(result["red_attempts"]) == 2
    assert not (tmp_path / "tests" / "unit" / "test_spec_007.py").exists()


LEDGER = """from dataclasses import dataclass, field
from typing import Any, Dict, List


def _opening_entries() -> List[Dict[str, Any]]:
    return [{"account": "cash", "amount": 0}, {"account": "equity", "amount": 0}]


@dataclass
class Ledger:
    id: str
    currency: str = "EUR"
    entries: List[Dict[str, Any]] = field(default_factory=_opening_entries)
    notes: List[str] = field(default_factory=list)
    totals: Dict[str, int] = field(default_factory=lambda: {"cash": 0})
"""


def test_hollowing_empties_a_starting_state_the_class_works_out():
    """Verify a rule about how a new object starts is behaviour too when the class computes that state.

    id: TST-HOLLOW-004
    Given: A class whose fields start from a function, from a lambda, from an empty list and from a literal
    When: The class is hollowed
    Then: The computed starting states are empty containers of their kind; the literal and the empty list are as
          they were, so a test that only reads a literal default is still a tautology
    """
    scope: dict = {}
    exec(hollow_class_source(LEDGER, "Ledger"), scope)
    ledger = scope["Ledger"](id="l1")

    assert ledger.entries == [] and ledger.totals == {}
    assert ledger.notes == [] and ledger.currency == "EUR"


def test_the_test_writer_thinks_longer_when_asked_to_be_careful(monkeypatch):
    """Verify a reconsidered test is written with more thought than a first draft, and given the time for it.

    id: TST-RED-CAREFUL
    Given: The test writer
    When: It is asked for a test, and then for a careful one
    Then: The first call leaves the effort at the default; the careful one asks for medium effort and a longer timeout
    """
    import agent_orchestrator
    seen = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **k: seen.append(k) or "```python\nx\n```")
    tdd_machine.generate_red_test(_spec(), "class Invoice:\n    pass\n", "invoice", "Invoice")
    tdd_machine.generate_red_test(_spec(), "class Invoice:\n    pass\n", "invoice", "Invoice", careful=True)

    assert not seen[0].get("reasoning_effort")
    assert seen[1]["reasoning_effort"] == "medium" and seen[1]["timeout_s"] > 60


def test_a_first_draft_of_a_test_is_given_the_time_a_whole_class_of_actions_takes(monkeypatch):
    """Verify a test may take longer to write than an ordinary call (the one test of a class's eight actions took
    31 s in one build and was cut off at 60 s in the next, slower one, so no action was built and the page was empty).

    id: TST-RED-TIME
    Given: The test writer
    When: It is asked for a first draft
    Then: The call is given more time than an ordinary call, at the default effort
    """
    import agent_orchestrator
    seen = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **k: seen.append(k) or "```python\nx\n```")
    tdd_machine.generate_red_test(_spec(), "class Invoice:\n    pass\n", "invoice", "Invoice")

    assert seen[0]["timeout_s"] == tdd_machine.RED_TIMEOUT_S > agent_orchestrator.DEFAULT_TIMEOUT_S
    assert not seen[0].get("reasoning_effort")
