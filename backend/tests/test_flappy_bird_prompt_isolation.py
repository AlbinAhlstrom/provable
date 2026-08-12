"""
Automated Test Suite: Prompt Vocabulary & Component Isolation Verification.

Verifies that prompt prompts like 'A flappy bird game' generate isolated game domain
artifacts with ZERO leakage of pizzeria/e-commerce vocabulary, pizza menu items,
sourdough reviews, or wood-fired hero banners.
"""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.block_catalog import analyze_pitch_for_kickstart
from onboarding.dynamic_domain_generator import build_site_manifest_from_schema
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx
from onboarding.code_verifier import verify_tsx_syntax


def test_flappy_bird_block_analysis_isolation():
    pitch = "A flappy bird game"
    analysis = analyze_pitch_for_kickstart(pitch)
    
    blocks = analysis.get("blocks", [])
    block_dict = {b["id"]: b for b in blocks}
    
    # 1. flappy_bird mini-game block MUST be recommended for game pitch
    assert "flappy_bird" in block_dict, "flappy_bird feature block missing from block catalog analysis!"
    assert block_dict["flappy_bird"]["is_recommended"] is True, "flappy_bird block was not recommended for game prompt!"

    # 2. E-commerce blocks must NOT be force-recommended by default on a game prompt
    assert block_dict.get("catalog_grid", {}).get("is_recommended") is False, "catalog_grid force-recommended on game prompt!"
    assert block_dict.get("shopping_cart", {}).get("is_recommended") is False, "shopping_cart force-recommended on game prompt!"
    assert block_dict.get("order_tracking", {}).get("is_recommended") is False, "order_tracking force-recommended on game prompt!"


def test_flappy_bird_site_manifest_generation():
    pitch = "A flappy bird game"
    schema = {
        "pitch": pitch,
        "enabled_features": ["flappy_bird"]
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest = build_site_manifest_from_schema(schema, tmp_dir)
        
        # 1. Intent Category must be interactive_game
        assert manifest.intent.domain_category == "interactive_game", f"Expected 'interactive_game' category, got {manifest.intent.domain_category}"
        
        # 2. Brand name must reflect prompt title, not pizzeria
        assert "pizzeria" not in manifest.intent.brand_name.lower()
        assert "oven" not in manifest.intent.brand_name.lower()

        # 3. Hero banner must be game-specific, zero wood-fired pizza leak
        headline_lower = manifest.layout.hero_banner.headline.lower()
        subtitle_lower = manifest.layout.hero_banner.subtitle.lower()
        
        assert "pizza" not in headline_lower, f"Pizza leaked in headline: {manifest.layout.hero_banner.headline}"
        assert "wood-fired" not in headline_lower
        assert "sourdough" not in subtitle_lower
        assert "interactive" in headline_lower or "flappy" in headline_lower


def test_flappy_bird_ast_compiler_isolation():
    pitch = "A flappy bird game"
    schema = {
        "pitch": pitch,
        "enabled_features": ["flappy_bird"]
    }
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest = build_site_manifest_from_schema(schema, tmp_dir)
        compiled_tsx = compile_site_manifest_to_app_tsx(manifest)
        
        # 1. TSX must be valid React TypeScript syntax
        is_valid, err = verify_tsx_syntax(compiled_tsx)
        assert is_valid, f"Compiled TSX syntax error: {err}"
        
        # 2. Zero Pizza vocabulary leakage in TSX
        code_lower = compiled_tsx.lower()
        forbidden_pizza_terms = ["margherita", "pepperoni", "truffle wild mushroom", "sourdough crust", "san marzano"]
        for term in forbidden_pizza_terms:
            assert term not in code_lower, f"Pizza term '{term}' leaked into generated TSX code for '{pitch}'!"
            
        # 3. Flappy bird game hooks / components present
        assert "flappyscore" in code_lower, "Flappy Bird game state hooks missing from generated code!"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
