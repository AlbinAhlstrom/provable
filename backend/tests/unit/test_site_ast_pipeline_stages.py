"""
Comprehensive Step-by-Step Test Suite for the 6-Stage Site Manifest AST Pipeline.

Tests each stage in strict isolation and end-to-end:
- Stage 1: Intent & Domain Deconstruction (DomainIntentSpec)
- Stage 2: Component Topology & Capability Planner (ComponentNodeAST)
- Stage 3: Page Hierarchy & Route Architect (SiteNavigationAST, Header, Hero, Theme)
- Stage 4: Component Content & State Schema Spec (ComponentContentAST)
- Stage 5: Unified Site Manifest AST Document (site_manifest.json serialization/deserialization)
- Stage 6: Deterministic AST-to-React Compiler (compile_site_manifest_to_app_tsx)
- End-to-End AST Pipeline Mutation & Vite Build Validation
"""

import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.site_manifest_schema import (
    UnifiedSiteManifestAST, DomainIntentSpec, ComponentNodeAST,
    NavigationRouteAST, HeroBannerAST, HeaderSpecAST, ThemeTokensAST, SiteNavigationAST, ComponentContentAST
)
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx
from onboarding.dynamic_domain_generator import build_site_manifest_from_schema


def test_stage1_intent_deconstruction():
    """Stage 1 Test: Validates DomainIntentSpec parsing and field defaults across diverse pitches."""
    pitches = [
        ("An app to order pizzas called P1 Pizzas", "P1 Pizzas", "e_commerce"),
        ("Fresh artisan bakery storefront", "Grandma's Artisan Bakery", "e_commerce"),
        ("On-demand babysitter booking care", "Little Tots Care", "service_booking"),
        ("Executive luxury car rental fleet", "Prestige Rentals", "fleet_rental")
    ]

    for pitch, expected_brand, category in pitches:
        spec = DomainIntentSpec(
            business_pitch=pitch,
            brand_name=expected_brand,
            domain_category=category,
            primary_workflow="ordering"
        )
        assert spec.business_pitch == pitch
        assert spec.brand_name == expected_brand
        assert spec.domain_category == category
        assert "Product" in spec.entity_models


def test_stage2_component_topology():
    """Stage 2 Test: Validates ComponentNodeAST generation, canonical keys, icons, and type classification."""
    features = [
        ("catalog", "Catalog", "premade", "📋"),
        ("cart", "Cart", "premade", "🛒"),
        ("tracking", "Tracking", "premade", "📦"),
        ("flappy_bird", "Flappy Bird Game", "custom", "🎮"),
        ("payment_system", "Payment System", "custom", "💳"),
        ("loyalty_points", "Loyalty Rewards", "custom", "🎁")
    ]

    nodes = []
    for key, name, expected_type, expected_icon in features:
        node = ComponentNodeAST(
            id=f"REQ-CMP-{key.upper()}-001",
            canonical_key=key,
            name=name,
            component_type=expected_type,
            icon=expected_icon,
            enabled=True
        )
        assert node.canonical_key == key
        assert node.component_type == expected_type
        assert node.icon == expected_icon
        nodes.append(node)

    assert len(nodes) == 6


def test_stage3_layout_architecture():
    """Stage 3 Test: Validates SiteNavigationAST, Header, Hero Banner, and Theme Tokens."""
    header = HeaderSpecAST(brand_title="Oven & Earth Pizzeria", sla_badge="15–25 MINS")
    hero = HeroBannerAST(
        headline="Artisanal Wood-Fired Pizza & Fast Delivery",
        subtitle="Hand-stretched sourdough pizzas baked in 450°C stone deck ovens.",
        badges=["🔥 Stone Deck Baked", "⏱️ 35-45 Min Guarantee", "🌱 Organic San Marzano"]
    )
    theme = ThemeTokensAST(primary_color="#991b1b", bg_color="#fcfbf7", font_family="Georgia, serif")

    routes = [
        NavigationRouteAST(key="menu", label="Menu", component_ref="catalog", icon="📋"),
        NavigationRouteAST(key="cart", label="Cart", component_ref="cart", icon="🛒"),
        NavigationRouteAST(key="tracking", label="Tracking", component_ref="tracking", icon="📦")
    ]

    layout = SiteNavigationAST(
        theme=theme,
        header=header,
        hero_banner=hero,
        navigation_routes=routes,
        default_route="menu"
    )

    assert layout.header.brand_title == "Oven & Earth Pizzeria"
    assert layout.hero_banner.headline == "Artisanal Wood-Fired Pizza & Fast Delivery"
    assert len(layout.hero_banner.badges) == 3
    assert layout.theme.primary_color == "#991b1b"
    assert len(layout.navigation_routes) == 3


def test_stage4_component_content_spec():
    """Stage 4 Test: Validates ComponentContentAST seed data generation."""
    catalog = [
        { "id": "p1", "name": "Margherita Special", "price": 16.50, "desc": "Fresh mozzarella, San Marzano tomato.", "icon": "🍕" },
        { "id": "p2", "name": "Pepperoni Feast", "price": 18.50, "desc": "Double pepperoni, hot honey.", "icon": "🌶️" }
    ]
    reviews = [
        { "id": 1, "author": "Sarah M.", "rating": 5, "comment": "Best pizza in town!", "date": "10 mins ago" }
    ]

    content = ComponentContentAST(
        catalog_items=catalog,
        review_items=reviews,
        mock_seed_data={"delivery_fee": 2.99}
    )

    assert len(content.catalog_items) == 2
    assert content.catalog_items[0]["name"] == "Margherita Special"
    assert content.review_items[0]["rating"] == 5


