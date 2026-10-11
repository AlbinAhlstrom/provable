"""Fixing a red rule (ADR-010): the page is changed until the rule's own test is green and no other rule turned red.
A fix starts from a red test, gets one retry with what the app said, and leaves the page as it was when it fails."""
from onboarding.rule_fix import Check, NoFix, fix

RULE = {"spec_id": "SPEC-007", "title": "A sent order is locked",
        "given_when_then": "Given a sent order When the customer opens it Then its lines cannot be changed"}
RED = {"status": "fail", "reason": "AssertionError: still enabled", "evidence": "button enabled", "source": "def test_x(app): ..."}
PAGES = {"src/App.tsx": "old app", "src/views/OrderView.tsx": "old view"}


class _Bench:
    """A page on disk, a writer that answers in turn, and an app whose verdicts are set per attempt."""

    def __init__(self, answers, checks):
        self.disk = dict(PAGES)
        self.answers, self.checks = list(answers), list(checks)
        self.feedback, self.seen_by_check = [], []

    def write(self, feedback):
        self.feedback.append(feedback)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    def put(self, files):
        self.disk.update(files)

    def check(self):
        self.seen_by_check.append(dict(self.disk))
        return self.checks.pop(0)

    def run(self, stored=RED):
        return fix(RULE, stored, dict(PAGES), write=self.write, put=self.put, check=self.check)


def test_a_change_that_turns_the_rule_green_is_kept():
    """
    Given: A red rule and a writer whose change makes the app pass its check
    When: The rule is fixed
    Then: The change is on disk, the result names the changed file and one attempt was made
    """
    bench = _Bench([{"src/views/OrderView.tsx": "new view"}], [Check(ok=True)])
    result = bench.run()

    assert (result["status"], result["files"]) == ("fixed", ["src/views/OrderView.tsx"])
    assert bench.disk == {"src/App.tsx": "old app", "src/views/OrderView.tsx": "new view"}
    assert [a["ok"] for a in result["attempts"]] == [True] and bench.feedback == [""]


def test_a_rule_that_is_not_red_is_not_touched():
    """
    Given: A rule whose test passed, one that never ran and one whose test is broken
    When: A fix is asked for
    Then: Nothing is written: a fix starts from a test that judged the page and found it wanting
    """
    for stored in ({**RED, "status": "pass"}, None, {**RED, "status": "broken"}):
        bench = _Bench([], [])
        result = bench.run(stored)
        assert result["status"] == "not_red" and bench.feedback == [] and bench.disk == PAGES


def test_a_change_the_app_rejects_goes_back_once_with_what_the_app_said():
    """
    Given: A writer whose first change leaves the rule red and whose second makes it green
    When: The rule is fixed
    Then: The second attempt was told what the check said and which change it was said of, it started from the
          page as it was, and the second change is kept
    """
    bench = _Bench([{"src/App.tsx": "first try"}, {"src/views/OrderView.tsx": "second try"}],
                   [Check(ok=False, reason="the rule's test still fails", evidence="button enabled"), Check(ok=True)])
    result = bench.run()

    assert result["status"] == "fixed" and result["files"] == ["src/views/OrderView.tsx"]
    assert "the rule's test still fails" in bench.feedback[1] and "button enabled" in bench.feedback[1]
    assert "first try" in bench.feedback[1]
    assert bench.seen_by_check[1] == {"src/App.tsx": "old app", "src/views/OrderView.tsx": "second try"}
    assert [a["ok"] for a in result["attempts"]] == [False, True]


def test_two_rejected_changes_leave_the_page_as_it_was():
    """
    Given: A writer whose two changes are both rejected
    When: The rule is fixed
    Then: The page on disk is the original, the result says why, and nothing is written a third time
    """
    bench = _Bench([{"src/App.tsx": "first"}, {"src/App.tsx": "second"}, {"src/App.tsx": "third"}],
                   [Check(ok=False, reason="turned SPEC-002 red"), Check(ok=False, reason="the page does not build")])
    result = bench.run()

    assert (result["status"], result["reason"], result["files"]) == ("not_fixed", "the page does not build", [])
    assert bench.disk == PAGES and len(bench.feedback) == 2
    assert [a["reason"] for a in result["attempts"]] == ["turned SPEC-002 red", "the page does not build"]


def test_a_file_the_writer_was_not_shown_is_refused_and_nothing_is_written():
    """
    Given: A writer that answers with a file outside the page it was shown, twice
    When: The rule is fixed
    Then: Neither answer reaches the disk or the check, and the refusal was fed back
    """
    bench = _Bench([{"src/domain/order.py": "x"}, {"../secrets.txt": "x"}], [])
    result = bench.run()

    assert result["status"] == "not_fixed" and bench.disk == PAGES and bench.seen_by_check == []
    assert "src/domain/order.py" in bench.feedback[1] and "src/App.tsx" in bench.feedback[1]


def test_an_answer_that_changes_nothing_is_a_rejected_attempt():
    """
    Given: A writer that answers with a shown file exactly as it is
    When: The rule is fixed
    Then: The app is not checked for it: the rule is known to be red on this page
    """
    bench = _Bench([{"src/App.tsx": "old app"}, {"src/App.tsx": "new app"}], [Check(ok=True)])
    result = bench.run()
    assert result["status"] == "fixed" and len(bench.seen_by_check) == 1
    assert "changes nothing" in bench.feedback[1]


def test_a_model_that_gives_no_answer_is_not_asked_again():
    """
    Given: A writer that fails (a provider or parse error)
    When: The rule is fixed
    Then: The result carries the error, and there was one call
    """
    bench = _Bench([NoFix("the provider answered 529")], [])
    result = bench.run()
    assert (result["status"], result["reason"]) == ("not_fixed", "the provider answered 529")
    assert len(bench.feedback) == 1 and bench.disk == PAGES
