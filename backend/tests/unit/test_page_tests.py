"""A rule is proved by a test that drives the running page (ADR-010). These tests cover everything around the browser:
what a run's report means, when a test is written or written again, and what the test writer is shown."""
import os

from onboarding import page_tests
from onboarding.page_tests import Verdict, condense, describe_app, ensure_harness, judge, lint, prove

RULE = {"spec_id": "SPEC-007", "title": "A sent order is locked",
        "given_when_then": "Given a sent order When the customer opens it Then its lines cannot be changed"}
GOOD_TEST = '''from playwright.sync_api import expect


def test_a_sent_order_is_locked(app):
    order = app.given("orders", status="sent")
    page = app.open()
    expect(page.get_by_role("button", name="Add line")).to_be_disabled()
'''


def _report(*tests, collectors=()):
    return {"exit_code": 1, "timed_out": False, "stderr": "", "report": {"tests": list(tests), "collectors": list(collectors)}}


def _test(outcome="passed", raised=None, message="", when="call"):
    stage = {"outcome": "failed", "crash": {"message": message}, "longrepr": message} if raised else {"outcome": "passed"}
    return {"nodeid": "tests/e2e/test_x.py::test_x", "outcome": outcome, when: stage,
            "metadata": {"raised": f"{when}:{raised}"} if raised else {}}


# ── what a run says ───────────────────────────────────────────────────────────

def test_a_run_whose_assertions_all_held_passes():
    """
    Given: A report with two passed tests
    When: The run is judged
    Then: The rule passes, with no reason
    """
    verdict = judge(_report(_test(), _test()))
    assert (verdict.status, verdict.reason) == ("pass", None)


def test_an_assertion_that_did_not_hold_fails_the_rule():
    """
    Given: A report with one passed test and one that raised an AssertionError
    When: The run is judged
    Then: The rule fails, the reason is the assertion's first line, and nothing suggests writing the test again
    """
    verdict = judge(_report(_test(), _test("failed", "AssertionError", "AssertionError: Locator expected to be disabled\nCall log: ...")))
    assert verdict.status == "fail"
    assert verdict.reason == "AssertionError: Locator expected to be disabled"
    assert verdict.control_not_found is False
    assert "Call log" in verdict.evidence


def test_the_evidence_names_the_case_that_failed_and_condenses_what_the_page_read_out():
    """
    Given: A failed test whose message carries what the page read out, forty like controls long
    When: The run is judged
    Then: The evidence opens with the name of the test function, keeps the expectation, and shows the forty
          controls by their first few and a line for the rest
    """
    seats = "\n".join(f'  - button "Seat {n}, free"' for n in range(1, 41))
    message = f"AssertionError: Locator expected to be visible\nActual value: hidden\n- main:\n{seats}"
    verdict = judge(_report(_test("failed", "AssertionError", message)))
    assert verdict.evidence.startswith("in test_x:\nAssertionError: Locator expected to be visible\nActual value: hidden")
    assert '… 37 more button like these, named "Seat #, free"' in verdict.evidence
    assert 'Seat 20, free' not in verdict.evidence


def test_a_control_the_page_never_offered_fails_the_rule_and_is_marked():
    """
    Given: A report whose test timed out waiting for a control
    When: The run is judged
    Then: The rule fails and the verdict says a control was not found (the test may be the one that is wrong)
    """
    verdict = judge(_report(_test("failed", "TimeoutError", "TimeoutError: Locator.click: Timeout 5000ms exceeded.")))
    assert (verdict.status, verdict.control_not_found) == ("fail", True)


def test_a_run_that_could_not_judge_is_broken():
    """
    Given: A test that raised something else, one whose setup failed, a module that did not import, a run that timed
           out and a run that collected nothing
    When: Each run is judged
    Then: Each is broken and carries its reason
    """
    other = judge(_report(_test("failed", "Refused", "Refused: POST /api/orders answered 422")))
    setup = judge(_report(_test("error", "RuntimeError", "RuntimeError: the app's API did not start", when="setup")))
    imports = judge(_report(collectors=[{"outcome": "failed", "longrepr": "ImportError: No module named 'x'"}]))
    late = judge({"exit_code": 2, "timed_out": True, "stderr": "Pytest execution timed out after 90 seconds.", "report": {}})
    nothing = judge({"exit_code": 5, "timed_out": False, "stderr": "", "report": {"tests": []}})
    assert [v.status for v in (other, setup, imports, late, nothing)] == ["broken"] * 5
    assert other.reason == "Refused: POST /api/orders answered 422"
    assert "did not start" in setup.reason
    assert "ImportError" in imports.reason
    assert "timed out" in late.reason
    assert nothing.reason


# ── what a test must be ──────────────────────────────────────────────────────

