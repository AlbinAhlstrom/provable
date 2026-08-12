"""
Automated Test Suite: Custom Concept vs Pre-Baked Registry Block Classification Benchmark.

Verifies that Provable's pitch analysis and component planning engines accurately
differentiate standard pre-baked UX catalog blocks (catalog, cart, tracking, booking)
from custom bespoke domain concepts (games, calculators, custom builders, custom tools).
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.block_catalog import analyze_pitch_for_kickstart, FEATURE_BLOCK_CATALOG
from onboarding.dynamic_domain_generator import build_site_manifest_from_schema


CLASSIFICATION_BENCHMARK_CASES = [
    {
        "domain": "Pure Custom Game",
        "pitch": "A flappy bird game",
        "expected_custom_concept": True,
        "expected_premade_blocks": ["flappy_bird"],
        "forbidden_premade_blocks": ["catalog_grid", "shopping_cart", "order_tracking"]
    },
    {
        "domain": "Fintech / Calculator Tool",
        "pitch": "A mortgage interest rate calculator with monthly amortization charts",
        "expected_custom_concept": True,
        "expected_premade_blocks": [],
        "forbidden_premade_blocks": ["catalog_grid", "shopping_cart", "order_tracking"]
    },
    {
        "domain": "Pure E-Commerce",
        "pitch": "A boutique sourdough bakery for pre-ordering artisan bread and pastries with cart checkout",
        "expected_custom_concept": False,
        "expected_premade_blocks": ["catalog_grid", "shopping_cart"],
        "forbidden_premade_blocks": ["booking_calendar"]
    },
    {
        "domain": "Hybrid Domain (E-Commerce + Custom Builder)",
        "pitch": "A pizzeria with custom sourdough pizza builder and live order tracking",
        "expected_custom_concept": True,
        "expected_premade_blocks": ["catalog_grid", "shopping_cart", "order_tracking"],
        "forbidden_premade_blocks": []
    },
    {
        "domain": "Service Booking",
        "pitch": "A site for parents to book a babysitter with open weekly calendar hours",
        "expected_custom_concept": False,
        "expected_premade_blocks": ["booking_calendar"],
        "forbidden_premade_blocks": ["catalog_grid", "shopping_cart", "order_tracking"]
    }
]


@pytest.mark.parametrize("case", CLASSIFICATION_BENCHMARK_CASES, ids=[c["domain"] for c in CLASSIFICATION_BENCHMARK_CASES])
def test_custom_concept_vs_premade_block_classification(case):
    pitch = case["pitch"]
    analysis = analyze_pitch_for_kickstart(pitch)
    
    recommended_blocks = [b["id"] for b in analysis["blocks"] if b["is_recommended"]]
    
    # 1. Verify expected premade blocks are recommended
    for expected_id in case["expected_premade_blocks"]:
        assert expected_id in recommended_blocks, f"Expected premade block '{expected_id}' was not recommended for pitch: '{pitch}'"

    # 2. Verify forbidden premade blocks are NOT force-recommended
    for forbidden_id in case["forbidden_premade_blocks"]:
        assert forbidden_id not in recommended_blocks, f"Forbidden block '{forbidden_id}' was wrongfully recommended for pitch: '{pitch}'"


def test_custom_concept_manifest_intent_isolation():
    # Test that game/calculator pitches set non-ecommerce domain intent categories
    game_pitch = "A flappy bird game"
    manifest_game = build_site_manifest_from_schema({"pitch": game_pitch}, "/tmp")
    assert manifest_game.intent.domain_category == "interactive_game"
    
    ecom_pitch = "An artisan bakery for ordering sourdough bread"
    manifest_ecom = build_site_manifest_from_schema({"pitch": ecom_pitch}, "/tmp")
    assert manifest_ecom.intent.domain_category == "e_commerce"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