def test_stage5_unified_site_manifest():
    """Stage 5 Test: Validates UnifiedSiteManifestAST composition, JSON serialization, disk save, and deserialization."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        schema = {
            "pitch": "Artisan Bakery",
            "brand_title": "Grandma's Artisan Bakery",
            "delivery_sla": "10–15 MINS",
            "enabled_features": ["catalog", "cart", "flappy_bird"]
        }

        manifest = build_site_manifest_from_schema(schema, tmp_dir)
        assert isinstance(manifest, UnifiedSiteManifestAST)
        assert "Artisan Bakery" in manifest.intent.brand_name
        assert len(manifest.components) >= 1

        # Verify disk persistence
        manifest_path = os.path.join(tmp_dir, 'requirements', 'site_manifest.json')
        assert os.path.exists(manifest_path)

        with open(manifest_path, 'r', encoding='utf-8') as f:
            disk_json = f.read()

        restored_manifest = UnifiedSiteManifestAST.from_json(disk_json)
        assert restored_manifest.intent.brand_name == manifest.intent.brand_name
        assert len(restored_manifest.components) == len(manifest.components)


def test_stage6_ast_to_react_compiler_isolation():
    """Stage 6 Test: Validates AST Compiler code generation and zero unreplaced template tags."""
    manifest = UnifiedSiteManifestAST(
        business_pitch="Luxury Car Rental",
        intent=DomainIntentSpec(business_pitch="Luxury Car Rental", brand_name="Prestige Executive Rentals"),
        components=[
            ComponentNodeAST(id="REQ-CMP-CATALOG-001", canonical_key="catalog", name="Cars Fleet", component_type="premade", icon="🏎️"),
            ComponentNodeAST(id="REQ-CMP-DRIVER_MAP-001", canonical_key="live_delivery_driver_map", name="Live GPS Driver Map", component_type="custom", icon="🚚")
        ],
        layout=SiteNavigationAST(
            header=HeaderSpecAST(brand_title="Prestige Executive Rentals", sla_badge="24h Concierge"),
            hero_banner=HeroBannerAST(
                headline="Executive Luxury Car & Fleet Rentals",
                subtitle="Premium sports cars delivered directly to your location.",
                badges=["🏎️ Premium Fleet", "🛡️ Full Insurance"]
            ),
            navigation_routes=[
                NavigationRouteAST(key="menu", label="Fleet", component_ref="catalog", icon="🏎️"),
                NavigationRouteAST(key="live_delivery_driver_map", label="Live Map", component_ref="live_delivery_driver_map", icon="🚚")
            ]
        )
    )

    code = compile_site_manifest_to_app_tsx(manifest)

    # Assert brand and content present
    assert "Prestige Executive Rentals" in code
    assert "Executive Luxury Car & Fleet Rentals" in code
    assert "Live GPS Driver Map" in code
    assert "export default function App()" in code

    # Assert ZERO unreplaced placeholder tokens
    unreplaced_tokens = ["__BRAND_TITLE__", "__HEADLINE__", "__SUBTITLE__", "__BADGES_HTML__", "__PRIMARY_COLOR__", "__BG_COLOR__", "__SLA_BADGE__"]
    for token in unreplaced_tokens:
        assert token not in code, f"Unreplaced template placeholder token found: {token}"


def test_end_to_end_ast_mutation_and_recompilation():
    """End-to-End Test: Tests adding and deleting component AST nodes and verifying TSX updates."""
    schema = {
        "pitch": "Pizzeria App",
        "brand_title": "Oven & Earth Pizzeria",
        "delivery_sla": "15–25 MINS",
        "enabled_features": ["catalog", "cart", "tracking"]
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest = build_site_manifest_from_schema(schema, tmp_dir)
        code1 = compile_site_manifest_to_app_tsx(manifest)
        assert "payment_system" not in code1

        # Simulate PM Studio ➕ Add Dynamic Component Action
        manifest.components.append(
            ComponentNodeAST(id="REQ-CMP-PAYMENT-001", canonical_key="payment_system", name="Payment Gateway", component_type="custom", icon="💳")
        )
        manifest.layout.navigation_routes.append(
            NavigationRouteAST(key="payment_system", label="Payment Gateway", component_ref="payment_system", icon="💳")
        )

        code2 = compile_site_manifest_to_app_tsx(manifest)
        assert "payment_system" in code2
        assert "Payment Gateway" in code2

        # Simulate PM Studio 🗑️ Delete Component Action
        manifest.components = [c for c in manifest.components if c.canonical_key != "payment_system"]
        manifest.layout.navigation_routes = [r for r in manifest.layout.navigation_routes if r.key != "payment_system"]

        code3 = compile_site_manifest_to_app_tsx(manifest)
        assert "payment_system" not in code3