def test_a_page_test_opens_the_page_and_asserts_something():
    """
    Given: A test that opens the page and expects something, and four that are not page tests
    When: Each is linted
    Then: Only the first is accepted, and each refusal says why
    """
    assert lint(GOOD_TEST) == (True, "")
    no_page = "def test_x(app):\n    assert app.given('orders', status='sent')['status'] == 'sent'\n"
    no_assertion = "def test_x(app):\n    app.open().get_by_role('button').click()\n"
    imports_the_app = "from src.domain.order import Order\n" + GOOD_TEST
    for source, word in ((no_page, "app.open"), (no_assertion, "assert"), (imports_the_app, "import"), ("def broken(:", "SyntaxError")):
        accepted, why = lint(source)
        assert accepted is False and word in why


# ── when a test is written ───────────────────────────────────────────────────

class _Bench:
    """Stands in for the model and the browser."""

    def __init__(self, sources, verdicts):
        self.sources, self.verdicts = list(sources), list(verdicts)
        self.feedback, self.ran = [], []

    def write(self, rule, feedback):
        self.feedback.append(feedback)
        return self.sources.pop(0)

    def run(self, source):
        self.ran.append(source)
        return self.verdicts.pop(0)


def _prove(bench, stored=None):
    return prove(RULE, write=bench.write, run=bench.run, stored=stored)


def test_a_rule_without_a_test_gets_one_written_and_run():
    """
    Given: A rule that has no stored test
    When: It is proved
    Then: One test is written, run, and stored with its verdict and the rule text it was written for
    """
    bench = _Bench([GOOD_TEST], [Verdict("pass")])
    result = _prove(bench)
    assert (result["status"], result["source"], bench.feedback) == ("pass", GOOD_TEST, [""])
    assert result["written_for"] == page_tests.rule_text(RULE)
    assert result["written"] == 1


def test_a_stored_test_is_run_again_as_it_is():
    """
    Given: A rule with a stored test that ran to a verdict before
    When: It is proved again
    Then: Nothing is written; the stored test runs and its new verdict is reported, red included
    """
    bench = _Bench([], [Verdict("fail", "AssertionError: still enabled", "evidence")])
    stored = {"status": "pass", "source": GOOD_TEST, "written_for": page_tests.rule_text(RULE)}
    result = _prove(bench, stored)
    assert (result["status"], result["reason"], result["written"]) == ("fail", "AssertionError: still enabled", 0)
    assert bench.ran == [GOOD_TEST]


def test_a_changed_rule_or_a_broken_test_is_written_again():
    """
    Given: A stored test written for other wording, and a stored test that was broken
    When: Each rule is proved
    Then: Each gets a new test
    """
    for stored in ({"status": "pass", "source": "old", "written_for": "Given something else"},
                   {"status": "broken", "source": "old", "written_for": page_tests.rule_text(RULE)}):
        bench = _Bench([GOOD_TEST], [Verdict("pass")])
        assert _prove(bench, stored)["source"] == GOOD_TEST


def test_a_new_test_that_could_not_judge_is_written_once_more_with_the_error():
    """
    Given: A new test that is broken, and one that could not find a control
    When: Each rule is proved
    Then: Each is written a second time with the first run's evidence, and the second verdict stands
    """
    for first in (Verdict("broken", "Refused: 422", "Refused: POST /api/orders answered 422"),
                  Verdict("fail", "TimeoutError", "Locator.click: Timeout", control_not_found=True)):
        bench = _Bench([GOOD_TEST, GOOD_TEST + "# again\n"], [first, Verdict("pass")])
        result = _prove(bench)
        assert (result["status"], result["written"]) == ("pass", 2)
        assert first.evidence in bench.feedback[1]
        assert result["source"].endswith("# again\n")


def test_a_new_test_that_fails_is_checked_once_against_the_rule():
    """
    Given: A new test whose assertion did not hold, and a writer that finds its own expectation was wrong
    When: The rule is proved
    Then: The writer is shown the test and the evidence once, and the corrected test's verdict stands
    """
    bench = _Bench([GOOD_TEST, GOOD_TEST + "# corrected\n"], [Verdict("fail", "AssertionError: expected 3", "expected 3, got 2"), Verdict("pass")])
    result = _prove(bench)
    assert (result["status"], result["written"]) == ("pass", 2)
    assert "expected 3, got 2" in bench.feedback[1] and "the rule" in bench.feedback[1]


def test_a_writer_that_stands_by_its_test_leaves_the_rule_red():
    """
    Given: A new test whose assertion did not hold, and a writer that answers with the same test
    When: The rule is proved
    Then: The test is not run again and the rule is red with the first run's reason
    """
    bench = _Bench([GOOD_TEST, GOOD_TEST], [Verdict("fail", "AssertionError: nothing happened", "evidence")])
    result = _prove(bench)
    assert (result["status"], result["reason"], len(bench.ran)) == ("fail", "AssertionError: nothing happened", 1)


