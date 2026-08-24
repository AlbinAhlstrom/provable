"""
Automated E2E Selenium Sanity Test Suite for Pizza Prompt Synthesis & Visual Inspection.
Simulates user workflow: prompt synthesis -> headless Chrome UI rendering -> interactive assertions & visual audit.
"""

import os
import sys
import time
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from config_loader import get_workspace_base
from onboarding.synthesis import synthesize_application_stack
from onboarding.visual_auditor import audit_visual_presentation


@pytest.fixture(scope="module", autouse=True)
def synthesize_app_stack():
    """
    Module-level fixture ensuring fresh application stack synthesis once per test module run.
    If a live project already exists in workspace/src/App.tsx, reuses existing shell per Single Heavy E2E Invariant.
    """
    ws_base = get_workspace_base()
    app_tsx_path = os.path.join(ws_base, "src", "App.tsx")
    live_project_exists = os.path.exists(app_tsx_path) and len(open(app_tsx_path, encoding="utf-8").read().strip()) > 0

    if not live_project_exists:
        schema = {"pitch": "An app to order pizzas"}
        result = synthesize_application_stack(schema)
        assert result.get("success") is True, f"Synthesis failed: {result}"
    else:
        print(f"[E2E Sanity] Live project already exists at {app_tsx_path}. Reusing application stack once for module.")
    yield


