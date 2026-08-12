"""
AST Pipeline Inspection Script.
Generates full UnifiedSiteManifestAST JSON documents for diverse business prompts
to enable critical analysis of AST structure, field mappings, and synthesis flaws.
"""

import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.site_manifest_schema import UnifiedSiteManifestAST
from onboarding.dynamic_domain_generator import build_site_manifest_from_schema
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx

TEST_PROMPTS = [
    {
        "name": "Pizzeria Order & Delivery",
        "schema": {
            "pitch": "A wood-fired sourdough pizzeria called Oven & Earthling with custom pizza builder, live order tracking, and customer reviews",
            "delivery_sla": "15–25 MINS",
            "enabled_features": ["catalog", "cart", "tracking", "reviews", "custom_item_builder"]
        }
    },
    {
        "name": "Artisan Bakery Storefront",
        "schema": {
            "pitch": "Gourmet French bakery called Grandma's Bakery with morning pastry pre-orders and loyalty rewards",
            "brand_title": "Grandma's Artisan Bakery",
            "delivery_sla": "10–15 MINS",
            "enabled_features": ["catalog", "cart", "tracking", "reviews", "loyalty_points", "table_reservation_calendar"]
        }
    },
    {
        "name": "Pet Grooming & Appointment Booking",
        "schema": {
            "pitch": "Paws & Claws pet grooming parlor with online appointment calendar and driver pet pickup",
            "brand_title": "Paws & Claws Pet Care",
            "delivery_sla": "Same Day Slot",
            "enabled_features": ["catalog", "cart", "tracking", "reviews", "table_reservation_calendar", "live_delivery_driver_map"]
        }
    },
    {
        "name": "Luxury Sports Car Rental",
        "schema": {
            "pitch": "Prestige Rentals executive luxury supercar rental with live GPS driver delivery map",
            "brand_title": "Prestige Executive Rentals",
            "delivery_sla": "24h Concierge",
            "enabled_features": ["catalog", "cart", "tracking", "reviews", "live_delivery_driver_map", "payment_system"]
        }
    }
]


def run_ast_inspection():
    print("=" * 80)
    print("🔍 AST PIPELINE MULTI-PROMPT INSPECTION REPORT")
    print("=" * 80)

    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tmp_ast_test'))
    os.makedirs(tmp_dir, exist_ok=True)

    results = []

    for test in TEST_PROMPTS:
        print(f"\n📌 PROMPT: {test['name']}")
        print(f"   Pitch: \"{test['schema']['pitch']}\"")
        
        manifest = build_site_manifest_from_schema(test['schema'], tmp_dir)
        manifest_dict = json.loads(manifest.to_json())
        compiled_tsx = compile_site_manifest_to_app_tsx(manifest)

        results.append({
            "name": test["name"],
            "manifest": manifest_dict,
            "tsx_length": len(compiled_tsx)
        })

        print("\n--- GENERATED AST MANIFEST (JSON Summary) ---")
        print(f"Brand Title: {manifest_dict['layout']['header']['brand_title']}")
        print(f"Domain Category: {manifest_dict['intent']['domain_category']}")
        print(f"Hero Headline: {manifest_dict['layout']['hero_banner']['headline']}")
        print(f"Hero Badges: {manifest_dict['layout']['hero_banner']['badges']}")
        print("Active Components:")
        for c in manifest_dict['components']:
            print(f"   - [{c['icon']}] {c['name']} (key: {c['canonical_key']}, type: {c['component_type']})")
        print("Navigation Routes:")
        for r in manifest_dict['layout']['navigation_routes']:
            print(f"   - [{r['icon']}] {r['label']} (ref: {r['component_ref']})")
        print(f"Compiled TSX Size: {len(compiled_tsx)} chars")

    return results


if __name__ == "__main__":
    run_ast_inspection()
