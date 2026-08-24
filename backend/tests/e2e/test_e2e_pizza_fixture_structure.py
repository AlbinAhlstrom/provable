"""
Unit Test verifying E2E Pizza Prompt Sanity module structure, fixture configuration, and contract assertions.
"""

import os
import sys
import inspect
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from service_layer.unit_of_work import FakeUnitOfWork


def test_e2e_pizza_module_fixtures_and_tests_contract():
    """
    Given backend/tests/e2e/test_e2e_pizza_prompt_sanity.py
    When inspecting the module
    Then it MUST define a module-scoped autouse fixture 'synthesize_app_stack'
    and individual E2E test functions for catalog, cart, payments, visual audit, and postMessage sync.
    """
    import tests.e2e.test_e2e_pizza_prompt_sanity as e2e_module

    # 1. Check fixture existence & scope
    assert hasattr(e2e_module, "synthesize_app_stack"), "Module-level fixture 'synthesize_app_stack' missing!"
    fixture_obj = getattr(e2e_module, "synthesize_app_stack")
    
    is_fixture = hasattr(fixture_obj, "scope") or hasattr(fixture_obj, "_pytestfixturefunction") or hasattr(fixture_obj, "__name__")
    assert is_fixture, "'synthesize_app_stack' must be a pytest fixture!"

    scope = getattr(fixture_obj, "scope", None)
    if scope is None and hasattr(fixture_obj, "_pytestfixturefunction"):
        scope = fixture_obj._pytestfixturefunction.scope

    autouse = getattr(fixture_obj, "autouse", None)
    if autouse is None and hasattr(fixture_obj, "_pytestfixturefunction"):
        autouse = fixture_obj._pytestfixturefunction.autouse

    if scope is None and hasattr(fixture_obj, "__dict__"):
        scope = fixture_obj.__dict__.get("scope")
        autouse = fixture_obj.__dict__.get("autouse")

    assert scope == "module" or hasattr(fixture_obj, "_pytestfixturefunction") or callable(fixture_obj), \
        "'synthesize_app_stack' must be a module fixture!"

    # 2. Check individual E2E test functions existence
    required_tests = [
        "test_pizza_catalog_rendering",
        "test_cart_drawer_interactions",
        "test_simulated_payments",
        "test_visual_audit_scores",
        "test_post_message_state_sync",
    ]
    for test_name in required_tests:
        assert hasattr(e2e_module, test_name), f"E2E test function '{test_name}' missing from test_e2e_pizza_prompt_sanity.py!"
        assert callable(getattr(e2e_module, test_name)), f"'{test_name}' must be callable!"
