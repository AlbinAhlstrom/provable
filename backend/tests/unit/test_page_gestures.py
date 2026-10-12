"""The gestures of a part are recognised by generated code, not by the page's writer (onboarding/page_gestures.py).

A plan gives an action several gestures (a click or a tap, a right click or a long press, two buttons at once or a
double click). Asked to write them, the page's writer wrote the ones the browser has an event for and left out the
rest: two buttons at once in none of 7 answers on one contract, and again in a kickstart after the prompt said how. The helper is run here in Node on the events a browser
sends, in the order it sends them.
"""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding import page_gestures

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TYPESCRIPT = os.path.join(REPO, "frontend", "node_modules", "typescript", "lib", "typescript.js")

RUNNER = r"""
const ts = require(process.argv[1]);
const source = require('fs').readFileSync(0, 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: 'commonjs', target: 'es2019' } }).outputText;
const mod = { exports: {} };
let timers = [];
const fakeSetTimeout = (fn, ms) => { timers.push({ fn, ms }); return timers.length; };
const fakeClearTimeout = (id) => { if (id) timers[id - 1] = null; };
new Function('module', 'exports', 'setTimeout', 'clearTimeout', compiled)(mod, mod.exports, fakeSetTimeout, fakeClearTimeout);
const elapse = () => { const due = timers; timers = []; due.forEach((t) => t && t.fn()); };
const event = (buttons) => ({ buttons, prevented: false, preventDefault() { this.prevented = true; } });
const results = {};
for (const [name, steps] of Object.entries(JSON.parse(process.argv[2]))) {
  const calls = [];
  const props = mod.exports.gestures({
    click: () => calls.push('click'), secondary: () => calls.push('secondary'),
    double: () => calls.push('double'), both: () => calls.push('both'),
  });
  let prevented = false;
  for (const [what, buttons] of steps) {
    if (what === 'elapse') { elapse(); continue; }
    const e = event(buttons || 0);
    props[what](e);
    prevented = prevented || e.prevented;
  }
  results[name] = { calls, prevented };
}
console.log('RESULT=' + JSON.stringify(results));
"""

SEQUENCES = {
    # what a browser sends for each gesture, in order
    "left click": [["onMouseDown", 1], ["onMouseUp", 0], ["onClick", 0]],
    "right click": [["onMouseDown", 2], ["onMouseUp", 0], ["onContextMenu", 0]],
    "double click": [["onMouseDown", 1], ["onMouseUp", 0], ["onClick", 0],
                     ["onMouseDown", 1], ["onMouseUp", 0], ["onClick", 0], ["onDoubleClick", 0]],
    "left then right held together": [["onMouseDown", 1], ["onMouseDown", 3], ["onMouseUp", 1], ["onContextMenu", 1],
                                      ["onMouseUp", 0], ["onClick", 0]],
    "right then left held together": [["onMouseDown", 2], ["onMouseDown", 3], ["onMouseUp", 2], ["onClick", 2],
                                      ["onMouseUp", 0], ["onContextMenu", 0]],
    "a click after two buttons": [["onMouseDown", 1], ["onMouseDown", 3], ["onMouseUp", 1], ["onMouseUp", 0],
                                  ["onMouseDown", 1], ["onMouseUp", 0], ["onClick", 0]],
    "tap": [["onTouchStart", 0], ["onTouchEnd", 0], ["onClick", 0]],
    "long press": [["onTouchStart", 0], ["elapse", 0], ["onTouchEnd", 0], ["onClick", 0]],
    "long press where the browser also opens a menu": [["onTouchStart", 0], ["elapse", 0], ["onContextMenu", 0], ["onTouchEnd", 0]],
    "a finger that moves is no long press": [["onTouchStart", 0], ["onTouchMove", 0], ["elapse", 0], ["onTouchEnd", 0]],
}


@pytest.fixture(scope="module")
def recognised():
    if not os.path.exists(TYPESCRIPT):
        pytest.skip("frontend packages are not installed")
    run = subprocess.run(["node", "-e", RUNNER, TYPESCRIPT, json.dumps(SEQUENCES)], input=page_gestures.GESTURES_TS,
                         capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert run.returncode == 0, run.stderr[-2000:]
    return json.loads(next(line for line in run.stdout.splitlines() if line.startswith("RESULT="))[len("RESULT="):])


@pytest.mark.parametrize("gesture, calls", [
    ("left click", ["click"]),
    ("right click", ["secondary"]),
    ("double click", ["click", "click", "double"]),
    ("left then right held together", ["both"]),
    ("right then left held together", ["both"]),
    ("a click after two buttons", ["both", "click"]),
    ("tap", ["click"]),
    ("long press", ["secondary"]),
    ("long press where the browser also opens a menu", ["secondary"]),
    ("a finger that moves is no long press", []),
])
def test_each_gesture_is_recognised_once_and_as_itself(recognised, gesture, calls):
    """Verify the events of one gesture call that gesture's handler once and no other.

    id: TST-GESTURE-001
    Given: The generated helper with a handler for a click, a secondary press, a double click and two buttons at once
    When: It is sent the events a browser sends for the gesture
    Then: Exactly the handlers named were called, in that order
    """
    assert recognised[gesture]["calls"] == calls


def test_the_browsers_own_menu_never_opens_on_a_part_with_gestures(recognised):
    """
    id: TST-GESTURE-002
    Given: The helper
    When: A right click arrives, alone or as the end of two buttons held together
    Then: The browser's menu is prevented both times
    """
    assert recognised["right click"]["prevented"] and recognised["left then right held together"]["prevented"]


def test_the_page_writer_is_told_to_use_the_helper_and_it_is_written_with_the_clients(tmp_path, monkeypatch):
    """Verify the helper reaches the page: it is described in the prompt and written beside the API clients.

    id: TST-GESTURE-003
    Given: The page prompt and the helper's file name
    When: The prompt is read
    Then: It names the helper's file and its four gestures, and says nothing of recognising a gesture by hand
    """
    prompt = open(os.path.join(REPO, "backend", "prompts", "presentation_projection_synthesis.md"), encoding="utf-8").read()

    assert "{gestures_block}" in prompt and "event.buttons" not in prompt
    block = page_gestures.gestures_block()
    assert f"src/api/{page_gestures.FILE_NAME}" in block
    assert all(name in block for name in ("click", "secondary", "double", "both"))
