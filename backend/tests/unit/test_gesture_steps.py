"""A page test does a gesture through generated code that the page's gesture helper answers (vault: Shared Decisions
Inventory, row 2).

The page's helper recognises a fixed set of gestures (`src/api/gestures.ts`). A test's writer used to perform the
plan's gesture its own way: the plan said "both buttons or the middle button", the page bound both buttons, the test
clicked with the middle button, and nothing on the page answers that. The steps a test does a gesture with are now
written beside the helper, from the same set (`tests/e2e/gestures.py`).
"""
import json
import os
import subprocess
import sys
import textwrap

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding import page_gestures, page_tests

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TYPESCRIPT = os.path.join(REPO, "frontend", "node_modules", "typescript", "lib", "typescript.js")

TRANSPILE = r"""
const ts = require(process.argv[1]);
const source = require('fs').readFileSync(0, 'utf8');
process.stdout.write(ts.transpileModule(source, { compilerOptions: { module: 'commonjs', target: 'es2019' } }).outputText);
"""

# One square per gesture; the helper's handlers are attached the way React attaches the props it returns
SCRIPT = textwrap.dedent('''
    import json, sys
    from importlib.machinery import SourceFileLoader
    SourceFileLoader("page_test_harness", sys.argv[1]).load_module()
    gestures = SourceFileLoader("gestures", sys.argv[2]).load_module()
    helper = open(sys.argv[3], encoding="utf-8").read()
    from playwright.sync_api import sync_playwright

    PAGE = """
    <style>div { width: 40px; height: 40px; margin: 8px; background: #ccc; }</style>
    <div role="gridcell" aria-label="one"></div><div role="gridcell" aria-label="two"></div>
    <div role="gridcell" aria-label="three"></div><div role="gridcell" aria-label="four"></div>
    <div role="gridcell" aria-label="five"></div>
    <script>
    const module = { exports: {} }; const exports = module.exports;
    HELPER
    window.calls = {};
    const events = { onMouseDown: "mousedown", onMouseUp: "mouseup", onMouseLeave: "mouseleave", onClick: "click",
                     onDoubleClick: "dblclick", onContextMenu: "contextmenu", onTouchStart: "touchstart",
                     onTouchMove: "touchmove", onTouchEnd: "touchend", onTouchCancel: "touchcancel" };
    for (const cell of document.querySelectorAll("div")) {
      const name = cell.getAttribute("aria-label"), calls = window.calls[name] = [];
      const props = module.exports.gestures({
        click: () => calls.push("click"), secondary: () => calls.push("secondary"), double: () => calls.push("double"),
        both: () => calls.push("both"), press: (down) => calls.push(down ? "pressed" : "let go") });
      for (const [prop, event] of Object.entries(events)) cell.addEventListener(event, props[prop]);
    }
    </script>
    """.replace("HELPER", helper)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(PAGE)
        cell = lambda name: page.get_by_role("gridcell", name=name, exact=True)
        gestures.click(cell("one"))
        gestures.right_click(cell("two"))
        gestures.double_click(cell("three"))
        gestures.both_buttons(cell("four"))
        gestures.press(cell("five"))
        held = list(page.evaluate("window.calls.five"))
        gestures.release(cell("five"))
        out = {"calls": page.evaluate("window.calls"), "while_held": held}
        browser.close()
    print("RESULT=" + json.dumps(out))
''')


@pytest.mark.slow
def test_each_gesture_step_is_answered_by_the_pages_helper(tmp_path):
    """Verify the steps a test does gestures with, in a browser, against the page's helper.

    id: TST-GESTURE-STEPS
    Given: The page's gesture helper on five parts, and the page tests' harness
    When: A test clicks one, right-clicks one, double-clicks one, presses both buttons on one, and presses one and
          lets it go
    Then: Each part's helper answers with that gesture and no other; the pressed part is held until it is let go
    """
    if not os.path.exists(TYPESCRIPT):
        pytest.skip("frontend packages are not installed")
    compiled = subprocess.run(["node", "-e", TRANSPILE, TYPESCRIPT], input=page_gestures.GESTURES_TS,
                              capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert compiled.returncode == 0, compiled.stderr[-1500:]
    (tmp_path / "helper.js").write_text(compiled.stdout, encoding="utf-8")
    (tmp_path / "gestures.py").write_text(page_gestures.GESTURES_PY, encoding="utf-8")

    proc = subprocess.run([sys.executable, "-c", SCRIPT, page_tests._TEMPLATE, str(tmp_path / "gestures.py"),
                           str(tmp_path / "helper.js")], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = json.loads(next(l for l in proc.stdout.splitlines() if l.startswith("RESULT="))[len("RESULT="):])

    def answered(name):
        return [call for call in out["calls"][name] if call not in ("pressed", "let go")]

    assert answered("one") == ["click"]
    assert answered("two") == ["secondary"]
    assert "double" in answered("three") and not {"secondary", "both"} & set(answered("three"))
    assert answered("four") == ["both"]
    assert out["while_held"] == ["pressed"] and out["calls"]["five"][-1] in ("let go", "click")
    assert "let go" in out["calls"]["five"]


def test_the_gesture_steps_are_written_beside_the_parts(tmp_path):
    """Verify a page test can import the gesture steps wherever it can import the parts.

    id: TST-GESTURE-STEPS-WRITTEN
    Given: A plan that names a part
    When: The parts are written for the page tests
    Then: The gesture steps are written beside them, as generated
    """
    page_tests.ensure_parts(str(tmp_path), '### 3. Parts\n- Square · gridcell · "Row {row}"\n')

    written = tmp_path / "tests" / "e2e" / "gestures.py"
    assert written.read_text(encoding="utf-8") == page_gestures.GESTURES_PY


def test_a_test_writer_is_told_to_do_every_gesture_through_the_steps(monkeypatch):
    """Verify the page test's writer is given the gesture steps and nothing else to do a gesture with.

    id: TST-GESTURE-STEPS-PROMPT
    Given: An app description
    When: A page test is written
    Then: The prompt names every step and says a gesture outside them is answered by nothing on the page
    """
    import agent_orchestrator
    asked = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini",
                        lambda prompt, stage="general", **k: asked.append(prompt) or
                        "```python\ndef test_x(app):\n    assert app.open()\n```")
    page_tests.write_test({"title": "t", "given_when_then": "Given a When b Then c"},
                          page_tests.AppDescription(api="API", page="PAGE"))

    for step in ("gestures.click(", "gestures.right_click(", "gestures.double_click(", "gestures.both_buttons(",
                 "gestures.press(", "gestures.release("):
        assert step in asked[0]
    assert "answered by nothing" in asked[0]
