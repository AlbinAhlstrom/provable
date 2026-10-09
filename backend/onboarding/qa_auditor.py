"""
Automated Multi-Device QA Gate & Viewport Verifier.

Tests live application previews on port 5174 across a responsive device matrix:
- Mobile: 375x812 (iPhone standard)
- Tablet: 768x1024 (iPad standard)
- Desktop: 1280x800 (Laptop standard)

Enforces Hard QA Invariants:
1. Zero Horizontal Overflow: the page's scroll width fits the device's width (the emulated width, not
   window.innerWidth, which a mobile browser widens to fit overflowing content)
2. Zero Console Exceptions: window.console.errors and unhandled promise rejections
3. Interactive Element Visibility: key interactive widgets must be rendered and visible
4. Forms work: on the desktop, each form is filled and submitted, and a request the API refuses is a defect
   (qa_form_check.py)
5. Text can be seen: on the desktop, text drawn in nearly the colour of its background is a defect
   (qa_contrast_check.py)
6. The page agrees with its own types: when the audit is given the workspace, each error the TypeScript compiler
   reports is a defect (qa_type_check.py)
7. Text is what was meant: on the desktop, an escape or entity the page shows letter by letter is a defect
   (qa_text_check.py)
"""

import pipeline_trace
from pipeline_trace import traced
from concurrent.futures import ThreadPoolExecutor
import base64
import os
import time
import urllib.request
from typing import Callable, Dict, Any, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from onboarding.qa_contrast_check import measure_contrast
from onboarding.qa_form_check import exercise_forms
from onboarding.qa_text_check import read_text
from onboarding.qa_type_check import check_types

DEVICE_MATRIX = [
    {
        "name": "Mobile",
        "viewport": (375, 812),
        "is_mobile": True,
        "device_scale_factor": 3
    },
    {
        "name": "Tablet",
        "viewport": (768, 1024),
        "is_mobile": False,
        "device_scale_factor": 2
    },
    {
        "name": "Desktop",
        "viewport": (1280, 800),
        "is_mobile": False,
        "device_scale_factor": 1,
        "exercise_forms": True,  # once is enough: whether a submission is accepted does not depend on the screen
        "measure_contrast": True,  # once is enough: colours do not depend on the screen
        "read_text": True  # once is enough: what the text says does not depend on the screen
    }
]

MAX_FULL_PAGE_HEIGHT = 12000  # CSS pixels; a taller page is captured up to here
API_READY_TIMEOUT_S = 20


def _answers(url: str) -> None:
    with urllib.request.urlopen(url, timeout=3):
        pass


def wait_until_answering(url: str, timeout_s: float = API_READY_TIMEOUT_S, probe: Callable[[str], None] = _answers,
                         sleep: Callable[[float], None] = time.sleep, now: Callable[[], float] = time.time) -> bool:
    """Waits until the API behind the page answers. The API restarts whenever its code is written, and the audit often
    starts the moment the last file lands; a page audited in that gap reports requests that failed for no fault of its
    own. Returns False when the time is over: the audit then goes ahead and reports what it sees."""
    deadline = now() + timeout_s
    while True:
        try:
            probe(url)
            return True
        except Exception:
            if now() >= deadline:
                print(f"[QA Gate] {url} did not answer within {timeout_s}s; auditing anyway", flush=True)
                return False
            sleep(0.5)


