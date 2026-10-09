import pytest
from unittest.mock import MagicMock, patch
from onboarding.qa_auditor import run_responsive_qa_audit, DEVICE_MATRIX
from onboarding.qa_contrast_check import ContrastCheck
from onboarding.qa_form_check import FormCheck
from onboarding.qa_type_check import TypeCheck


@pytest.fixture(autouse=True)
def form_checks(monkeypatch):
    """The form check has its own tests against a real browser; here it is a double that records who ran it."""
    ran = {"devices": [], "result": FormCheck()}

    def fake(driver, device):
        ran["devices"].append(device)
        return ran["result"]

    monkeypatch.setattr("onboarding.qa_auditor.exercise_forms", fake)
    return ran


@pytest.fixture(autouse=True)
def contrast_checks(monkeypatch):
    """The contrast check has its own tests; here it is a double that records who ran it."""
    ran = {"devices": [], "result": ContrastCheck()}

    def fake(driver, device):
        ran["devices"].append(device)
        return ran["result"]

    monkeypatch.setattr("onboarding.qa_auditor.measure_contrast", fake)
    return ran


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_fails_a_page_whose_text_cannot_be_read(mock_chrome_cls, tmp_path, contrast_checks):
    """Verify a page that fits every screen still fails the audit when its text cannot be seen.

    id: TST-QA-CONTRAST
    Given: A page with clean layout metrics on which the contrast check finds unreadable text
    When: The audit runs
    Then: The text is measured once (on the desktop) and what it found is a defect that fails the audit
    """
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver
    mock_driver.execute_script.return_value = {"innerWidth": 375, "maxScrollWidth": 375, "hasHorizontalOverflow": False,
                                               "overflowDelta": 0, "hasCrashOverlay": False}
    contrast_checks["result"] = ContrastCheck(defects=["[Desktop] Unreadable text: 16 text(s) are drawn in #f5f5f4"])

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert contrast_checks["devices"] == ["Desktop"]
    assert report["passed"] is False
    assert report["defects"] == ["[Desktop] Unreadable text: 16 text(s) are drawn in #f5f5f4"]


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_fails_a_page_that_contradicts_its_own_types(mock_chrome_cls, tmp_path, monkeypatch):
    """Verify a page that renders on every screen still fails the audit when the compiler refuses it.

    id: TST-QA-TYPES
    Given: A page with clean layout metrics, in a workspace whose type check reports an error and a warning
    When: The audit runs with that workspace, and again without one
    Then: With the workspace the error is a defect that fails the audit and the warning is reported; without one the
          types are not checked
    """
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver
    mock_driver.execute_script.return_value = {"innerWidth": 375, "maxScrollWidth": 375, "hasHorizontalOverflow": False,
                                               "overflowDelta": 0, "hasCrashOverlay": False}
    checked = []
    monkeypatch.setattr("onboarding.qa_auditor.check_types", lambda ws: checked.append(ws) or TypeCheck(
        defects=["[Types] src/App.tsx line 3: Property 'x' does not exist"], warnings=["the type check was slow"]))

    report = run_responsive_qa_audit(save_screenshots=False, output_dir=str(tmp_path), workspace_dir="ws")
    assert checked == ["ws"]
    assert report["passed"] is False and report["overall_status"] == "FAIL"
    assert report["defects"] == ["[Types] src/App.tsx line 3: Property 'x' does not exist"]
    assert report["warnings"] == ["the type check was slow"]

    assert run_responsive_qa_audit(save_screenshots=False, output_dir=str(tmp_path))["passed"] is True
    assert checked == ["ws"]


def test_qa_auditor_matrix_definitions():
    """Verifies standard multi-device matrix coverage (Mobile, Tablet, Desktop)."""
    device_names = [d["name"] for d in DEVICE_MATRIX]
    assert "Mobile" in device_names
    assert "Tablet" in device_names
    assert "Desktop" in device_names

    mobile_spec = next(d for d in DEVICE_MATRIX if d["name"] == "Mobile")
    assert mobile_spec["viewport"] == (375, 812)
    assert mobile_spec["is_mobile"] is True


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_passes_when_no_overflow_and_no_crash(mock_chrome_cls, tmp_path):
    """Hermetically tests that QA auditor passes when scrollWidth <= innerWidth."""
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver

    # Clean metrics: no horizontal overflow, no Vite error overlay
    mock_driver.execute_script.return_value = {
        "innerWidth": 375,
        "maxScrollWidth": 375,
        "hasHorizontalOverflow": False,
        "overflowDelta": 0,
        "hasCrashOverlay": False
    }

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert report["passed"] is True
    assert len(report["device_results"]) == 3
    assert len(report["defects"]) == 0
    assert report["device_results"][0]["device"] == "Mobile"
    assert report["device_results"][0]["passed"] is True


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_flags_horizontal_overflow_defects(mock_chrome_cls, tmp_path):
    """Hermetically tests that QA auditor flags horizontal overflow and marks passed=False."""
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver

    # Overflow metrics: scrollWidth 480px on 375px viewport
    mock_driver.execute_script.return_value = {
        "innerWidth": 375,
        "maxScrollWidth": 480,
        "hasHorizontalOverflow": True,
        "overflowDelta": 105,
        "hasCrashOverlay": False
    }

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert report["passed"] is False
    assert len(report["defects"]) > 0
    assert any("overflow" in d.lower() for d in report["defects"])
    assert report["device_results"][0]["passed"] is False


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_flags_vite_react_error_overlay(mock_chrome_cls, tmp_path):
    """Hermetically tests that QA auditor detects application crash overlays."""
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver

    mock_driver.execute_script.return_value = {
        "innerWidth": 375,
        "maxScrollWidth": 375,
        "hasHorizontalOverflow": False,
        "overflowDelta": 0,
        "hasCrashOverlay": True
    }

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert report["passed"] is False
    assert any("crash" in d.lower() or "error overlay" in d.lower() for d in report["defects"])


