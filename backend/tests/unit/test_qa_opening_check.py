"""QA's last resort for a page that never gets going: it opens showing none of the parts its plan names.

A page listed its records, found none and showed its loading text for good. Its layout was tidy on three devices,
so QA passed it. What makes the first record is now the contract's and the client's (the `origin` of a record);
this check is for whatever else leaves a person in front of an empty page.
"""

import contextlib
from unittest.mock import MagicMock, patch

import pytest

from onboarding import code_verifier, page_gates
from onboarding.fresh_page import FreshPage
from onboarding.page_parts import parts_of
from onboarding.qa_opening_check import EMPTY, OpeningCheck, check_opening
from onboarding.qa_auditor import run_responsive_qa_audit

PLAN = '''### 3. How each part is read out (role and name, used as written)
- Basket · list · "Basket"
- Order · button · "Order"
- Total · status · "Total {amount}"
'''
STUCK = '<div id="root"><header><h1>Corner Kitchen</h1></header><main><p>Loading…</p></main></div>'
OPEN = '<div id="root"><main><ul aria-label="Basket"></ul><p>Nothing in the basket yet</p></main></div>'


def _driver(html):
    driver = MagicMock()
    driver.execute_script.return_value = html
    return driver


def test_a_page_that_opens_on_none_of_its_parts_is_a_defect():
    """
    id: TST-QA-OPENING-001
    Given: A plan of three parts, and a page whose opened document holds none of them
    When: The opening is checked
    Then: One defect says the page opens empty and names parts of the plan
    """
    check = check_opening(_driver(STUCK), "Desktop", parts_of(PLAN))
    assert check.on_screen == 0 and len(check.defects) == 1
    assert check.defects[0].startswith("[Desktop] " + EMPTY) and '"Basket"' in check.defects[0]


def test_a_page_that_opens_on_some_of_its_parts_passes():
    """
    id: TST-QA-OPENING-002
    Given: The same plan, and a page that opens on one of its parts (the others appear after a step)
    When: The opening is checked
    Then: Nothing is reported: which parts are there from the start is not this check's question
    """
    check = check_opening(_driver(OPEN), "Desktop", parts_of(PLAN))
    assert check.on_screen == 1 and check.defects == []


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_the_audit_checks_the_opening_once_when_it_is_given_the_parts(mock_chrome_cls, tmp_path, monkeypatch):
    """
    id: TST-QA-OPENING-003
    Given: A page with clean layout metrics whose opening check finds it empty
    When: The audit runs with the plan's parts, and again without any
    Then: With parts the opening is checked on the desktop and its defect fails the audit; without, it is not checked
    """
    mock_chrome_cls.return_value = MagicMock()
    mock_chrome_cls.return_value.execute_script.return_value = {
        "innerWidth": 375, "maxScrollWidth": 375, "hasHorizontalOverflow": False, "overflowDelta": 0,
        "hasCrashOverlay": False}
    for check in ("measure_contrast", "read_text", "exercise_forms"):
        monkeypatch.setattr(f"onboarding.qa_auditor.{check}", lambda driver, device: MagicMock(defects=[], warnings=[], outcomes=[]))
    ran = []

    def fake(driver, device, parts):
        ran.append((device, len(parts)))
        return OpeningCheck(defects=[f"[{device}] {EMPTY}nothing"], on_screen=0)
    monkeypatch.setattr("onboarding.qa_auditor.check_opening", fake)

    report = run_responsive_qa_audit(save_screenshots=False, output_dir=str(tmp_path), parts=parts_of(PLAN))
    assert ran == [("Desktop", 3)] and report["passed"] is False and report["defects"] == [f"[Desktop] {EMPTY}nothing"]

    ran.clear()
    assert run_responsive_qa_audit(save_screenshots=False, output_dir=str(tmp_path))["passed"] is True and ran == []


def test_the_gates_hand_the_audit_the_plans_parts(tmp_path, monkeypatch):
    """
    id: TST-QA-OPENING-004
    Given: A page with a plan of three parts
    When: The gates run their own audit
    Then: The audit is given those parts
    """
    given = {}

    def audit(**kw):
        given.update(kw)
        return {"passed": True, "defects": [], "console_errors": []}
    monkeypatch.setattr("onboarding.qa_auditor.run_responsive_qa_audit", audit)

    page_gates.run_page_gates(workspace_dir=str(tmp_path), pitch="p", presentation={"files": []}, ux_blueprint=PLAN,
                              page=lambda workspace_dir: contextlib.nullcontext(FreshPage("http://door", "http://api")))

    assert [part.what for part in given["parts"]] == ["Basket", "Order", "Total"]


def test_the_rework_of_an_empty_opening_is_shown_the_plan(tmp_path, monkeypatch):
    """
    id: TST-QA-OPENING-005
    Given: The defect of a page that opens empty, and the page's plan
    When: The rework is asked for a fix
    Then: Its prompt carries the plan
    """
    page = tmp_path / "src" / "App.tsx"
    page.parent.mkdir(parents=True)
    page.write_text("export default function App() { return null; }", encoding="utf-8")
    seen = {}

    def fake(prompt, stage="general", json_mode=False, **kw):
        seen["prompt"] = prompt
        return "<<<src/App.tsx>>>\nexport default function App() { return 1; }\n<<<end>>>\n"
    monkeypatch.setattr(code_verifier, "call_gemini", fake)

    code_verifier.self_heal_presentation_suite(
        workspace_dir=str(tmp_path), pitch="p", defects=[f"[Desktop] {EMPTY}nothing"], console_errors=[],
        component_files=[str(page)], plan=PLAN, compile_check=lambda ws, code: (True, ""))

    assert "### 3. How each part is read out" in seen["prompt"]
