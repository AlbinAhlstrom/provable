#!/usr/bin/env python3
"""Capture a headless-Chrome screenshot of the running app.

Tries Selenium first (what the project's tests use) and falls back to Playwright if
Selenium cannot start a browser, e.g. a chromedriver/Chrome version mismatch in a
cloud sandbox. Set CHROME_BIN to point at a specific Chrome/Chromium binary.
"""
import os
import sys
import time
import argparse

BROWSER_CANDIDATES = (
    os.environ.get("CHROME_BIN"),
    "/usr/bin/chromium-browser",
    "/opt/pw-browsers/chromium",
)


def parse_args():
    parser = argparse.ArgumentParser(description="Capture headless Chrome screenshots.")
    parser.add_argument("--url", default="http://localhost:5173", help="Base URL to navigate to")
    parser.add_argument("--view", default=None, help="Visible text of a button/tab to click before capturing")
    parser.add_argument("--output", default="screenshot.png", help="Path to save the screenshot")
    parser.add_argument("--viewport", default="1280x800", help="Viewport resolution in WIDTHxHEIGHT format")
    return parser.parse_args()


def find_browser():
    return next((c for c in BROWSER_CANDIDATES if c and os.path.exists(c)), None)


def capture_selenium(args, width, height):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    print("🤖 Initializing Chrome WebDriver in headless mode...")
    opts = Options()
    for flag in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                 "--disable-gpu", "--remote-debugging-port=9222"):
        opts.add_argument(flag)
    browser = find_browser()
    if browser:
        opts.binary_location = browser

    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_window_size(width, height)
        print(f"🤖 Navigating to: {args.url}")
        driver.get(args.url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)  # Allow React app hydration

        if args.view:
            wanted = args.view.strip().lower()
            candidates = driver.find_elements(By.CSS_SELECTOR, "button, a, [role='tab']")
            target = next((c for c in candidates if c.text.strip().lower() == wanted), None)
            if target:
                print(f"🤖 Clicking on navigation element: '{target.text}'")
                target.click()
                time.sleep(2.5)
            else:
                print(f"⚠️ Warning: '{args.view}' not found. Available: "
                      f"{sorted({c.text.strip() for c in candidates if c.text.strip()})}")
        driver.save_screenshot(args.output)
    finally:
        driver.quit()


def capture_playwright(args, width, height):
    from playwright.sync_api import sync_playwright

    print("🤖 Initializing Playwright Chromium in headless mode...")
    with sync_playwright() as p:
        launch_kwargs = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        browser_path = find_browser()
        if browser_path:
            launch_kwargs["executable_path"] = browser_path
        browser = p.chromium.launch(**launch_kwargs)
        try:
            page = browser.new_page(viewport={"width": width, "height": height})
            print(f"🤖 Navigating to: {args.url}")
            page.goto(args.url, wait_until="load", timeout=15000)
            page.wait_for_timeout(3000)  # Allow React app hydration

            if args.view:
                target = page.locator("button, a, [role='tab']").filter(has_text=args.view.strip()).first
                if target.count():
                    print(f"🤖 Clicking on navigation element: '{args.view}'")
                    target.click()
                    page.wait_for_timeout(2500)
                else:
                    print(f"⚠️ Warning: '{args.view}' not found.")
            page.screenshot(path=args.output)
        finally:
            browser.close()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()

    try:
        width, height = map(int, args.viewport.lower().split("x"))
    except Exception:
        print(f"Invalid viewport format: '{args.viewport}'. Using default 1280x800.")
        width, height = 1280, 800

    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)

    try:
        capture_selenium(args, width, height)
    except Exception as selenium_err:
        first_line = str(selenium_err).strip().splitlines()[0] if str(selenium_err).strip() else type(selenium_err).__name__
        print(f"⚠️ Selenium capture failed ({first_line}); trying Playwright...", file=sys.stderr)
        try:
            capture_playwright(args, width, height)
        except Exception as pw_err:
            print(f"❌ Screenshot failed with both engines.\n  selenium: {first_line}\n  playwright: {pw_err}\n"
                  "  (Playwright needs `pip install playwright` and a Chromium via CHROME_BIN or `playwright install chromium`.)",
                  file=sys.stderr)
            sys.exit(1)

    print(f"🤖 Saving screenshot to: {args.output}")
    print("✅ Screenshot captured successfully.")


if __name__ == "__main__":
    main()
