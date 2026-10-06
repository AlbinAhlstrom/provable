import pytest
from unittest.mock import MagicMock, patch
from onboarding.qa_auditor import run_responsive_qa_audit, DEVICE_MATRIX


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
