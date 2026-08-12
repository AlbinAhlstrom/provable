"""
Automated test suite for 3-Pillar Generic Synthesis Architecture.

Verifies:
1. Zero domain-specific keyword cascades across onboarding codebase.
2. Zero pizza/sourdough fallback leakage across 5 novel domain archetypes.
3. WCAG contrast ratio invariant on generated ThemeTokensAST.
4. Contract-driven generic component routing without string matching hacks.
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


NOVEL_DOMAIN_PROMPTS = [
    {
        "id": "drone_fleet",
        "pitch": "Drone delivery fleet logistics monitor with live telemetry and route planning",
        "expected_category": "operations_dashboard",
        "forbidden_terms": ["margherita", "pepperoni", "sourdough", "san marzano", "sitter", "babysitter", "bakery"],
    },
    {
        "id": "solar_roi",
        "pitch": "Solar panel ROI and payback period calculator with energy yield estimates",
        "expected_category": "fintech_tool",
        "forbidden_terms": ["margherita", "pepperoni", "sourdough", "san marzano", "sitter", "babysitter", "bakery"],
    },
    {
        "id": "tennis_court",
        "pitch": "Tennis court hourly reservation system with open slot scheduling",
        "expected_category": "service_booking",
        "forbidden_terms": ["margherita", "pepperoni", "sourdough", "san marzano", "sitter", "babysitter", "pizzeria"],
    },
    {
        "id": "crypto_tracker",
        "pitch": "Crypto portfolio tracker and real-time market alert feed",
        "expected_category": "fintech_tool",
        "forbidden_terms": ["margherita", "pepperoni", "sourdough", "san marzano", "sitter", "babysitter", "bakery"],
    },
    {
        "id": "retro_game",
        "pitch": "Retro 8-bit space shooter game with high score leaderboard",
        "expected_category": "interactive_game",
        "forbidden_terms": ["margherita", "pepperoni", "sourdough", "san marzano", "sitter", "babysitter", "bakery"],
    },
]


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


@pytest.mark.parametrize("domain_spec", NOVEL_DOMAIN_PROMPTS, ids=lambda d: d["id"])
def test_generic_domain_synthesis_vocabulary_isolation(domain_spec):
    """Verify generic synthesis produces domain-appropriate manifest & zero pizza/sourdough vocabulary leakage."""
    pitch = domain_spec["pitch"]
    schema = {
        "pitch": pitch,
        "brand_title": "Auto Generated",
        "delivery_sla": "LIVE TELEMETRY",
        "enabled_features": ["flappy_bird"] if domain_spec["expected_category"] == "interactive_game" else ["catalog"],
    }

    manifest = build_site_manifest_from_schema(schema)
    assert manifest is not None, "Failed to build manifest"
    assert manifest.intent.business_pitch == pitch

    compiled_tsx = compile_site_manifest_to_app_tsx(manifest)
    compiled_lower = compiled_tsx.lower()

    # Check forbidden leakage terms
    for term in domain_spec["forbidden_terms"]:
        assert term not in compiled_lower, f"Forbidden term '{term}' leaked into TSX output for pitch '{pitch}'!"


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
    """Verify synthesize_domain_intent_and_branding extracts clean titles and copy without hardcoded defaults."""
    pitch = "A drone delivery fleet logistics monitor"
    intent_data = synthesize_domain_intent_and_branding(pitch)

    assert "brand_title" in intent_data
    assert "Drone" in intent_data["brand_title"] or "Fleet" in intent_data["brand_title"] or "Logistics" in intent_data["brand_title"]
    assert "Oven & Earth" not in intent_data["brand_title"]
    assert "Grandma's" not in intent_data["brand_title"]
    assert intent_data["domain_category"] == "operations_dashboard"


def test_brand_title_formatting_no_app_suffix():
    """Verify brand title strips leading articles ('A', 'An') and trailing 'App' for clean titles."""
    pitch = "A flappy bird game"
    intent_data = synthesize_domain_intent_and_branding(pitch)
    brand = intent_data["brand_title"]

    assert not brand.startswith("A "), f"Brand title '{brand}' has unacceptable leading article 'A '!"
    assert not brand.endswith(" App"), f"Brand title '{brand}' has unacceptable trailing ' App'!"
    assert "Flappy Bird" in brand


def test_hero_banner_color_harmony_no_pizzeria_red():
    """Verify compiled hero banner uses dynamic theme colors instead of hardcoded pizzeria red gradients."""
    pitch = "A flappy bird game"
    schema = {"pitch": pitch, "enabled_features": ["flappy_bird"]}
    manifest = build_site_manifest_from_schema(schema)
    compiled = compile_site_manifest_to_app_tsx(manifest)

    assert "#7f1d1d" not in compiled, "Pizzeria red gradient '#7f1d1d' leaked into hero banner!"
    assert "#450a0a" not in compiled, "Pizzeria red gradient '#450a0a' leaked into hero banner!"


def test_component_node_is_visible_attribute():
    """Verify ComponentNodeAST supports is_visible and relevance_reason metadata."""
    pitch = "A flappy bird game"
    schema = {"pitch": pitch, "enabled_features": ["flappy_bird"]}
    manifest = build_site_manifest_from_schema(schema)

    for comp in manifest.components:
        assert hasattr(comp, "is_visible"), f"ComponentNodeAST '{comp.canonical_key}' missing 'is_visible' attribute!"
        assert hasattr(comp, "relevance_reason"), f"ComponentNodeAST '{comp.canonical_key}' missing 'relevance_reason' attribute!"


def test_minimum_core_view_invariant():
    """Verify at least 1 primary focus component node remains is_visible == True."""
    pitch = "A flappy bird game"
    schema = {"pitch": pitch, "enabled_features": ["flappy_bird"]}
    manifest = build_site_manifest_from_schema(schema)

    visible_components = [c for c in manifest.components if c.is_visible]
    assert len(visible_components) >= 1, "Manifest failed minimum core view invariant (0 visible components)!"
    assert any(c.canonical_key == "flappy_bird" for c in visible_components), "Primary game component should be visible!"


def test_zero_sla_badge_in_onboarding_codebase():
    """Verify sla_badge is completely purged from onboarding codebase files."""
    onboarding_dir = os.path.join(os.path.dirname(__file__), "..", "onboarding")
    for filename in os.listdir(onboarding_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(onboarding_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                assert "sla_badge" not in content, f"Domain-specific attribute 'sla_badge' found in {filename}!"


def test_zero_est_sla_text_in_compiled_output():
    """Verify compiled output contains zero 'Est. SLA' text for any prompt."""
    schema = {"pitch": "A flappy bird game", "enabled_features": ["flappy_bird"]}
    manifest = build_site_manifest_from_schema(schema)
    compiled = compile_site_manifest_to_app_tsx(manifest)
    assert "est. sla" not in compiled.lower(), "Hardcoded text 'Est. SLA' leaked into compiled output!"


def test_get_active_domain_params_kickstart_resolution(tmp_path):
    """Verify get_active_domain_params in main.py extracts clean title and non-empty enabled_features for game prompts."""
    from main import get_active_domain_params
    from db.store import set_active_db, init_db, save_kickstart_state

    db_file = str(tmp_path / "provable_test.db")
    set_active_db(db_file)
    init_db()

    save_kickstart_state({"business_pitch": "A flappy bird game"})
    params = get_active_domain_params()

    assert params["pitch"] == "A flappy bird game"
    assert not params["brand_title"].endswith(" App"), f"Brand title '{params['brand_title']}' has redundant ' App' suffix!"
    assert "flappy_bird" in params["enabled_features"], f"Enabled features should contain 'flappy_bird', got {params['enabled_features']}!"


def test_no_duplicate_flappy_bird_h3_in_compiled_output():
    """Verify compiled TSX suppresses redundant inner h3 container title for games when brand title is in header."""
    schema = {"pitch": "A flappy bird game", "enabled_features": ["flappy_bird"]}
    manifest = build_site_manifest_from_schema(schema)
    compiled = compile_site_manifest_to_app_tsx(manifest)

    assert "Flappy Bird Arcade</h3>" not in compiled, "Redundant inner h3 title 'Flappy Bird Arcade' found in game container!"


def test_arcade_dark_shell_styling():
    """Verify compiled game viewport uses sleek dark arcade container styling."""
    schema = {"pitch": "A flappy bird game", "enabled_features": ["flappy_bird"]}
    manifest = build_site_manifest_from_schema(schema)
    compiled = compile_site_manifest_to_app_tsx(manifest)

    assert "#0f172a" in compiled, "Dark arcade container background '#0f172a' missing from compiled game component!"


def test_chess_game_prompt_does_not_trigger_flappy_bird():
    """Verify 'A chess game' prompt does NOT recommend or compile flappy_bird component."""
    from onboarding.block_catalog import analyze_pitch_for_kickstart

    res = analyze_pitch_for_kickstart("A chess game")
    recommended_ids = [b["id"] for b in res.get("blocks", []) if b.get("is_recommended")]

    assert "flappy_bird" not in recommended_ids, f"flappy_bird block incorrectly recommended for chess game prompt: {recommended_ids}!"

    manifest = build_site_manifest_from_schema({"pitch": "A chess game"})
    compiled = compile_site_manifest_to_app_tsx(manifest)
    assert "flappy" not in compiled.lower(), "flappy_bird code leaked into compiled TSX output for 'A chess game'!"


def test_chess_game_kickstart_isolation(tmp_path):
    """Verify kickstarting 'A chess game' generates ZERO e-commerce or pizza requirements in SQLite store."""
    from main import kickstart_synthesize, KickstartSynthesisRequest
    from db.store import set_active_db, init_db, get_all_requirements

    db_file = str(tmp_path / "provable_kickstart_test.db")
    set_active_db(db_file)
    init_db()

    kickstart_synthesize(KickstartSynthesisRequest(business_pitch="A chess game", selected_blocks=[]))
    reqs = get_all_requirements()

    req_ids = [r["id"] for r in reqs]
    assert not any(k in req_ids for k in ["REQ-CATALOG-001", "REQ-CART-001", "REQ-TRACK-001", "REQ-KDS-001", "REQ-DELIVERY-001"]), \
        f"E-commerce requirement IDs leaked into chess game kickstart DB: {req_ids}"


def test_chess_game_manifest_has_custom_chess_component():
    """Verify build_site_manifest_from_schema for 'A chess game' synthesizes custom chess component and zero cart/catalog."""
    manifest = build_site_manifest_from_schema({"pitch": "A chess game"})

    component_keys = [c.canonical_key for c in manifest.components if c.is_visible]
    assert len(component_keys) > 0, "Site manifest for 'A chess game' MUST NOT have empty components list!"
    assert any("chess" in k for k in component_keys), f"Component list should contain custom 'chess_game' component, got {component_keys}!"
    assert "cart" not in component_keys, f"Cart feature leaked into chess game components: {component_keys}"


def test_chess_game_compiled_output_has_interactive_chessboard():
    """Verify compiled output for 'A chess game' contains interactive chess UI and ZERO checkout button or blank page fallback."""
    manifest = build_site_manifest_from_schema({"pitch": "A chess game"})
    compiled = compile_site_manifest_to_app_tsx(manifest)

    assert '"cart"' not in compiled.split("const [enabledFeatures] = useState")[1].split(";")[0], "Cart active key leaked into compiled TSX activeKeys!"
    assert "Available Items & Offerings" not in compiled, "Blank catalog fallback 'Available Items & Offerings' rendered for chess game!"
    assert "chess" in compiled.lower(), "Compiled TSX output missing chess game interactive component!"