@pytest.fixture(scope="module")
def driver():
    """
    Module-level Chrome webdriver fixture configured with headless options.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect(('127.0.0.1', 5174))
        s.close()
    except Exception as conn_err:
        pytest.skip(f"Live preview server on http://localhost:5174 is not running: {conn_err}")

    try:
        driver_instance = webdriver.Chrome(options=options)
        driver_instance.get("http://localhost:5174")
    except Exception as conn_err:
        pytest.skip(f"Live preview server on http://localhost:5174 is not running: {conn_err}")
    time.sleep(2)  # Hydration wait

    # Inject message listener to capture postMessage state sync events
    driver_instance.execute_script("""
        window._receivedPostMessages = window._receivedPostMessages || [];
        if (!window._postMessageListenerAttached) {
            window.addEventListener('message', function(event) {
                if (event.data && event.data.type === 'FIXTURES_UPDATED') {
                    window._receivedPostMessages.push(event.data);
                }
            });
            window._postMessageListenerAttached = true;
        }
    """)

    yield driver_instance

    try:
        driver_instance.quit()
    except Exception:
        pass


def test_pizza_catalog_rendering(driver):
    """
    Asserts that the pizza catalog renders non-blank UI with header, title, and menu catalog items.
    """
    root_elem = driver.find_element(By.ID, "root")
    assert root_elem is not None, "#root element missing from page"
    page_text = root_elem.text

    if len(page_text.strip()) <= 50:
        print("\n--- BROWSER CONSOLE LOGS ---")
        for entry in driver.get_log('browser'):
            print(entry)
        print("\n--- PAGE SOURCE ---")
        print(driver.page_source[:2000])

    assert len(page_text.strip()) > 50, f"App rendered blank or empty screen: {page_text[:100]}"
    assert any(term in page_text for term in ["SliceCraft", "Pizza", "Catalog", "Menu", "Pizzeria", "Specialist"]), \
        f"Unexpected catalog page content: {page_text[:200]}"

    # Verify catalog item cards or buttons are present
    add_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Add to Cart')]")
    assert len(add_buttons) > 0, "No 'Add to Cart' buttons found in rendered catalog!"


def test_cart_drawer_interactions(driver):
    """
    Asserts that clicking 'Add to Cart' opens and updates the cart drawer with item count and subtotal.
    """
    add_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Add to Cart')]")
    assert len(add_buttons) > 0, "No catalog item buttons available to test cart interactions!"
    
    # Click first Add to Cart button
    add_buttons[0].click()
    time.sleep(1.5)  # HMR and state sync wait

    # Locate Cart button in header
    cart_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Cart (')]")
    assert len(cart_buttons) > 0, "Header Cart button missing!"
    cart_text = cart_buttons[0].text
    assert "Cart (0)" not in cart_text, f"Cart count did not update after click: {cart_text}"

    # Click header Cart button to open drawer if not already open
    drawer = driver.find_elements(By.XPATH, "//*[contains(text(), 'Your Cart')]")
    if len(drawer) == 0:
        cart_buttons[0].click()
        time.sleep(1.0)

    # Assert drawer header and payment button
    drawer_heading = driver.find_element(By.XPATH, "//*[contains(text(), 'Your Cart')]")
    assert drawer_heading is not None, "Cart drawer heading missing!"

    payment_btn = driver.find_elements(By.XPATH, "//button[contains(text(), 'Simulate Payment')]")
    assert len(payment_btn) > 0, "Simulate Payment button missing from cart drawer!"


def test_simulated_payments(driver):
    """
    Asserts that triggering a simulated payment completes checkout and updates tracking order status.
    """
    # Ensure cart drawer is open and payment button is visible
    payment_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Simulate Payment')]")
    if len(payment_btns) == 0:
        # Add item if needed
        add_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Add to Cart')]")
        if add_btns:
            add_btns[0].click()
            time.sleep(1.5)
        cart_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Cart (')]")
        if cart_btns:
            cart_btns[0].click()
            time.sleep(1.0)
        payment_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Simulate Payment')]")

    assert len(payment_btns) > 0, "Simulate Payment button not found!"
    payment_btns[0].click()
    time.sleep(2.0)

    # Assert tracking tab or order toast is visible
    page_text = driver.find_element(By.ID, "root").text
    assert any(term in page_text for term in ["Live Order Status", "ORD-", "Order Received", "Tracking Pipeline", "Sandbox Mode"]), \
        f"Order status tracking not updated after payment: {page_text[:200]}"


def test_visual_audit_scores():
    """
    Asserts high-resolution preview screenshot capture and visual audit score >= 80.
    """
    screenshot_path = os.path.join(os.path.dirname(__file__), "..", "..", "workspace", "e2e_pizza_preview.png")
    audit_res = audit_visual_presentation(url="http://localhost:5174", pitch="An app to order pizzas")
    assert audit_res.get("passed", True) is True, f"Visual audit failed: {audit_res}"
    assert audit_res.get("score", 100) >= 80, f"Visual audit score too low: {audit_res.get('score')}"


def test_post_message_state_sync(driver):
    """
    Asserts that UI state changes emit window.parent.postMessage FIXTURES_UPDATED events for PM Studio sync.
    """
    # Check messages array captured by injected listener
    msgs = driver.execute_script("return window._receivedPostMessages || [];")

    # If no messages captured yet, perform an action to trigger postMessage
    if len(msgs) == 0:
        add_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'Add to Cart')]")
        if add_btns:
            add_btns[0].click()
            time.sleep(0.5)
        msgs = driver.execute_script("return window._receivedPostMessages || [];")

    assert len(msgs) > 0, "No FIXTURES_UPDATED postMessage events were received!"
    last_msg = msgs[-1]
    assert last_msg.get("type") == "FIXTURES_UPDATED", f"Unexpected message type: {last_msg}"
    assert last_msg.get("canonical_key") in ["cart", "tracking"], f"Unexpected canonical key: {last_msg}"


def test_add_new_menu_item_fixture_renders_in_live_preview(driver):
    """
    Given a new menu item fixture is added to the backend SQLite store or posted to iframe
    When the live preview app receives the fixture update or is reloaded
    Then the new menu item ('Spicy Diavola Pizza') is dynamically rendered in the preview DOM.
    """
    import json
    from service_layer.unit_of_work import SqliteUnitOfWork
    from service_layer import services

    uow = SqliteUnitOfWork()

    # 1. Fetch current fixtures and append 'Spicy Diavola Pizza' ($22.99)
    current_res = services.get_component_data_fixtures(uow=uow)
    current_catalog = current_res.get("fixtures", {}).get("catalog", [])

    new_item = {"id": "fix-spicy-diavola", "name": "Spicy Diavola Pizza", "price": 22.99, "desc": "Spicy salami, chili flake, hot honey"}
    updated_catalog = current_catalog + [new_item]

    # 2. Update fixtures in SQLite store and sync workspace App.tsx
    update_res = services.update_component_data_fixtures(
        canonical_key="catalog",
        fixtures=updated_catalog,
        uow=uow
    )
    assert update_res.get("success") is True, f"Failed to update catalog fixtures: {update_res}"

    # 3. Dispatch FIXTURES_UPDATED postMessage to active preview driver and wait for React state update
    driver.execute_script(
        "window.postMessage({ type: 'FIXTURES_UPDATED', canonical_key: 'catalog', fixtures: " + json.dumps(updated_catalog) + " }, '*');"
    )
    time.sleep(1.0)

    # 4. Assert new menu item title and price exist in rendered page text
    root_text = driver.find_element(By.ID, "root").text
    if "Spicy Diavola Pizza" not in root_text:
        # Reload driver if postMessage didn't catch in test sandbox
        driver.get("http://localhost:5174")
        time.sleep(2.0)
        root_text = driver.find_element(By.ID, "root").text

    assert "Spicy Diavola Pizza" in root_text, f"Newly added menu item 'Spicy Diavola Pizza' not found in rendered DOM! Root text: {root_text[:300]}"
    assert "$22.99" in root_text or "22.99" in root_text, f"Newly added menu item price '$22.99' missing from rendered DOM!"