def test_qa_auditor_graceful_offline_fallback():
    """Verifies that if Chrome / WebDriver cannot connect, auditor gracefully returns SKIPPED_OFFLINE without crashing."""
    with patch("selenium.webdriver.Chrome", side_effect=Exception("No Chrome binary available")):
        report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False)
        assert report["passed"] is True
        assert report["overall_status"] == "SKIPPED_OFFLINE"


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_flags_vertical_overflow_defects(mock_chrome_cls, tmp_path):
    """Hermetically tests that QA auditor flags vertical overflow when check_vertical_containment=True."""
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver

    # Vertical overflow: scrollHeight 950px on 800px viewport
    mock_driver.execute_script.return_value = {
        "innerWidth": 1280,
        "innerHeight": 800,
        "maxScrollWidth": 1280,
        "maxScrollHeight": 950,
        "hasHorizontalOverflow": False,
        "overflowDelta": 0,
        "hasVerticalOverflow": True,
        "verticalOverflowDelta": 150,
        "hasCrashOverlay": False
    }

    report = run_responsive_qa_audit(
        url="http://localhost:5174",
        save_screenshots=False,
        output_dir=str(tmp_path),
        check_vertical_containment=True
    )

    assert report["passed"] is False
    assert len(report["defects"]) > 0
    assert any("vertical" in d.lower() for d in report["defects"])
    assert report["device_results"][0]["passed"] is False


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_saves_the_whole_page_not_only_the_first_screen(mock_chrome_cls, tmp_path):
    """Verify everything below the fold can be reviewed (the viewport shot showed 800 of 3,586 pixels).

    id: TST-QA-FULLPAGE
    Given: A page 3,000 CSS pixels tall on every device
    When: The audit runs with screenshots on
    Then: Each device gets a whole-page image, captured at one image pixel per CSS pixel, and how long it took
    """
    import base64
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver
    mock_driver.execute_script.return_value = {
        "innerWidth": 375, "maxScrollWidth": 375, "maxScrollHeight": 3000,
        "hasHorizontalOverflow": False, "overflowDelta": 0, "hasCrashOverlay": False}
    captures = []

    def cdp(command, params):
        if command == "Page.captureScreenshot":
            captures.append(params)
            return {"data": base64.b64encode(b"png-bytes").decode()}
        return {}

    mock_driver.execute_cdp_cmd.side_effect = cdp

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=True, output_dir=str(tmp_path))

    mobile = report["device_results"][0]
    assert mobile["full_page_screenshot"].endswith("qa_mobile_full.png")
    assert (tmp_path / "qa_mobile_full.png").read_bytes() == b"png-bytes"
    mobile_capture = next(c for c in captures if c["clip"]["width"] == 375)  # the devices run at the same time
    assert mobile_capture["captureBeyondViewport"] is True
    assert mobile_capture["clip"]["height"] == 3000 and abs(mobile_capture["clip"]["scale"] - 1 / 3) < 1e-9
    assert mobile["duration_s"] >= 0
    assert len(captures) == 3


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_reports_what_the_crash_overlay_says(mock_chrome_cls, tmp_path):
    """Verify a crash defect carries the compiler's message, so the rework is told what broke and where.

    id: TST-QA-OVERLAY
    Given: A page showing Vite's error overlay with a message and a file
    When: The audit runs
    Then: The defect quotes both, once per device
    """
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver
    mock_driver.execute_script.return_value = {
        "innerWidth": 375, "maxScrollWidth": 375, "hasHorizontalOverflow": False, "overflowDelta": 0,
        "hasCrashOverlay": True, "crashMessage": 'Unexpected "null"', "crashFile": "/src/components/Controls/X.tsx:15:22"}

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert report["passed"] is False
    crash = [d for d in report["defects"] if "error overlay" in d]
    assert len(crash) == 3
    assert 'Unexpected "null"' in crash[0] and "/src/components/Controls/X.tsx:15:22" in crash[0]


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_warns_about_text_cut_off_at_the_screen_edge(mock_chrome_cls, tmp_path):
    """Verify content clipped by an overflow-hidden ancestor is reported (the page does not scroll, so the overflow
    check cannot see it: price labels were cut off on phones and the audit passed in silence).

    id: TST-QA-CLIPPED
    Given: A page with no horizontal scroll where two labelled elements run past the screen edge
    When: The audit runs
    Then: It still passes, and it warns with the count and an example for each device
    """
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver
    mock_driver.execute_script.return_value = {
        "innerWidth": 375, "maxScrollWidth": 375, "hasHorizontalOverflow": False, "overflowDelta": 0,
        "hasCrashOverlay": False, "clippedCount": 2, "clippedSamples": ['span "$28/hr" ends at 398px']}

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert report["passed"] is True and report["defects"] == []
    assert len(report["warnings"]) == 3
    assert "2 element(s)" in report["warnings"][0] and '$28/hr' in report["warnings"][0] and "[Mobile]" in report["warnings"][0]


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_measures_overflow_against_the_device_width(mock_chrome_cls, tmp_path):
    """Verify each device's width is handed to the page measurement (window.innerWidth grows with overflowing content
    on a phone, so a page 76 px too wide measured as fitting and passed), and that the defect names what overflows.

    id: TST-QA-DEVICEWIDTH
    Given: The three devices, and a page that overflows with one labelled element past the edge
    When: The audit runs
    Then: The measurement script receives 375, 768 and 1280, and the overflow defect quotes the element
    """
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver
    mock_driver.execute_script.return_value = {
        "innerWidth": 375, "maxScrollWidth": 451, "hasHorizontalOverflow": True, "overflowDelta": 76,
        "hasCrashOverlay": False, "clippedCount": 1, "clippedSamples": ['span "Ages 4-11" ends at 450px']}

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert sorted(call.args[1] for call in mock_driver.execute_script.call_args_list) == [375, 768, 1280]
    assert "arguments[0]" in mock_driver.execute_script.call_args_list[0].args[0]
    overflow = [d for d in report["defects"] if "horizontal overflow" in d]
    assert overflow and 'span "Ages 4-11" ends at 450px' in overflow[0]


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_gives_each_device_its_own_browser_and_reports_them_in_order(mock_chrome_cls, tmp_path):
    """Verify the devices are audited side by side without sharing a browser, and the report keeps its order.

    id: TST-QA-PARALLEL
    Given: Three devices
    When: The audit runs
    Then: Three browsers are started and closed, and the results read Mobile, Tablet, Desktop
    """
    drivers = []

    def new_driver(*args, **kwargs):
        driver = MagicMock()
        driver.execute_script.return_value = {"innerWidth": 375, "maxScrollWidth": 375, "hasHorizontalOverflow": False,
                                              "overflowDelta": 0, "hasCrashOverlay": False}
        drivers.append(driver)
        return driver

    mock_chrome_cls.side_effect = new_driver
    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))
    assert len(drivers) == 3 and all(d.quit.called for d in drivers)
    assert [r["device"] for r in report["device_results"]] == ["Mobile", "Tablet", "Desktop"]
    assert report["passed"] is True