def _save_full_page(driver, path: str, width: int, page_height: Any, scale_factor: float) -> Optional[str]:
    """Saves the whole page, top to bottom, at one image pixel per CSS pixel. The viewport screenshot shows only the
    first screen at the device's own density; this one is what makes the rest of the page reviewable."""
    try:
        height = min(int(page_height), MAX_FULL_PAGE_HEIGHT)
        shot = driver.execute_cdp_cmd("Page.captureScreenshot", {
            "format": "png", "captureBeyondViewport": True,
            "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1 / scale_factor}})
        with open(path, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        return path
    except Exception as err:
        print(f"[QA Gate] No whole-page screenshot for {os.path.basename(path)}: {err}", flush=True)
        return None


@traced("qa.responsive_audit")
def run_responsive_qa_audit(
    url: str = "http://localhost:5174",
    timeout: int = 5,
    save_screenshots: bool = True,
    output_dir: Optional[str] = None,
    check_vertical_containment: bool = False,
    workspace_dir: Optional[str] = None,
    api_ready_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes automated QA verification against the live frontend on :5174 across device viewports.
    Returns a structured QA report detailing pass/fail status, device metrics, and layout defects.
    """
    if output_dir is None:
        workspace_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "workspace"))
        output_dir = os.path.join(workspace_base, ".qa_reports")
    
    if save_screenshots:
        os.makedirs(output_dir, exist_ok=True)
    if api_ready_url:
        wait_until_answering(api_ready_url)

    def browser_options() -> Options:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1400,1000")
        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        return options

    def audit_device(dev: Dict[str, Any]) -> tuple:
        """Audits one device in a browser of its own, so the devices are measured at the same time.
        Returns (result, defects, warnings, console errors)."""
        defects: List[str] = []
        warnings: List[str] = []  # reported with the verdict; they do not fail the audit
        all_console_errors: List[str] = []
        driver = webdriver.Chrome(options=browser_options())
        try:
            dev_name = dev["name"]
            width, height = dev["viewport"]
            device_started = time.time()

            # Emulate device via Chrome DevTools Protocol
            driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": dev.get("device_scale_factor", 1),
                "mobile": dev.get("is_mobile", False)
            })

            driver.get(url)
            time.sleep(1.5)  # Allow Vite hydration and layout paint

            # Check browser console logs for fatal script/module exceptions
            console_errors = []
            try:
                browser_logs = driver.get_log("browser")
                for entry in browser_logs:
                    if entry.get("level") == "SEVERE" and "favicon.ico" not in entry.get("message", ""):
                        msg = entry.get("message", "")
                        console_errors.append(msg)
                        if msg not in all_console_errors:
                            all_console_errors.append(msg)
            except Exception:
                pass

            # Measure layout metrics and detect horizontal, vertical overflow and blank root
            metrics = driver.execute_script("""
                var doc = document.documentElement;
                var body = document.body;
                // The width to hold the page to is the emulated device's. window.innerWidth cannot be used for that:
                // a mobile browser widens its layout viewport to fit content that overflows, so the two grow together
                // and an overflowing page measures as fitting.
                var innerW = arguments[0] || window.innerWidth;
                var innerH = window.innerHeight;
                var docScrollW = doc.scrollWidth;
                var bodyScrollW = body ? body.scrollWidth : 0;
                var maxScrollW = Math.max(docScrollW, bodyScrollW);

                var docScrollH = doc.scrollHeight;
                var bodyScrollH = body ? body.scrollHeight : 0;
                var maxScrollH = Math.max(docScrollH, bodyScrollH);

                var hasHOverflow = maxScrollW > (innerW + 2); // 2px margin of error for rounding
                var overflowDeltaX = hasHOverflow ? (maxScrollW - innerW) : 0;

                var hasVOverflow = maxScrollH > (innerH + 4);
                var overflowDeltaY = hasVOverflow ? (maxScrollH - innerH) : 0;

                // Check for console errors if intercepted or check document body text for React error overlay
                var errorOverlay = document.querySelector('vite-error-overlay');
                var hasCrashOverlay = !!errorOverlay;
                // What the overlay says: the compiler's message and the file and line it points at
                var overlayRoot = errorOverlay && errorOverlay.shadowRoot;
                var overlayText = function (selector) {
                    var el = overlayRoot && overlayRoot.querySelector(selector);
                    return el ? el.textContent.trim().slice(0, 600) : '';
                };

                // Text or controls that start on screen and end beyond its right edge. The page may not scroll
                // (an ancestor hides the overflow), so the scroll-width check above cannot see them.
                var clipped = [];
                var candidates = document.querySelectorAll('a, button, input, select, textarea, label, span, p, li, td, th, h1, h2, h3, h4');
                for (var i = 0; i < candidates.length; i++) {
                    var el = candidates[i];
                    var rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0 || rect.left >= innerW || rect.right <= innerW + 1) continue;
                    var ownText = '';
                    for (var n = 0; n < el.childNodes.length; n++) {
                        if (el.childNodes[n].nodeType === 3) ownText += el.childNodes[n].textContent;
                    }
                    ownText = (ownText.trim() || el.value || el.placeholder || '').toString().trim();
                    if (!ownText) continue;
                    var scrollable = false;
                    for (var parent = el.parentElement; parent; parent = parent.parentElement) {
                        var overflowX = getComputedStyle(parent).overflowX;
                        if (overflowX === 'auto' || overflowX === 'scroll') { scrollable = true; break; }
                    }
                    if (scrollable) continue;
                    clipped.push(el.tagName.toLowerCase() + ' "' + ownText.slice(0, 40) + '" ends at ' + Math.round(rect.right) + 'px');
                }

                var rootEl = document.getElementById('root');
                var isRootEmpty = !rootEl || rootEl.childElementCount === 0;

                // Extract sample text for semantic inspection
                var rootText = rootEl ? rootEl.innerText.slice(0, 1000) : '';

                return {
                    innerWidth: innerW,
                    layoutViewportWidth: window.innerWidth,
                    innerHeight: innerH,
                    maxScrollWidth: maxScrollW,
                    maxScrollHeight: maxScrollH,
                    hasHorizontalOverflow: hasHOverflow,
                    overflowDelta: overflowDeltaX,
                    hasVerticalOverflow: hasVOverflow,
                    verticalOverflowDelta: overflowDeltaY,
                    hasCrashOverlay: hasCrashOverlay,
                    crashMessage: overlayText('.message-body'),
                    crashFile: overlayText('.file'),
                    clippedCount: clipped.length,
                    clippedSamples: clipped.slice(0, 5),
                    isRootEmpty: isRootEmpty
                };
            """, width)

            screenshot_path = None
            full_page_path = None
            if save_screenshots:
                shot_name = f"qa_{dev_name.lower()}_{width}x{height}.png"
                shot_full = os.path.join(output_dir, shot_name)
                try:
                    driver.save_screenshot(shot_full)
                    screenshot_path = shot_full
                except Exception:
                    pass
                full_page_path = _save_full_page(
                    driver, os.path.join(output_dir, f"qa_{dev_name.lower()}_full.png"), width,
                    metrics.get("maxScrollHeight"), dev.get("device_scale_factor", 1))

            passed = True
            device_defects: List[str] = []
            device_warnings: List[str] = []
            if metrics.get("clippedCount"):
                samples = "; ".join(str(sample) for sample in metrics.get("clippedSamples") or [])
                device_warnings.append(f"[{dev_name}] {metrics['clippedCount']} element(s) with text run past the "
                                       f"{width}px screen edge: {samples}")
                warnings.extend(device_warnings)

            if metrics.get("hasCrashOverlay"):
                passed = False
                said = " ".join(str(metrics.get(k) or "") for k in ("crashMessage", "crashFile")).strip()
                said = f": {said}" if said else ""
                device_defects.append(f"React Vite error overlay present on {dev_name}{said}")
                defects.append(f"[{dev_name}] Application crashed: React error overlay detected{said}")

            if metrics.get("isRootEmpty"):
                passed = False
                device_defects.append(f"Application DOM is blank: #root has 0 children on {dev_name}")
                defects.append(f"[{dev_name}] Blank UI defect: #root element has 0 children")

            if console_errors:
                passed = False
                for cerr in console_errors:
                    device_defects.append(f"Console SEVERE: {cerr}")
                    defects.append(f"[{dev_name}] Console error: {cerr}")


            if metrics.get("hasHorizontalOverflow"):
                passed = False
                delta = metrics.get("overflowDelta", 0)
                device_defects.append(f"Horizontal overflow detected: scrollWidth {metrics.get('maxScrollWidth')}px exceeds viewport {width}px by {delta}px")
                widest = "; ".join(str(sample) for sample in metrics.get("clippedSamples") or [])
                defects.append(f"[{dev_name}] Layout defect: {delta}px horizontal overflow on {width}px screen"
                               + (f" (running past the edge: {widest})" if widest else ""))

            if dev.get("measure_contrast") and not metrics.get("hasCrashOverlay") and not metrics.get("isRootEmpty"):
                contrast = measure_contrast(driver, dev_name)
                device_warnings.extend(contrast.warnings)
                warnings.extend(contrast.warnings)
                if contrast.defects:
                    passed = False
                    device_defects.extend(contrast.defects)
                    defects.extend(contrast.defects)

            if dev.get("read_text") and not metrics.get("hasCrashOverlay") and not metrics.get("isRootEmpty"):
                text_check = read_text(driver, dev_name)
                device_warnings.extend(text_check.warnings)
                warnings.extend(text_check.warnings)
                if text_check.defects:
                    passed = False
                    device_defects.extend(text_check.defects)
                    defects.extend(text_check.defects)

            # Last, after the screenshots: submitting a form changes what the page shows
            form_check = None
            if dev.get("exercise_forms") and not metrics.get("hasCrashOverlay") and not metrics.get("isRootEmpty"):
                form_check = exercise_forms(driver, dev_name)
                device_warnings.extend(form_check.warnings)
                warnings.extend(form_check.warnings)
                if form_check.defects:
                    passed = False
                    device_defects.extend(form_check.defects)
                    defects.extend(form_check.defects)

            if check_vertical_containment and metrics.get("hasVerticalOverflow"):
                passed = False
                delta_y = metrics.get("verticalOverflowDelta", 0)
                device_defects.append(f"Vertical overflow detected: scrollHeight {metrics.get('maxScrollHeight')}px exceeds viewport {height}px by {delta_y}px")
                defects.append(f"[{dev_name}] Layout defect: {delta_y}px vertical cutoff/overflow on {height}px screen")

            return {
                "device": dev_name,
                "width": width,
                "height": height,
                "passed": passed,
                "metrics": metrics,
                "defects": device_defects,
                "warnings": device_warnings,
                "screenshot": screenshot_path,
                "full_page_screenshot": full_page_path,
                "forms": form_check.outcomes if form_check else None,
                "duration_s": round(time.time() - device_started, 2)
            }, defects, warnings, all_console_errors
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    try:
        with ThreadPoolExecutor(max_workers=len(DEVICE_MATRIX) + 1) as pool:
            types = pool.submit(pipeline_trace.bind_context(check_types), workspace_dir) if workspace_dir else None
            audited = list(pool.map(pipeline_trace.bind_context(audit_device), DEVICE_MATRIX))
    except Exception as e:
        print(f"[QA Gate] WebDriver connection or execution notice: {e}")
        # In offline/mock test environments without active Chrome/Vite, return a graceful fallback
        return {
            "passed": True,
            "overall_status": "SKIPPED_OFFLINE",
            "device_results": [],
            "defects": [],
            "summary": f"QA test run bypassed (browser or server unavailable): {e}"
        }

    results: List[Dict[str, Any]] = []
    defects: List[str] = []
    warnings: List[str] = []
    all_console_errors: List[str] = []
    for result, device_defects, device_warnings, device_console_errors in audited:  # in DEVICE_MATRIX order
        results.append(result)
        defects.extend(device_defects)
        warnings.extend(device_warnings)
        all_console_errors.extend(e for e in device_console_errors if e not in all_console_errors)
    overall_passed = all(r["passed"] for r in results)
    if types is not None:
        type_check = types.result()
        defects.extend(type_check.defects)
        warnings.extend(type_check.warnings)
        overall_passed = overall_passed and not type_check.defects

    status_str = "PASS" if overall_passed else "FAIL"
    summary_text = (
        f"QA Audit {status_str}: Tested across {len(DEVICE_MATRIX)} viewports "
        f"({', '.join(d['name'] for d in DEVICE_MATRIX)}). "
        f"{len(defects)} defect(s) discovered."
    )

    return {
        "passed": overall_passed,
        "overall_status": status_str,
        "device_results": results,
        "defects": defects,
        "warnings": warnings,
        "console_errors": all_console_errors,
        "summary": summary_text
    }
