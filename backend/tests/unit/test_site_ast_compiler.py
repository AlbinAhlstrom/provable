"""
Unit Test Suite for Site Manifest AST Pipeline & Stage 6 AST Compiler.
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.site_manifest_schema import (
    UnifiedSiteManifestAST, DomainIntentSpec, ComponentNodeAST,
    NavigationRouteAST, HeroBannerAST, HeaderSpecAST, SiteNavigationAST, ComponentContentAST
)
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx


def test_site_manifest_ast_serialization():
    """Verifies Pydantic AST schema construction, JSON serialization, and deserialization."""
    intent = DomainIntentSpec(
        business_pitch="Fresh Bakery Storefront",
        brand_name="Grandma's Artisan Bakery",
        domain_category="e_commerce"
    )

    components = [
        ComponentNodeAST(id="REQ-CMP-CATALOG-001", canonical_key="catalog", name="Breads Menu", component_type="premade", icon="🥐"),
        ComponentNodeAST(id="REQ-CMP-FLAPPY-001", canonical_key="flappy_bird", name="Bakery Game", component_type="custom", icon="🎮")
    ]

    layout = SiteNavigationAST(
        header=HeaderSpecAST(brand_title="Grandma's Artisan Bakery", sla_badge="10-15 MINS"),
        hero_banner=HeroBannerAST(
            headline="Fresh Daily Breads & Pastries",
            subtitle="Handcrafted organic sourdough breads baked every morning.",
            badges=["🌾 Organic Flour", "🥐 French Butter"]
        ),
        navigation_routes=[
            NavigationRouteAST(key="menu", label="Breads", component_ref="catalog", icon="🥐"),
            NavigationRouteAST(key="flappy_bird", label="Flappy Game", component_ref="flappy_bird", icon="🎮")
        ]
    )

    manifest = UnifiedSiteManifestAST(
        business_pitch="Fresh Bakery Storefront",
        intent=intent,
        components=components,
        layout=layout,
        content=ComponentContentAST()
    )

    # Test serialization
    json_str = manifest.to_json()
    assert "Grandma's Artisan Bakery" in json_str
    assert "Fresh Daily Breads & Pastries" in json_str

    # Test deserialization
    restored = UnifiedSiteManifestAST.from_json(json_str)
    assert restored.intent.brand_name == "Grandma's Artisan Bakery"
    assert len(restored.components) == 2
    assert restored.components[1].canonical_key == "flappy_bird"


def test_ast_to_react_compiler():
    """Verifies Stage 6 AST Compiler emits clean, valid React 18 TSX code."""
    manifest = UnifiedSiteManifestAST(
        business_pitch="Babysitter Booking Service",
        intent=DomainIntentSpec(business_pitch="Babysitter Booking", brand_name="Little Tots Care"),
        components=[
            ComponentNodeAST(id="REQ-CMP-CATALOG-001", canonical_key="catalog", name="Sitters", component_type="premade", icon="👶"),
            ComponentNodeAST(id="REQ-CMP-PAYMENT-001", canonical_key="payment_system", name="Payment System", component_type="custom", icon="💳")
        ],
        layout=SiteNavigationAST(
            header=HeaderSpecAST(brand_title="Little Tots Nanny Care"),
            hero_banner=HeroBannerAST(headline="Verified Sitters", subtitle="Trustworthy child care.", badges=["🛡️ Verified"]),
            navigation_routes=[NavigationRouteAST(key="menu", label="Sitters", component_ref="catalog", icon="👶")]
        )
    )

    code = compile_site_manifest_to_app_tsx(manifest)
    assert "Little Tots Nanny Care" in code
    assert "Verified Sitters" in code
    assert "export default function App()" in code
    assert "__HEADLINE__" not in code
    assert "__BRAND_TITLE__" not in code


def test_dynamic_component_ast_mutation():
    """Verifies dynamic component node addition and deletion in AST manifest."""
    manifest = UnifiedSiteManifestAST(
        business_pitch="Pizzeria App",
        intent=DomainIntentSpec(business_pitch="Pizzeria App", brand_name="P1 Pizzas"),
        components=[
            ComponentNodeAST(id="REQ-CMP-CATALOG-001", canonical_key="catalog", name="Menu", component_type="premade", icon="🍕")
        ]
    )

    initial_code = compile_site_manifest_to_app_tsx(manifest)
    assert "loyalty_points" not in initial_code

    # Mutation: Add dynamic loyalty component AST node
    manifest.components.append(
        ComponentNodeAST(id="REQ-CMP-LOYALTY-001", canonical_key="loyalty_points", name="Loyalty Rewards", component_type="custom", icon="🎁")
    )
    manifest.layout.navigation_routes.append(
        NavigationRouteAST(key="loyalty_points", label="Loyalty Rewards", component_ref="loyalty_points", icon="🎁")
    )

    updated_code = compile_site_manifest_to_app_tsx(manifest)
    assert "loyalty_points" in updated_code
    assert "Loyalty Rewards" in updated_code

    # Mutation: Delete dynamic component AST node
    manifest.components = [c for c in manifest.components if c.canonical_key != "loyalty_points"]
    manifest.layout.navigation_routes = [r for r in manifest.layout.navigation_routes if r.key != "loyalty_points"]

    final_code = compile_site_manifest_to_app_tsx(manifest)
    assert "loyalty_points" not in final_code