def test_nothing_is_written_a_third_time():
    """
    Given: A new test that is broken, and a second one that cannot find a control either
    When: The rule is proved
    Then: The second verdict stands: red, because the page offers no control the test could use
    """
    second = Verdict("fail", "TimeoutError: no button", "e", control_not_found=True)
    bench = _Bench([GOOD_TEST, GOOD_TEST + "# again\n"], [Verdict("broken", "x", "x"), second])
    result = _prove(bench)
    assert (result["status"], result["written"], bench.sources) == ("fail", 2, [])


def test_a_refused_test_is_written_again_once_and_never_run():
    """
    Given: A model whose first test asserts nothing
    When: The rule is proved
    Then: The lint's reason is the feedback for the one rewrite; a second refusal is broken and nothing ran
    """
    refused = "def test_x(app):\n    app.open()\n"
    bench = _Bench([refused, refused], [])
    result = _prove(bench)
    assert (result["status"], result["written"], bench.ran) == ("broken", 2, [])
    assert "assert" in bench.feedback[1] and "assert" in result["reason"]


def test_a_model_that_answers_nothing_is_broken_and_not_asked_again():
    """
    Given: A provider that fails
    When: The rule is proved
    Then: The rule is broken with the provider's reason after one call
    """
    def write(rule, feedback):
        raise page_tests.NoTest("RateLimitError: slow down")
    bench = _Bench([], [])
    result = prove(RULE, write=write, run=bench.run)
    assert (result["status"], result["reason"], bench.ran) == ("broken", "RateLimitError: slow down", [])


# ── what the test writer is shown ────────────────────────────────────────────

def _write(root, rel, text):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def test_the_writer_is_shown_the_api_and_the_page_the_app_serves(tmp_path):
    """
    Given: An app with one collection, a page of two files and a view nothing imports
    When: The app is described
    Then: The API names the collection with its class's fields and methods, and the page holds the served files only
    """
    root = str(tmp_path)
    _write(root, "src/entrypoints/routers/purchase_order.py",
           'from src.domain.purchase_order import PurchaseOrder\nrouter = APIRouter(prefix="/api/purchase_orders", tags=["x"])\n')
    _write(root, "src/domain/purchase_order.py",
           "from dataclasses import dataclass\n\n@dataclass\nclass PurchaseOrder:\n    id: str\n    status: str = 'draft'\n\n"
           "    def send(self, at: str) -> None:\n        self.status = 'sent'\n")
    _write(root, "src/main.tsx", "import App from './App';\n")
    _write(root, "src/App.tsx", "import { OrderView } from './views/OrderView';\nexport default function App() { return null; }\n")
    _write(root, "src/views/OrderView.tsx", "export const OrderView = () => <button>Send order</button>;\n")
    _write(root, "src/views/Unused.tsx", "export const Unused = () => <p>never shown</p>;\n")
    _write(root, "src/api/purchase_orderClient.ts", "export const BASE = '/api/purchase_orders';\n")

    app = describe_app(root)

    assert "purchase_orders" in app.api and "status: str = 'draft'" in app.api and "def send(self, at: str)" in app.api
    assert "self.status = 'sent'" not in app.api
    assert "Send order" in app.page and "src/views/OrderView.tsx" in app.page
    assert "never shown" not in app.page and "purchase_orderClient" not in app.page
    assert app.rendered == ""  # no address to open the page at: only its source is shown


def test_the_writer_is_shown_the_page_as_a_person_meets_it(tmp_path):
    """
    Given: An app, and a browser that reads out what the opened page offers
    When: The app is described with the address of its page
    Then: The description carries what was read out, so a control's name is one that was seen and not one guessed
    """
    seen = []

    def read_out(workspace_dir, page_url):
        seen.append((workspace_dir, page_url))
        return '- button "Send order"'

    app = describe_app(str(tmp_path), "http://page", read_out=read_out)
    assert app.rendered == '- button "Send order"' and seen == [(str(tmp_path), "http://page")]


def test_a_long_run_of_like_controls_is_shown_by_its_first_and_its_kinds_of_name():
    """
    Given: What a page of forty seats reads out, between a heading and a button
    When: It is condensed
    Then: The first seats stay as they are, the rest are one line that counts them and gives each kind of name
          they carry once, and everything around the run is unchanged
    """
    seats = [f'  - button "Seat {n}, {"taken" if n % 5 == 0 else "free"}"' for n in range(1, 41)]
    lines = condense("\n".join(['- heading "Evening show"', "- main:", *seats, '  - button "Book"'])).split("\n")

    assert lines[:5] == ['- heading "Evening show"', "- main:", *seats[:3]]
    assert lines[5] == '  - … 37 more button like these, named "Seat #, free" or "Seat #, taken"'
    assert lines[6:] == ['  - button "Book"']