@patch("selenium.webdriver.Chrome")
@pytest.mark.slow
def test_qa_auditor_fails_a_page_whose_form_the_api_refuses(mock_chrome_cls, tmp_path, form_checks):
    """Verify a page that measures perfectly still fails the audit when using it does not work.

    id: TST-QA-FORMS
    Given: A page with clean layout metrics whose form submission is refused, and one form the check could not fill
    When: The audit runs
    Then: The forms are exercised once (on the desktop), the refusal is a defect that fails the audit, and the
          unfilled form is a warning
    """
    mock_driver = MagicMock()
    mock_chrome_cls.return_value = mock_driver
    mock_driver.execute_script.return_value = {"innerWidth": 375, "maxScrollWidth": 375, "hasHorizontalOverflow": False,
                                               "overflowDelta": 0, "hasCrashOverlay": False}
    form_checks["result"] = FormCheck(defects=['[Desktop] Submitting the form "Send" failed: POST /api/x answered 422: id required'],
                                      warnings=['[Desktop] the form check could not fill the form "Join"'])

    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False, output_dir=str(tmp_path))

    assert form_checks["devices"] == ["Desktop"]
    assert report["passed"] is False
    assert report["defects"] == ['[Desktop] Submitting the form "Send" failed: POST /api/x answered 422: id required']
    assert report["warnings"] == ['[Desktop] the form check could not fill the form "Join"']
    assert [r["passed"] for r in report["device_results"]] == [True, True, False]
