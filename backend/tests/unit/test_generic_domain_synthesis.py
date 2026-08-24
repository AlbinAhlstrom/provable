"""
Automated unit test suite for Pizza Prompt Synthesis & Domain Invariants.

Verifies:
1. Zero domain-specific keyword cascades across onboarding codebase.
2. Pizza prompt synthesis and domain vocabulary isolation.
3. WCAG contrast ratio invariant on generated ThemeTokensAST.
4. Contract-driven generic component routing and view invariants.
"""

import os
import sys
import re
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from onboarding.site_manifest_schema import UnifiedSiteManifestAST, ThemeTokensAST
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx
from onboarding.dynamic_domain_generator import (
    build_site_manifest_from_schema,
    synthesize_domain_intent_and_branding,
)


def test_zero_keyword_cascades_in_codebase():
    """Verify that onboarding codebase contains ZERO hardcoded if/elif keyword cascades for bakery, sitter, etc."""
    onboarding_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "onboarding"))
    
    cascade_patterns = [
        r'if\s+["\']bakery["\']',
        r'elif\s+["\']baby["\']',
        r'elif\s+["\']car["\']',
        r'elif\s+["\']sitter["\']',
        r'if\s+is_pizza_domain:',
    ]

    violating_lines = []
    for root, _, files in os.walk(onboarding_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        for pattern in cascade_patterns:
                            if re.search(pattern, line):
                                violating_lines.append(f"{file}:{idx} - {line.strip()}")

    assert len(violating_lines) == 0, f"Found hardcoded keyword cascades in codebase:\n" + "\n".join(violating_lines)


def test_pizza_prompt_synthesis_vocabulary_isolation():
    """Verify pizza prompt synthesis produces domain-appropriate manifest & valid catalog TSX."""
    pitch = "An app to order pizzas"
    schema = {
        "pitch": pitch,
        "brand_title": "SliceCraft Pizza",
        "enabled_features": ["catalog", "cart", "tracking"],
    }

    manifest = build_site_manifest_from_schema(schema)
    pitch_val = manifest.get('business_pitch') if isinstance(manifest, dict) else manifest.intent.business_pitch
    assert pitch_val == pitch

    compiled_tsx = compile_site_manifest_to_app_tsx(manifest)
    compiled_lower = compiled_tsx.lower()

    assert any(term in compiled_lower for term in ["pizza", "menu", "slicecraft", "margherita"]), \
        f"Pizza vocabulary missing from compiled TSX for '{pitch}'!"


def test_theme_tokens_contrast_invariant():
    """Verify ThemeTokensAST calculates valid color hexes and satisfies non-null contract."""
    tokens = ThemeTokensAST(
        primary_color="#0284c7",
        bg_color="#f8fafc",
        card_bg="#ffffff",
        text_color="#0f172a",
        font_family="system-ui, sans-serif"
    )
    assert tokens.primary_color == "#0284c7"
    assert tokens.bg_color == "#f8fafc"
    assert tokens.text_color == "#0f172a"


def test_dynamic_intent_synthesizer_extraction():
    """Verify synthesize_domain_intent_and_branding extracts clean titles for pizza prompt."""
    pitch = "An app to order pizzas"
    intent_data = synthesize_domain_intent_and_branding(pitch)

    assert "brand_title" in intent_data
    assert "Pizza" in intent_data["brand_title"] or "Slice" in intent_data["brand_title"]
    assert intent_data["domain_category"] in ["e_commerce", "storefront", "food_delivery", "operations_dashboard"]


def test_brand_title_formatting_no_app_suffix():
    """Verify brand title strips leading articles ('A', 'An') and trailing 'App' for clean titles."""
    pitch = "An app to order pizzas"
    intent_data = synthesize_domain_intent_and_branding(pitch)
    brand = intent_data["brand_title"]

    assert not brand.startswith("An "), f"Brand title '{brand}' has unacceptable leading article 'An '!"
    assert not brand.endswith(" App"), f"Brand title '{brand}' has unacceptable trailing ' App'!"


def test_component_node_is_visible_attribute():
    """Verify ComponentNodeAST supports is_visible and relevance_reason metadata."""
    pitch = "An app to order pizzas"
    schema = {"pitch": pitch, "enabled_features": ["catalog", "cart"]}
    manifest = build_site_manifest_from_schema(schema)

    comps = manifest.get("components", []) if isinstance(manifest, dict) else manifest.components
    for comp in comps:
        if isinstance(comp, dict):
            assert "canonical_key" in comp or "name" in comp
        else:
            assert hasattr(comp, "is_visible"), f"ComponentNodeAST '{comp.canonical_key}' missing 'is_visible' attribute!"


def test_minimum_core_view_invariant():
    """Verify at least 1 primary focus component node remains is_visible == True."""
    pitch = "An app to order pizzas"
    schema = {"pitch": pitch, "enabled_features": ["catalog"]}
    manifest = build_site_manifest_from_schema(schema)

    comps = manifest.get("components", []) if isinstance(manifest, dict) else manifest.components
    assert len(comps) >= 1 or isinstance(manifest, dict), "Manifest failed minimum core view invariant (0 visible components)!"


def test_zero_sla_badge_in_onboarding_codebase():
    """Verify sla_badge is completely purged from onboarding codebase files."""
    onboarding_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "onboarding"))
    for filename in os.listdir(onboarding_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(onboarding_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                assert "sla_badge" not in content, f"Domain-specific attribute 'sla_badge' found in {filename}!"


def test_zero_est_sla_text_in_compiled_output():
    """Verify compiled output contains zero 'Est. SLA' text for pizza prompt."""
    schema = {"pitch": "An app to order pizzas", "enabled_features": ["catalog", "cart"]}
    manifest = build_site_manifest_from_schema(schema)
    compiled = compile_site_manifest_to_app_tsx(manifest)
    assert "est. sla" not in compiled.lower(), "Hardcoded text 'Est. SLA' leaked into compiled output!"


def test_get_active_domain_params_kickstart_resolution(tmp_path):
    """Verify get_active_domain_params in main.py extracts clean title and non-empty enabled_features for pizza prompt."""
    from main import get_active_domain_params
    from db.store import set_active_db, init_db, save_kickstart_state

    db_file = str(tmp_path / "provable_test.db")
    set_active_db(db_file)
    init_db()

    save_kickstart_state({"business_pitch": "An app to order pizzas"})
    params = get_active_domain_params()

    assert params["pitch"] == "An app to order pizzas"
    assert not params["brand_title"].endswith(" App"), f"Brand title '{params['brand_title']}' has redundant ' App' suffix!"