def test_a_short_list_and_differing_controls_are_left_as_they_are():
    """
    Given: Three menu items in a row, and controls of different roles and names
    When: The listing is condensed
    Then: Nothing is taken away
    """
    listing = "\n".join(['- button "Save"', '- button "Send"', '- link "Help"', '- menuitem "Day 1"', '- menuitem "Day 2"', '- menuitem "Day 3"'])
    assert condense(listing) == listing


def test_the_page_as_it_opens_is_part_of_what_the_model_is_asked(monkeypatch):
    """
    Given: A description of an app with what its opened page reads out
    When: A test is written
    Then: The prompt carries that listing
    """
    import agent_orchestrator
    asked = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: asked.append(prompt) or "```python\n" + GOOD_TEST + "```")
    app = page_tests.AppDescription(api="API", page="PAGE", rendered='- button "Send order now"')
    page_tests.write_test({"title": "t", "given_when_then": "Given a When b Then c"}, app)
    assert '- button "Send order now"' in asked[0]


def test_the_harness_is_written_into_the_app_and_kept_current(tmp_path):
    """
    Given: An app without the harness, then one whose harness was edited
    When: The harness is ensured
    Then: tests/e2e/conftest.py holds the engine's harness both times
    """
    path = ensure_harness(str(tmp_path))
    assert path == os.path.join(str(tmp_path), "tests", "e2e", "conftest.py")
    with open(path, encoding="utf-8") as f:
        written = f.read()
    assert "def app(" in written
    with open(path, "w", encoding="utf-8") as f:
        f.write("# edited\n")
    ensure_harness(str(tmp_path))
    with open(path, encoding="utf-8") as f:
        assert f.read() == written


def test_the_situation_a_rule_starts_from_is_part_of_what_the_model_is_asked(monkeypatch):
    """
    Given: A rule that carries the situation its Given names, and one that carries none
    When: A test is written for each
    Then: The first prompt shows the situation with its values; the second has no line for one
    """
    import agent_orchestrator
    asked = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: asked.append(prompt) or "```python\n" + GOOD_TEST + "```")
    app = page_tests.AppDescription(api="API", page="PAGE")
    rule = {"title": "t", "given_when_then": "Given sent_order When b Then c"}

    page_tests.write_test({**rule, "situation": "`sent_order`: an order already sent: status sent, lines 2"}, app)
    page_tests.write_test(rule, app)

    assert "- **Situation** `sent_order`: an order already sent: status sent, lines 2" in asked[0]
    assert "**Situation**" not in asked[1]


SPECIFICATION = """# Table Booking

## Rules
- SPEC-001 [api] A booking holds its table: Given a free table, When it is booked, Then it is taken.

## The page
### 1. Opening
The floor plan shows every table free.

### 3. How each part is read out (role and name, used as written)
- Table · button · "Table {number}, {status wording}"

### 5. Refusals (the sentence is shown as written)
- (none)

### 6. Visual Direction
A warm, plain booking page.
TOKENS background=#faf6f1"""


def test_the_pages_plan_is_read_from_the_stored_specification():
    """
    Given: A product's stored specification with the page's plan in it, and one without
    When: The plan is read from each
    Then: The first gives the opening, the parts' names and the refusals, without the rules before it or the look
          after it; the second gives nothing
    """
    plan = page_tests.page_plan(SPECIFICATION)

    assert plan.startswith("### 1. Opening") and plan.endswith("- (none)")
    assert 'Table · button · "Table {number}, {status wording}"' in plan
    assert "SPEC-001" not in plan and "Visual Direction" not in plan and "TOKENS" not in plan
    assert page_tests.page_plan("A booking page for a restaurant.") == ""


def test_a_test_is_written_from_the_pages_plan_and_not_from_its_source(monkeypatch):
    """
    Given: An app described with the plan its page was built from, and one described without a plan
    When: A test is written for each
    Then: The first prompt holds the plan and none of the page's source, so nothing in the test can lean on how
          the page happens to be written; the second holds the source, the only account of the page there is
    """
    import agent_orchestrator
    asked = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: asked.append(prompt) or "```python\n" + GOOD_TEST + "```")
    rule = {"title": "t", "given_when_then": "Given a When b Then c"}

    page_tests.write_test(rule, page_tests.AppDescription(api="API", page="<button className='raised'>", plan='- Table · button · "Table 1, free"'))
    page_tests.write_test(rule, page_tests.AppDescription(api="API", page="<button className='raised'>"))

    assert "## The page's plan" in asked[0] and '- Table · button · "Table 1, free"' in asked[0]
    assert "className='raised'" not in asked[0] and "## The page's source" not in asked[0]
    assert "## The page's source" in asked[1] and "className='raised'" in asked[1] and "## The page's plan" not in asked[1]
