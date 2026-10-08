"""A deck's rules are written together (service_layer/tdd_batch.py).

One spec at a time, a nine-rule deck took nine test calls and nine code calls strictly one after another: most of a
kickstart's duration. The tests do not depend on each other's code, so they are written side by side; the code for
every rule of one class is then written in one answer and judged test by test.
"""
import os
import threading

from onboarding.router_engine import BusinessSpec
from service_layer import tdd_batch, tdd_machine

INVOICE = '''from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Invoice:
    id: str
    status: str = "open"
    total: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)
'''

TESTS = {
    "SPEC-001": '''import pytest
from src.domain.invoice import Invoice


def test_an_invoice_cannot_be_paid_twice():
    invoice = Invoice(id="i1")
    invoice.pay()
    with pytest.raises(ValueError):
        invoice.pay()
''',
    "SPEC-002": '''from src.domain.invoice import Invoice


def test_adding_a_line_raises_the_total():
    invoice = Invoice(id="i1")
    invoice.add_line(amount=40)
    assert invoice.total == 40
''',
    "SPEC-003": '''import pytest
from src.domain.invoice import Invoice


def test_a_paid_invoice_takes_no_more_lines():
    invoice = Invoice(id="i1", status="paid")
    with pytest.raises(ValueError):
        invoice.add_line(amount=1)
''',
}

PAY = '''
    def pay(self) -> None:
        if self.status == "paid":
            raise ValueError("Invoice is already paid.")
        self.status = "paid"
'''
ADD_LINE_OPEN = '''
    def add_line(self, amount: int) -> None:
        self.total += amount
'''
ADD_LINE = '''
    def add_line(self, amount: int) -> None:
        if self.status == "paid":
            raise ValueError("A paid invoice takes no more lines.")
        self.total += amount
'''


def _fragment(*methods):
    return "@dataclass\nclass Invoice:\n" + "".join(methods)


def _spec(spec_id):
    return BusinessSpec(spec_id=spec_id, title=f"Rule {spec_id}", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="Invoice", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False, priority="High")


def _workspace(tmp_path, source=INVOICE):
    domain = tmp_path / "src" / "domain"
    domain.mkdir(parents=True)
    (domain / "invoice.py").write_text(source, encoding="utf-8")
    return str(tmp_path)


def _models(monkeypatch, answers, tests=TESTS):
    """The test writer answers by spec; the code writer gives `answers` in order and records what it was shown."""
    calls = []
    monkeypatch.setattr(tdd_machine, "generate_red_test", lambda spec, *a, **k: tests[spec.spec_id])

    def green(**kwargs):
        calls.append(kwargs)
        return answers[len(calls) - 1]
    monkeypatch.setattr(tdd_machine, "synthesize_green_class_implementation", green)
    return calls


def test_every_rule_of_a_class_is_implemented_by_one_answer(tmp_path, monkeypatch):
    """Verify three rules need one code call, not three, and each is judged by its own test.

    id: TST-BATCH-001
    Given: Three specs on one class and a code answer that satisfies all three tests
    When: The specs are executed together
    Then: The code writer was called once and shown all three tests; every spec is fulfilled; its test is in
          tests/unit; results are reported in deck order
    """
    workspace = _workspace(tmp_path)
    calls = _models(monkeypatch, [_fragment(PAY, ADD_LINE)])
    reported = []

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace,
                                               on_result=lambda spec, result: reported.append(spec.spec_id))

    assert len(calls) == 1 and all(name in calls[0]["test_source"] for name in
                                   ("test_spec_001.py", "test_spec_002.py", "test_spec_003.py"))
    assert all(results[i]["success"] and results[i]["status"] == "FULFILLED" for i in TESTS)
    assert all(os.path.exists(results[i]["test_file"]) for i in TESTS)
    assert reported == list(TESTS)


def test_the_tests_are_written_side_by_side(tmp_path, monkeypatch):
    """Verify the test calls overlap: each waits for another to be in flight before answering.

    id: TST-BATCH-002
    Given: A test writer that only answers once two calls are in flight at the same time
    When: Three specs are executed together
    Then: Every spec got its test (no call waited in vain)
    """
    workspace = _workspace(tmp_path)
    _models(monkeypatch, [_fragment(PAY, ADD_LINE)])
    together = threading.Barrier(2, timeout=10)
    first_two = iter([True, True])

    def write_test(spec, *args, **kwargs):
        if next(first_two, False):
            together.wait()
        return TESTS[spec.spec_id]
    monkeypatch.setattr(tdd_machine, "generate_red_test", write_test)

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)
    assert all(results[i]["success"] for i in TESTS)


