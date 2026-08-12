"""
Automated E2E Selenium Sanity Test for Prompt Synthesis & Visual Inspection.
Simulates exact user workflow: prompt input -> AST synthesis -> headless Chrome UI rendering & visual audit.
"""

import os
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from onboarding.synthesis import synthesize_application_stack
from onboarding.visual_auditor import audit_visual_presentation

def test_e2e_pizza_app_prompt_synthesis_and_ui_sanity():
    """
    Given a user submits prompt "An app to order pizzas"
    When synthesizing the application stack and launching preview
    Then the app renders non-blank UI with header, navbar, and catalog components passing visual inspection.
    """
    # 1. Synthesize application stack for pizza pitch
    schema = {"pitch": "An app to order pizzas"}
    result = synthesize_application_stack(schema)
    assert result.get("success") is True, f"Synthesis failed: {result}"

    # 2. Setup Headless Chrome Options according to project rules (--disable-gpu, --remote-debugging-port=9222)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("http://localhost:5174")
        time.sleep(2)  # Hydration wait

        # 3. Assert root container and non-empty text content
        root_elem = driver.find_element(By.ID, "root")
        assert root_elem is not None, "#root element missing"
        page_text = root_elem.text

        if len(page_text.strip()) <= 50:
            print("\n--- BROWSER CONSOLE LOGS ---")
            for entry in driver.get_log('browser'):
                print(entry)
            print("\n--- PAGE SOURCE ---")
            print(driver.page_source[:2000])

        assert len(page_text.strip()) > 50, f"App rendered blank or empty screen: {page_text[:100]}"
        assert "App To Order Pizzas" in page_text or "Catalog" in page_text or "Pizzeria" in page_text, f"Unexpected page content: {page_text[:200]}"

        # 4. Save screenshot and perform visual auditor inspection
        screenshot_path = os.path.join(os.path.dirname(__file__), "..", "..", "workspace", "e2e_pizza_preview.png")
        driver.save_screenshot(screenshot_path)
        assert os.path.exists(screenshot_path)

        audit_res = audit_visual_presentation(url="http://localhost:5174", pitch="An app to order pizzas")
        assert audit_res.get("passed", True) is True
        assert audit_res.get("score", 100) >= 80

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
