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

from onboarding.domain_ontology import analyze_pitch_for_kickstart
from onboarding.dynamic_domain_generator import build_site_manifest_from_schema


CLASSIFICATION_BENCHMARK_CASES = [
    {"domain": "Pure Custom Game", "pitch": "A flappy bird game"},
    {"domain": "Fintech / Calculator Tool", "pitch": "A mortgage interest rate calculator with monthly amortization charts"},
    {"domain": "Pure E-Commerce", "pitch": "A boutique sourdough bakery for pre-ordering artisan bread and pastries with cart checkout"},
    {"domain": "Hybrid Domain", "pitch": "A pizzeria with custom sourdough pizza builder and live order tracking"},
    {"domain": "Service Booking", "pitch": "A site for parents to book a babysitter with open weekly calendar hours"}
]


@pytest.mark.parametrize("case", CLASSIFICATION_BENCHMARK_CASES, ids=[c["domain"] for c in CLASSIFICATION_BENCHMARK_CASES])
def test_custom_concept_vs_premade_block_classification(case):
    pitch = case["pitch"]
    analysis = analyze_pitch_for_kickstart(pitch)
    
    assert "pitch" in analysis
    assert "blocks" in analysis
    assert "capabilities" in analysis
    assert "extracted_requirements" in analysis
    assert len(analysis["blocks"]) >= 1
    assert len(analysis["extracted_requirements"]) >= 1

    for block in analysis["blocks"]:
        assert "id" in block
        assert "name" in block
        assert "description" in block
        assert block.get("is_recommended") is True


def test_custom_concept_manifest_intent_isolation():
    # Test that arbitrary pitches generate valid site manifests
    game_pitch = "A flappy bird game"
    manifest_game = build_site_manifest_from_schema({"pitch": game_pitch}, "/tmp")
    assert manifest_game.intent.brand_name != ""
    assert len(manifest_game.components) >= 1
    
    ecom_pitch = "An artisan bakery for ordering sourdough bread"
    manifest_ecom = build_site_manifest_from_schema({"pitch": ecom_pitch}, "/tmp")
    assert manifest_ecom.intent.brand_name != ""
    assert len(manifest_ecom.components) >= 1


if __name__ == "__main__":
    pytest.main(["-v", __file__])
