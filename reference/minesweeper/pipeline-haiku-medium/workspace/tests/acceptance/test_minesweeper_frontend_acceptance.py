"""
Universal Presentation Acceptance Test Suite for Minesweeper.
Automated QA gate enforcing non-blank mount, zero console exceptions, and viewport containment.
"""

import pytest
from onboarding.qa_auditor import run_responsive_qa_audit


def test_frontend_renders_without_blank_screen():
    """Spec: When the app is loaded, the DOM must mount child elements into #root."""
    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False)
    for dev in report.get("device_results", []):
        metrics = dev.get("metrics", {})
        assert not metrics.get("isRootEmpty"), (
            f"Blank screen detected on device {dev.get('device')}: #root has 0 children"
        )


def test_frontend_has_zero_console_exceptions():
    """Spec: The browser console must be free of SEVERE runtime errors or crash overlays."""
    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False)
    assert not report.get("console_errors"), (
        f"Console errors detected: {report.get('console_errors')}"
    )
    for dev in report.get("device_results", []):
        metrics = dev.get("metrics", {})
        assert not metrics.get("hasCrashOverlay"), (
            f"Vite/React crash overlay present on {dev.get('device')}"
        )


def test_frontend_satisfies_viewport_containment():
    """Spec: Document layout must not cause horizontal blowout beyond device viewport."""
    report = run_responsive_qa_audit(url="http://localhost:5174", save_screenshots=False)
    for dev in report.get("device_results", []):
        metrics = dev.get("metrics", {})
        assert not metrics.get("hasHorizontalOverflow"), (
            f"Horizontal overflow detected on {dev.get('device')}: {dev.get('defects')}"
        )
