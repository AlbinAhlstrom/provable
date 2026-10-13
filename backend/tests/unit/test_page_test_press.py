"""A page test presses as long as a person does (templates/page_test_conftest.py.tmpl).

A generated page closed its menu 150 ms after a press on one of its items began. A test's click is over in no time,
so every rule about the menu passed, and a person, whose press lasts longer, chose a level about one time in three.
"""
import json
import os
import subprocess
import sys
import textwrap

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding import page_tests

# Run on its own: the harness changes how every click of its process is made
SCRIPT = textwrap.dedent('''
    import json, sys
    from importlib.machinery import SourceFileLoader
    harness = SourceFileLoader("page_test_harness", sys.argv[1]).load_module()
    from playwright.sync_api import sync_playwright

    PAGE = """
    <button id="plain" onmousedown="window.down = performance.now()" onmouseup="window.held = performance.now() - window.down"
            onclick="window.plainClicks = (window.plainClicks || 0) + 1">Plain</button>
    <button id="leaving" onmousedown="setTimeout(() => document.getElementById('leaving').remove(), 150)"
            onclick="window.leavingClicked = true">Leaving</button>
    <button id="quick" onmousedown="window.quickDown = performance.now()"
            onmouseup="window.quickHeld = performance.now() - window.quickDown">Quick</button>
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(PAGE)
        page.get_by_role("button", name="Plain").click()
        page.click("#leaving")
        page.get_by_role("button", name="Quick").click(delay=0)
        out = page.evaluate("({held: window.held, plain: window.plainClicks, leaving: window.leavingClicked === true, quick: window.quickHeld})")
        browser.close()
    print("RESULT=" + json.dumps({**out, "press_ms": harness.PRESS_MS}))
''')


@pytest.mark.slow
def test_a_click_is_held_as_long_as_a_person_holds_it():
    """
    id: TST-PAGE-TEST-PRESS
    Given: The harness of the page tests, and a page with a plain button, one that is taken away 150 ms after a
           press on it begins, and a third
    When: A test clicks the first two without saying how long, and the third saying it is let go at once
    Then: The press on the plain button lasted as long as the harness says a person's does and counted once; the
          button that left under the press was never clicked, as it would not be for a person; a test that says
          how long a press lasts is taken at its word
    """
    proc = subprocess.run([sys.executable, "-c", SCRIPT, page_tests._TEMPLATE], capture_output=True, text=True, timeout=90)
    assert proc.returncode == 0, proc.stderr[-1500:]
    out = json.loads(next(l for l in proc.stdout.splitlines() if l.startswith("RESULT="))[len("RESULT="):])

    assert out["press_ms"] >= 200
    assert out["held"] >= out["press_ms"] - 20
    assert out["plain"] == 1
    assert out["leaving"] is False
    assert out["quick"] < 100
