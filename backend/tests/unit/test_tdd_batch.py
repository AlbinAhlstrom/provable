"""A deck's rules are written together (service_layer/tdd_batch.py).

One spec at a time, a nine-rule deck took nine test calls and nine code calls strictly one after another: most of a
kickstart's duration. The tests do not depend on each other's code, so they are written side by side; the code for
every rule of one class is then written in one answer and judged test by test.
"""
import os
import threading

import pytest

from onboarding.router_engine import BusinessSpec
from service_layer import tdd_batch, tdd_machine

pytestmark = pytest.mark.slow  # every case runs pytest in the generated workspace several times

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
        answer = answers[len(calls) - 1]
        if isinstance(answer, Exception):
            raise answer
        return answer
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
    Then: Two code calls; the second was told the failing test by name, was given only that test to satisfy and
          the two that already pass as tests to keep passing; every spec is fulfilled with two attempts
    """
    workspace = _workspace(tmp_path)
    calls = _models(monkeypatch, [_fragment(PAY, ADD_LINE_OPEN), _fragment(ADD_LINE)])

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(calls) == 2 and "test_spec_003.py" in calls[1]["failure_output"]
    assert "test_spec_003.py" in calls[1]["test_source"] and "test_spec_001.py" not in calls[1]["test_source"]
    assert "test_spec_001.py" in calls[1]["existing_tests"] and "test_spec_002.py" in calls[1]["existing_tests"]
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


def test_a_retry_that_answers_in_words_leaves_the_first_answer_standing(tmp_path, monkeypatch):
    """Verify a code writer that declines the retry ("the test is wrong, the class needs no change") does not take
    the rules its first answer fulfilled down with it. A live kickstart lost all seventeen specs of a class this way.

    id: TST-BATCH-RETRY-IN-WORDS
    Given: A first answer that leaves the third test failing, and a retry whose answer holds no class
    When: The specs are executed together
    Then: The first two specs are fulfilled by the first answer; the third is not, with the failing assertion as
          its reason and the writer's words in its second attempt; the tests left in tests/unit pass
    """
    workspace = _workspace(tmp_path)
    declined = tdd_machine.NoClassInAnswer("Invoice", "The test expects the wrong total; Invoice needs no change.")
    calls = _models(monkeypatch, [_fragment(PAY, ADD_LINE_OPEN), declined])

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(calls) == 2
    assert results["SPEC-001"]["status"] == results["SPEC-002"]["status"] == "FULFILLED"
    failed = results["SPEC-003"]
    assert failed["status"] == "REQUIRES_HUMAN_INTERVENTION" and "Test assertions failed" in failed["error"]
    assert "Invoice needs no change" in failed["attempts"][1]["reason"]
    assert tdd_machine.run_isolated_pytest(str(tmp_path / "tests" / "unit"), cwd=workspace)["exit_code"] == 0


def test_a_first_answer_without_the_class_fails_the_class_loudly(tmp_path, monkeypatch):
    """Verify nothing is kept or retried when the first answer is no code: there is no verdict to feed back.

    id: TST-BATCH-NO-CLASS-FIRST
    Given: A first answer that holds no class
    When: The specs are executed together
    Then: One code call; every spec is an error naming the reason; the class is as it was
    """
    workspace = _workspace(tmp_path)
    calls = _models(monkeypatch, [tdd_machine.NoClassInAnswer("Invoice", "I cannot do this.")])

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(calls) == 1
    assert all(results[i]["status"] == "ERROR" and "definition of class Invoice" in results[i]["error"] for i in TESTS)
    assert (tmp_path / "src" / "domain" / "invoice.py").read_text(encoding="utf-8") == INVOICE


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


WRONG_003 = '''from src.domain.invoice import Invoice


def test_a_paid_invoice_takes_no_more_lines():
    invoice = Invoice(id="i1", status="paid")
    invoice.add_line(amount=1)
    assert invoice.total == 1
'''


asked_carefully = []


def _writer(monkeypatch, first, second):
    """A test writer whose first test for SPEC-003 is `first` and whose reconsidered one is `second`."""
    asked_carefully.clear()
    asked = []
    careful = asked_carefully

    def write_test(spec, *args, rejection_feedback="", **kwargs):
        if spec.spec_id != "SPEC-003":
            return TESTS[spec.spec_id]
        asked.append(rejection_feedback)
        careful.append(bool(kwargs.get("careful")))
        return first if len(asked) == 1 else second
    monkeypatch.setattr(tdd_machine, "generate_red_test", write_test)
    return asked


def test_a_test_no_code_answer_could_meet_is_reconsidered_once_by_its_writer(tmp_path, monkeypatch):
    """Verify a wrong expectation in a test does not fail a rule the code enforces.

    id: TST-BATCH-007
    Given: A test for SPEC-003 that expects a paid invoice to take a line (the rule says it is refused), and two
           code answers that both enforce the rule correctly
    When: The specs are executed together, and the writer, shown its test and the failure, corrects it
    Then: Two code calls and no third; the writer was shown the failing output and its own test; the spec is
          fulfilled by the corrected test, which is the one kept in tests/unit; nothing is left in tests/pending
    """
    workspace = _workspace(tmp_path)
    calls = _models(monkeypatch, [_fragment(PAY, ADD_LINE), _fragment(PAY, ADD_LINE)])
    asked = _writer(monkeypatch, WRONG_003, TESTS["SPEC-003"])

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(calls) == 2 and len(asked) == 2 and asked_carefully == [False, True]
    assert "A paid invoice takes no more lines" in asked[1] and "assert invoice.total == 1" in asked[1]
    assert "def add_line(self, amount: int) -> None:" in asked[1]  # the implementation it is asked to trace
    fulfilled = results["SPEC-003"]
    assert fulfilled["success"] and fulfilled["reconsidered"] and len(fulfilled["red_attempts"]) == 2
    assert (tmp_path / "tests" / "unit" / "test_spec_003.py").read_text(encoding="utf-8") == TESTS["SPEC-003"]
    assert not (tmp_path / "tests" / "pending" / "test_spec_003.py").exists()
    assert results["SPEC-001"]["success"] and results["SPEC-002"]["success"]


def test_a_writer_that_stands_by_its_test_leaves_the_rule_unfulfilled(tmp_path, monkeypatch):
    """Verify reconsidering is not a way to make a failing rule pass.

    id: TST-BATCH-008
    Given: Code that does not enforce SPEC-003 in either answer, and a writer that returns its (correct) test again
    When: The specs are executed together
    Then: The writer was asked exactly once more; the spec stays unfulfilled with its test in tests/pending
    """
    workspace = _workspace(tmp_path)
    _models(monkeypatch, [_fragment(PAY, ADD_LINE_OPEN), _fragment(PAY, ADD_LINE_OPEN)])
    asked = _writer(monkeypatch, TESTS["SPEC-003"], TESTS["SPEC-003"])

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(asked) == 2 and not results["SPEC-003"]["success"]
    assert (tmp_path / "tests" / "pending" / "test_spec_003.py").exists()
    assert not (tmp_path / "tests" / "unit" / "test_spec_003.py").exists()


def test_a_test_already_regenerated_once_is_not_reconsidered(tmp_path, monkeypatch):
    """Verify the test writer gets one more attempt in all, whichever gate asked for it.

    id: TST-BATCH-009
    Given: A first test for SPEC-003 the RED gate refuses (it asserts nothing about behaviour), a regenerated one
           with a wrong expectation, and code that enforces the rule correctly
    When: The specs are executed together
    Then: The writer was called twice for the spec and no third time; the spec is unfulfilled
    """
    workspace = _workspace(tmp_path)
    _models(monkeypatch, [_fragment(PAY, ADD_LINE), _fragment(PAY, ADD_LINE)])
    nothing = "from src.domain.invoice import Invoice\n\n\ndef test_starts_open():\n    assert Invoice(id='i1').status == 'open'\n"
    asked = _writer(monkeypatch, nothing, WRONG_003)

    results = tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert len(asked) == 2 and not results["SPEC-003"]["success"]


def test_each_test_writer_is_shown_the_other_rules_of_the_class(tmp_path, monkeypatch):
    """Verify a test can be arranged so that no other rule of the deck changes its outcome: its writer knows them.

    id: TST-BATCH-010
    Given: Three specs on one class
    When: The specs are executed together
    Then: The writer of each test was given the other two rules, title and scenario, and not its own
    """
    workspace = _workspace(tmp_path)
    _models(monkeypatch, [_fragment(PAY, ADD_LINE)])
    shown = {}

    def write_test(spec, *args, **kwargs):
        shown[spec.spec_id] = kwargs.get("other_rules", "")
        return TESTS[spec.spec_id]
    monkeypatch.setattr(tdd_machine, "generate_red_test", write_test)

    tdd_batch.execute_specs_together([_spec(i) for i in TESTS], workspace)

    assert "Rule SPEC-002: Given a When b Then c" in shown["SPEC-001"] and "Rule SPEC-003" in shown["SPEC-001"]
    assert "Rule SPEC-001" not in shown["SPEC-001"]


def test_a_rule_that_passed_before_the_code_was_written_does_not_outrank_the_others(tmp_path, monkeypatch):
    """Verify a deck's tests are judged as peers: one that happened to pass on the unfinished class is not a veto.

    id: TST-BATCH-011
    Given: A class that refuses a second payment, a spec for that (already satisfied) and a spec that needs code;
           two code answers that add the new rule and both stop refusing the second payment
    When: The specs are executed together
    Then: The new rule is fulfilled and its code kept; the rule the answers broke is the one reported unfulfilled,
          with what failed; the retry was asked to satisfy its test
    """
    workspace = _workspace(tmp_path, INVOICE + PAY)
    pays_twice = _fragment("\n    def pay(self) -> None:\n        self.status = 'paid'\n", ADD_LINE_OPEN)
    calls = _models(monkeypatch, [pays_twice, pays_twice])

    results = tdd_batch.execute_specs_together([_spec("SPEC-001"), _spec("SPEC-002")], workspace)

    assert results["SPEC-002"]["success"] and "def add_line" in (tmp_path / "src" / "domain" / "invoice.py").read_text(encoding="utf-8")
    broken = results["SPEC-001"]
    assert not broken["success"] and "DID NOT RAISE" in broken["error"]
    assert len(calls) == 2 and "test_spec_001.py" in calls[0]["existing_tests"] and "test_spec_001.py" in calls[1]["test_source"]
    assert tdd_machine.run_isolated_pytest(str(tmp_path / "tests" / "unit"), cwd=workspace)["exit_code"] == 0
