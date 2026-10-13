"""A part that opens over the page and closes again is kept open and closed by generated code (onboarding/page_opening.py).

Left to write it, the page's writer closed a menu on a timer started when its opener lost focus: 150 ms after a
press on an item began, the item was gone. A person's press lasts longer, so a choice from the menu was made about
one time in three. The helper is run here in Node, on a stand-in for React that calls it again after every change.
"""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding import page_opening

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TYPESCRIPT = os.path.join(REPO, "frontend", "node_modules", "typescript", "lib", "typescript.js")

RUNNER = r"""
const ts = require(process.argv[1]);
const source = require('fs').readFileSync(0, 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: 'commonjs', target: 'es2019' } }).outputText;

// React, as far as the helper uses it: state that is kept, an effect run again when what it depends on changed
let state, hasState = false, deps, cleanup = null;
const ref = { current: null };
const react = {
  useState: (first) => { if (!hasState) { state = first; hasState = true; } return [state, (next) => { state = typeof next === 'function' ? next(state) : next; }]; },
  useRef: () => ref,
  useEffect: (effect, now) => {
    if (deps && now.every((d, i) => d === deps[i])) return;
    if (cleanup) cleanup();
    deps = now;
    cleanup = effect() || null;
  },
};
const listeners = {};
const document = {
  addEventListener: (kind, fn) => { (listeners[kind] = listeners[kind] || []).push(fn); },
  removeEventListener: (kind, fn) => { listeners[kind] = (listeners[kind] || []).filter((l) => l !== fn); },
};
const mod = { exports: {} };
new Function('module', 'exports', 'require', 'document', compiled)(mod, mod.exports, () => react, document);

const inside = { name: 'inside' }, outside = { name: 'outside' };
ref.current = { contains: (target) => target === inside };
const send = (kind, event) => (listeners[kind] || []).slice().forEach((l) => l(event));
const listening = () => Object.values(listeners).reduce((n, l) => n + l.length, 0);

const results = {};
for (const [name, steps] of Object.entries(JSON.parse(process.argv[2]))) {
  hasState = false; deps = undefined; if (cleanup) cleanup(); cleanup = null;
  let part = mod.exports.useOpening();
  const seen = [];
  for (const step of steps) {
    if (step === 'toggle') part.toggle();
    else if (step === 'close') part.close();
    else if (step === 'press inside') send('pointerdown', { target: inside });
    else if (step === 'press outside') send('pointerdown', { target: outside });
    else send('keydown', { key: step });
    part = mod.exports.useOpening();
    seen.push(part.open);
  }
  results[name] = { seen, listening: listening() };
}
console.log('RESULT=' + JSON.stringify(results));
"""

SEQUENCES = {
    "opened and closed by its control": ["toggle", "toggle"],
    "a press inside leaves it open": ["toggle", "press inside"],
    "a press outside closes it": ["toggle", "press outside"],
    "Escape closes it": ["toggle", "Escape"],
    "another key leaves it open": ["toggle", "Enter"],
    "closed by a choice": ["toggle", "close"],
    "a press outside while closed": ["press outside"],
}


@pytest.fixture(scope="module")
def kept():
    if not os.path.exists(TYPESCRIPT):
        pytest.skip("frontend packages are not installed")
    run = subprocess.run(["node", "-e", RUNNER, TYPESCRIPT, json.dumps(SEQUENCES)], input=page_opening.OPENING_TS,
                         capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert run.returncode == 0, run.stderr[-2000:]
    return json.loads(next(line for line in run.stdout.splitlines() if line.startswith("RESULT="))[len("RESULT="):])


@pytest.mark.parametrize("what, seen", [
    ("opened and closed by its control", [True, False]),
    ("a press inside leaves it open", [True, True]),
    ("a press outside closes it", [True, False]),
    ("Escape closes it", [True, False]),
    ("another key leaves it open", [True, True]),
    ("closed by a choice", [True, False]),
    ("a press outside while closed", [False]),
])
def test_the_part_is_open_until_it_is_closed_or_a_press_lands_outside_it(kept, what, seen):
    """Verify what opens stays open through a press on it, however long the press lasts: nothing closes it but its
    own control, a choice, Escape, or a press that begins outside it.

    id: TST-OPENING-001
    Given: The generated helper, with an element that holds the part
    When: The steps are taken, one after another
    Then: The part is open or closed after each step as listed
    """
    assert kept[what]["seen"] == seen


def test_the_page_is_listened_to_only_while_the_part_is_open(kept):
    """
    id: TST-OPENING-002
    Given: The helper
    When: The part has been opened and closed again, and when it was left open
    Then: Nothing listens to the page after it closed; presses and keys are listened for while it is open
    """
    assert kept["a press outside closes it"]["listening"] == 0
    assert kept["closed by a choice"]["listening"] == 0
    assert kept["a press inside leaves it open"]["listening"] == 2


def test_the_page_writer_is_told_of_the_helper_and_it_is_written_with_the_clients():
    """Verify the helper reaches the page: it is described in the prompt, in no one product's words, and written
    beside the API clients.

    id: TST-OPENING-003
    Given: The page prompt and the page synthesizer
    When: They are read
    Then: The prompt has the helper's place; the description names its file, the hook and what it returns; the
          synthesizer writes the file with the clients
    """
    prompt = open(os.path.join(REPO, "backend", "prompts", "presentation_projection_synthesis.md"), encoding="utf-8").read()
    synthesizer = open(os.path.join(REPO, "backend", "onboarding", "presentation_projection_synthesizer.py"), encoding="utf-8").read()

    assert "{opening_block}" in prompt
    block = page_opening.opening_block()
    assert f"src/api/{page_opening.FILE_NAME}" in block
    assert all(name in block for name in ("useOpening", "open", "toggle", "close", "within"))
    assert "client_files[page_opening.FILE_NAME] = page_opening.OPENING_TS" in synthesizer
    assert '"{opening_block}": page_opening.opening_block()' in synthesizer
