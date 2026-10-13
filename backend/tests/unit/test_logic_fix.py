"""Fixing a red rule whose fault is in what the app does (onboarding/logic_fix.py): the record's class is changed
through the test-first loop, from the situation the page test failed in, and kept only when the page agrees."""
import os

from onboarding import logic_fix
from onboarding.rule_fix import Check

RULE = {"spec_id": "SPEC-007", "title": "The last line settles an order", "action": "settle_line",
        "target_aggregate": "Order", "description": "What the person sees: \"Settled\"",
        "given_when_then": "Given one_line_open, When settle_line(line 2), Then status settled",
        "situation": "`one_line_open`: an order of two lines, the first settled"}
RED = {"status": "fail", "reason": "AssertionError: Locator expected to be visible", "evidence": "waiting for Settled",
       "seen": "POST /api/orders/o1/action answered 200: status open",
       "source": "def test_settles(app):\n    app.given('orders', lines=[{'settled': True}, {'settled': False}])\n"}
OLD_CLASS, OLD_TEST = "class Order:\n    status = 'open'\n", "def test_old():\n    assert True\n"
NEW_CLASS, NEW_TEST = "class Order:\n    status = 'settled'\n", "def test_new():\n    assert True\n"
MANIFEST = {"actions": [{"name": "settle_line", "aggregate": "Order"}]}


def _workspace(tmp_path) -> str:
    os.makedirs(tmp_path / "src" / "domain")
    os.makedirs(tmp_path / "tests" / "unit")
    (tmp_path / "src" / "domain" / "order.py").write_text(OLD_CLASS, encoding="utf-8")
    (tmp_path / "tests" / "unit" / "test_spec_007.py").write_text(OLD_TEST, encoding="utf-8")
    return str(tmp_path)


def _files(workspace: str):
    read = lambda *parts: open(os.path.join(workspace, *parts), encoding="utf-8").read()
    return read("src", "domain", "order.py"), read("tests", "unit", "test_spec_007.py")


class _Loop:
    """The test-first loop: writes a new test and, when it succeeds, a new class."""

    def __init__(self, success: bool, error: str = ""):
        self.success, self.error, self.given = success, error, []

    def __call__(self, spec, workspace_dir, action_manifest=None):
        self.given.append((spec, action_manifest))
        with open(os.path.join(workspace_dir, "tests", "unit", "test_spec_007.py"), "w", encoding="utf-8") as f:
            f.write(NEW_TEST)
        if self.success:
            with open(os.path.join(workspace_dir, "src", "domain", "order.py"), "w", encoding="utf-8") as f:
                f.write(NEW_CLASS)
            return {"success": True, "status": "FULFILLED", "attempts": [{"attempt": 1, "approved": True, "reason": None}]}
        os.remove(os.path.join(workspace_dir, "tests", "unit", "test_spec_007.py"))  # the loop sets a failed test aside
        return {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "error": self.error,
                "attempts": [{"attempt": 1, "approved": False, "reason": self.error}]}


def test_the_loop_is_given_the_rule_with_the_situation_the_page_test_failed_in(tmp_path):
    """
    Given: A red rule, its page test and what the app held when the test ended
    When: The logic is fixed and the page agrees
    Then: The loop was handed the rule as a spec of its class, with the page test and what the app held in what the
          test writer reads, and the manifest; the new class and the new unit test are kept and named
    """
    workspace, loop = _workspace(tmp_path), _Loop(success=True)

    result = logic_fix.fix_logic(RULE, RED, workspace, MANIFEST, check=lambda: Check(ok=True), loop=loop)

    (spec, manifest), = loop.given
    assert (spec.spec_id, spec.target_aggregate, spec.action) == ("SPEC-007", "Order", "settle_line")
    assert spec.given_when_then == RULE["given_when_then"] and spec.situation == RULE["situation"]
    assert RULE["description"] in spec.description
    assert "app.given('orders'" in spec.description and RED["seen"] in spec.description
    assert manifest == MANIFEST
    assert (result["status"], result["reason"]) == ("fixed", None)
    assert result["files"] == ["src/domain/order.py", "tests/unit/test_spec_007.py"]
    assert _files(workspace) == (NEW_CLASS, NEW_TEST)


def test_a_change_the_page_test_does_not_accept_is_taken_back(tmp_path):
    """
    Given: A loop that changes the class and passes its own tests
    When: The rule's page test still fails afterwards
    Then: The class and the rule's unit test are as they were, and the answer says what the page test said
    """
    workspace = _workspace(tmp_path)
    check = lambda: Check(ok=False, reason="the rule's test still does not pass: AssertionError")

    result = logic_fix.fix_logic(RULE, RED, workspace, MANIFEST, check=check, loop=_Loop(success=True))

    assert result["status"] == "not_fixed" and "still does not pass" in result["reason"] and result["files"] == []
    assert _files(workspace) == (OLD_CLASS, OLD_TEST)


def test_a_loop_that_does_not_reach_green_leaves_the_rules_unit_test_as_it_was(tmp_path):
    """
    Given: A loop that fails because its change breaks the tests of other rules
    When: The logic is fixed
    Then: The page is never checked, the rule's unit test is back, and the answer carries the loop's reason
    """
    workspace, checked = _workspace(tmp_path), []
    loop = _Loop(success=False, error="Regression: your change makes earlier tests fail again: test_spec_004.py")

    result = logic_fix.fix_logic(RULE, RED, workspace, MANIFEST, check=lambda: checked.append(1), loop=loop)

    assert result["status"] == "not_fixed" and "test_spec_004.py" in result["reason"] and checked == []
    assert _files(workspace) == (OLD_CLASS, OLD_TEST)
    assert result["attempts"] == [{"number": 1, "ok": False, "reason": loop.error}]


def test_a_loop_that_crashes_leaves_everything_as_it_was_and_says_why(tmp_path):
    """
    Given: A loop that raises (a provider error)
    When: The logic is fixed
    Then: Nothing is retried, the files are as they were and the answer carries the error
    """
    workspace = _workspace(tmp_path)

    def loop(spec, workspace_dir, action_manifest=None):
        with open(os.path.join(workspace_dir, "src", "domain", "order.py"), "w", encoding="utf-8") as f:
            f.write(NEW_CLASS)
        raise RuntimeError("GREEN synthesis failed: APITimeoutError")

    result = logic_fix.fix_logic(RULE, RED, workspace, MANIFEST, check=lambda: Check(ok=True), loop=loop)

    assert result["status"] == "not_fixed" and "APITimeoutError" in result["reason"]
    assert _files(workspace) == (OLD_CLASS, OLD_TEST)


def test_the_tests_a_change_broke_are_passed_on(tmp_path):
    """
    Given: A loop that ends because its change broke another rule's test, and says which
    When: The logic is fixed
    Then: The answer names the broken tests
    """
    def loop(spec, workspace_dir, action_manifest=None):
        return {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "error": "Regression", "attempts": [],
                "broke": ["test_spec_004.py"]}

    result = logic_fix.fix_logic(RULE, RED, _workspace(tmp_path), MANIFEST, check=lambda: Check(ok=True), loop=loop)

    assert (result["status"], result["broke"]) == ("not_fixed", ["test_spec_004.py"])