def test_tests_still_failing_are_fed_back_once(tmp_path, monkeypatch):
    """Verify the one retry: the code writer is shown which tests its first answer left failing.

    id: TST-BATCH-003
    Given: A first answer that satisfies two of three tests, and a second that satisfies all
    When: The specs are executed together
    Then: Two code calls; the second was told the failing test by name; every spec is fulfilled with two attempts
    """
    workspace = _workspace(tmp_path)
    calls = _models(monkeypatch, [_fragment(PAY, ADD_LINE_OPEN), _fragment(ADD_LINE)])

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(calls) == 2 and "test_spec_003.py" in calls[1]["failure_output"]
    assert all(results[i]["success"] for i in TESTS) and len(results["SPEC-003"]["attempts"]) == 2


def test_a_rule_still_failing_after_the_retry_is_named_and_the_others_stand(tmp_path, monkeypatch):
    """Verify one rule that cannot be met does not take the others down with it.

    id: TST-BATCH-004
    Given: Two answers that both leave the third test failing
    When: The specs are executed together
    Then: Exactly two code calls; the first two specs are fulfilled; the third is not, with its reason and its test
          moved to tests/pending; the tests left in tests/unit pass
    """
    workspace = _workspace(tmp_path)
    calls = _models(monkeypatch, [_fragment(PAY, ADD_LINE_OPEN), _fragment(PAY, ADD_LINE_OPEN), _fragment(ADD_LINE)])

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(calls) == 2
    assert results["SPEC-001"]["success"] and results["SPEC-002"]["success"]
    failed = results["SPEC-003"]
    assert not failed["success"] and failed["status"] == "REQUIRES_HUMAN_INTERVENTION" and failed["error"]
    assert os.path.exists(tmp_path / "tests" / "pending" / "test_spec_003.py")
    assert not os.path.exists(tmp_path / "tests" / "unit" / "test_spec_003.py")
    assert tdd_machine.run_isolated_pytest(str(tmp_path / "tests" / "unit"), cwd=workspace)["exit_code"] == 0


def test_an_answer_that_breaks_an_earlier_verified_test_is_never_kept(tmp_path, monkeypatch):
    """Verify the regression gate holds for the batch: earlier rules outrank new ones.

    id: TST-BATCH-005
    Given: A class with a verified test (pay works), and two answers that both break pay
    When: Two new specs are executed together
    Then: The class is exactly as it was, no new spec is fulfilled, each names the earlier test it broke, and the
          earlier test still passes
    """
    paid = INVOICE + PAY
    workspace = _workspace(tmp_path, paid)
    unit = tmp_path / "tests" / "unit"
    unit.mkdir(parents=True)
    (unit / "test_spec_act_invoice.py").write_text(
        "from src.domain.invoice import Invoice\n\n\ndef test_pay_marks_it_paid():\n"
        "    invoice = Invoice(id='i1')\n    invoice.pay()\n    assert invoice.status == 'paid'\n", encoding="utf-8")
    breaks_pay = _fragment("\n    def pay(self) -> None:\n        self.status = 'void'\n", ADD_LINE)
    _models(monkeypatch, [breaks_pay, breaks_pay])

    results = tdd_batch.execute_specs_together([_spec("SPEC-002"), _spec("SPEC-003")], workspace)

    assert (tmp_path / "src" / "domain" / "invoice.py").read_text(encoding="utf-8") == paid
    assert not results["SPEC-002"]["success"] and not results["SPEC-003"]["success"]
    assert "test_spec_act_invoice.py" in results["SPEC-002"]["error"] and results["SPEC-002"]["rolled_back"]
    assert tdd_machine.run_isolated_pytest(str(unit), cwd=workspace)["exit_code"] == 0


def test_a_rule_settled_by_its_test_alone_asks_for_no_code(tmp_path, monkeypatch):
    """Verify a rule the class already enforces, and a rule whose test is refused twice, stay out of the code call.

    id: TST-BATCH-006
    Given: A class that already refuses a second payment; one spec for that, one whose test asserts nothing, and
           one that needs new code
    When: The specs are executed together
    Then: The first is fulfilled as already satisfied, the second is refused at the RED gate, the third is fulfilled;
          the code writer was shown only the third's test
    """
    workspace = _workspace(tmp_path, INVOICE + PAY)
    tests = dict(TESTS)
    tests["SPEC-003"] = ("from src.domain.invoice import Invoice\n\n\ndef test_starts_open():\n"
                         "    assert Invoice(id='i1').status == 'open'\n")
    calls = _models(monkeypatch, [_fragment(ADD_LINE)], tests=tests)

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert results["SPEC-001"]["success"] and results["SPEC-001"]["already_satisfied"]
    assert not results["SPEC-003"]["success"] and results["SPEC-003"]["phase"] == "RED_GATE"
    assert results["SPEC-002"]["success"]
    assert len(calls) == 1 and "test_spec_002.py" in calls[0]["test_source"] and "test_spec_001.py" not in calls[0]["test_source"]
