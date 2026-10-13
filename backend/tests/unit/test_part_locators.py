"""A page test finds a part of the page through a function written from the plan (onboarding/page_parts.py).

The plan names each part by role and name, and the page's writer and the test's writer each copied that line into
code of their own. A test's writer copied it wrong in a way no rule is about: it looked for a status by its text
where the plan gives it a name, so a rule the app kept was reported as not held. The line is now turned into the
locator by code, once, and a test calls it.
"""
import os

from onboarding import page_tests
from onboarding.page_parts import locators_block, locators_module, part_functions, parts_of

PLAN = '''### 3. How each part is read out (role and name, used as written)
- Basket · list · "Basket"
- Line · listitem · "{quantity} x {dish}"
- Order · button · "Order"
- Total · status · "Total {amount}"
- Table · button · "Table {number}, {status wording}"
- Order · menuitem · "Order again"
- Class · textbox · "Class"
- 2nd guest · textbox · "Guest's "other" name"
'''


class Page:
    """Stands in for a Playwright page or locator: notes how a part was looked for."""
    def get_by_role(self, role, **how):
        return (role, how)


def _module():
    scope = {}
    exec(compile(locators_module(parts_of(PLAN)), "parts.py", "exec"), scope)
    return scope


def test_each_part_has_a_function_named_after_what_it_is():
    """
    id: TST-LOCATOR-001
    Given: A plan with eight parts: two that are called the same, one called by a word Python keeps for itself, one
           whose name starts with a digit, and names with values in braces
    When: The parts' functions are read out
    Then: Each part has a function of its own, named after what the part is in a form Python accepts, and takes
          the values of its name as arguments named after them
    """
    functions = part_functions(parts_of(PLAN))

    assert [f.name for f in functions] == ["basket", "line", "order", "total", "table", "order_menuitem", "class_",
                                           "part_2nd_guest"]
    assert [f.slots for f in functions][:5] == [[], ["quantity", "dish"], [], ["amount"], ["number", "status_wording"]]


def test_a_function_finds_its_part_by_its_role_and_its_whole_name():
    """Verify the locator is the plan's line and nothing else, whatever a test's writer would have made of it.

    id: TST-LOCATOR-002
    Given: The module written from the plan
    When: A part without values, a part with two values and a part whose name holds quotation marks are looked for
    Then: Each is looked for by the role of its line and the name of its line with the values filled in, matched
          whole; a value that is left out is an error, not a name with a gap
    """
    parts = _module()
    page = Page()

    assert parts["order"](page) == ("button", {"name": "Order", "exact": True})
    assert parts["table"](page, number=4, status_wording="free") == ("button", {"name": "Table 4, free", "exact": True})
    assert parts["line"](page, quantity=2, dish="soup") == ("listitem", {"name": "2 x soup", "exact": True})
    assert parts["part_2nd_guest"](page) == ("textbox", {"name": 'Guest\'s "other" name', "exact": True})
    try:
        parts["table"](page, number=4)
    except TypeError:
        pass
    else:
        raise AssertionError("a part was looked for without one of the values its name is built from")


def test_the_test_writer_is_shown_each_part_as_the_call_that_finds_it(monkeypatch):
    """
    id: TST-LOCATOR-003
    Given: An app described with its page's plan, and one described without a plan
    When: A test is written for each
    Then: The first prompt lists every part as the call that finds it, beside the line it stands for; the second
          names no such module, since nothing was written from a plan
    """
    import agent_orchestrator
    asked = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini",
                        lambda prompt, stage="general", **k: asked.append(prompt) or "```python\ndef test_x(app):\n    pass\n```")
    rule = {"title": "t", "given_when_then": "Given a When b Then c"}

    page_tests.write_test(rule, page_tests.AppDescription(api="API", page="PAGE", plan=PLAN))
    page_tests.write_test(rule, page_tests.AppDescription(api="API", page="PAGE"))

    block = locators_block(parts_of(PLAN))
    assert block in asked[0]
    assert '`parts.table(page, number=..., status_wording=...)`: button "Table {number}, {status wording}"' in block
    assert "`parts.order(page)`: button \"Order\"" in block and "import parts" in block
    assert "import parts" not in asked[1] and "{parts_block}" not in asked[1]
    assert locators_block([]) == ""


def test_the_functions_are_written_beside_the_tests_before_a_rule_is_proved(tmp_path):
    """
    id: TST-LOCATOR-004
    Given: An app, the plan of its page, and a rule with a stored test that finds a part through its function
    When: The rule is proved
    Then: tests/e2e/parts.py holds the functions of the plan before the test runs, and an app whose plan names no
          part gets no such file
    """
    held = {}
    path = os.path.join(str(tmp_path), "tests", "e2e", "parts.py")

    def run(workspace_dir, spec_id, source, page_url):
        held["there"] = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        return page_tests.Verdict(page_tests.PASS)

    original, page_tests.run_test = page_tests.run_test, run
    try:
        rule = {"spec_id": "SPEC-001", "title": "t", "given_when_then": "Given a When b Then c"}
        stored = {"source": "import parts\n", "status": "pass", "written_for": page_tests.rule_text(rule)}
        page_tests.prove_rule(rule, str(tmp_path), "http://page", stored=stored, plan=PLAN)
        with_plan = held["there"]
        os.remove(path)
        page_tests.prove_rule(rule, str(tmp_path), "http://page", stored=stored, plan="### 1. Opening\nA calm page.")
    finally:
        page_tests.run_test = original

    assert with_plan == locators_module(parts_of(PLAN))
    assert held["there"] is None
