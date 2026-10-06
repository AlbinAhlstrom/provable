#!/usr/bin/env python3
import os
import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_args():
    parser = argparse.ArgumentParser(description="Capture headless Chrome screenshots.")
    parser.add_argument("--url", default="http://localhost:5173", help="Base URL to navigate to")
    parser.add_argument("--view", default=None, help="Name of the nav-item tab to click before taking the screenshot")
    parser.add_argument("--output", default="screenshot.png", help="Path to save the screenshot")
    parser.add_argument("--viewport", default="1280x800", help="Viewport resolution in WIDTHxHEIGHT format")
    return parser.parse_args()

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    args = parse_args()
    
    # Parse viewport size
    try:
        width, height = map(int, args.viewport.lower().split('x'))
    except Exception:
        print(f"Invalid viewport format: '{args.viewport}'. Using default 1280x800.")
        width, height = 1280, 800
        
    print(f"🤖 Initializing Chrome WebDriver in headless mode...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Browser lookup: CHROME_BIN override, then common Linux locations (incl. Playwright's Chromium).
    for candidate in (os.environ.get("CHROME_BIN"), "/usr/bin/chromium-browser",
                      "/opt/pw-browsers/chromium"):
        if candidate and os.path.exists(candidate):
            chrome_options.binary_location = candidate
            break
        
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.set_window_size(width, height)
        print(f"🤖 Navigating to: {args.url}")
        driver.get(args.url)
        
        # Wait for page to load & React hydration
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3) # Allow React app hydration
        
        if args.view:
            print(f"🤖 Locating view navigation tab: '{args.view}'")
            wanted = args.view.strip().lower()
            candidates = driver.find_elements(By.CSS_SELECTOR, "button, a, [role='tab']")
            target_btn = next((c for c in candidates if c.text.strip().lower() == wanted), None)

            if target_btn:
                print(f"🤖 Clicking on navigation element: '{target_btn.text}'")
                target_btn.click()
                time.sleep(2.5) # Wait for page render/API fetch completion
            else:
                print(f"⚠️ Warning: '{args.view}' not found. Available: {sorted({c.text.strip() for c in candidates if c.text.strip()})}")

        # Create output directory if it doesn't exist
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        print(f"🤖 Saving screenshot to: {args.output}")
        driver.save_screenshot(args.output)
        print("✅ Screenshot captured successfully.")
        
    except Exception as e:
        print(f"❌ Error during screenshot capture: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
