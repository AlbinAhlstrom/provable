"""The fallback App.tsx must be driven by the blueprint, never by a hardcoded business domain."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.code_verifier import verify_tsx_syntax
from onboarding.frontend_planning_engine import (
    _generate_fallback_assembled_app,
    inject_data_fixtures_sync_to_tsx,
)
from onboarding.planning_contracts import (
    AestheticThemeSpec, BespokeComponentSpec, CategoryLayoutPlan, ComponentSlotAssignment,
    UnifiedFrontendBlueprint,
)

# Terms that belonged to the old hardcoded commerce / warehouse / booking templates.
LEGACY_TEMPLATE_TERMS = [
    "handleSimulatePayment", "ORD-", "handleAddToCart", "isCartOpen", "Baking", "checkout",
    "Pallet", "PAL-001", "ZONE-A1", "isAvailableSlot", "Fresh artisan offering", "$14.99",
]

DOMAINS = [
    # (pitch, category_id that used to select a hardcoded template, title, singular, plural, seed)
    ("An app to order pizza", "e_commerce", "SliceCraft", "pizza", "pizzas",
     [{"id": "1", "name": "Margherita", "price": 12.5, "toppings": ["basil"]}]),
    ("Warehouse pallet tracking", "operations_dashboard", "Pallet Tracker", "pallet", "pallets",
     [{"id": "P1", "sku": "SKU-1", "weight": 450.0}]),
    ("Clinic booking", "service_booking", "ClinicHive", "doctor", "doctors",
     [{"id": "d1", "title": "Dr. Rivera", "specialty": "Cardiology"}]),
    ("Quantum circuit lab", "custom", "QubitBench", "qubit", "qubits",
     [{"id": "q1", "name": "Q0", "phase": 0.25}]),
]


def _blueprint(pitch, cat, title, singular, plural, seed, components=()):
    return UnifiedFrontendBlueprint(
        business_pitch=pitch,
        category_layout=CategoryLayoutPlan(category_id=cat, layout_name="L", category_reasoning="r", slots=[]),
        components=ComponentSlotAssignment(bespoke_components=list(components)),
        aesthetics=AestheticThemeSpec(
            domain_display_title=title, mock_seed_data=seed, item_singular=singular, item_plural=plural,
            hero_headline=f"All your {plural}", guarantee_badge="Verified", action_button_text=f"Add {singular}",
        ),
    )


@pytest.mark.parametrize("pitch,cat,title,singular,plural,seed", DOMAINS)
def test_fallback_has_no_legacy_template_content(pitch, cat, title, singular, plural, seed):
    """Verify no old hardcoded commerce/warehouse/booking content leaks into the fallback.

    id: TST-FB-001
    Given: Blueprints that used to trigger the commerce, warehouse and booking templates
    When: The fallback App.tsx is generated
    Then: It contains the blueprint's own data, none of the legacy template terms, and valid syntax
    """
    code = _generate_fallback_assembled_app(_blueprint(pitch, cat, title, singular, plural, seed))

    assert title in code and plural in code
    assert seed[0].get("name", seed[0].get("title", seed[0].get("sku"))) in code
    own_text = (pitch + title + singular + plural + str(seed)).lower()
    for term in LEGACY_TEMPLATE_TERMS:
        if term.lower() not in own_text:
            assert term not in code, f"legacy template term {term!r} leaked into fallback for {title}"
    ok, err = verify_tsx_syntax(code)
    assert ok, err


def test_fallback_renders_planned_components_and_empty_state():
    """Verify bespoke components from planning are rendered and an empty collection has an empty state.

    id: TST-FB-002
    Given: A blueprint with a bespoke component and no seed data
    When: The fallback is generated
    Then: The component spec is embedded and the empty-state branch exists
    """
    comp = BespokeComponentSpec(component_name="DoseScheduler", slot="main_content",
                                description="Schedules doses", key_interactions=["Drag a dose"])
    code = _generate_fallback_assembled_app(_blueprint("Pharmacy", "custom", "PharmaPlan", "dose", "doses", [], [comp]))
    assert "DoseScheduler" in code and "Drag a dose" in code
    assert "No {PLURAL} yet" in code


def test_fallback_keeps_bidirectional_fixture_sync_contract():
    """Verify the fallback still syncs with PM Studio through the `catalog` fixture key.

    id: TST-FB-003
    Given: The generated fallback App.tsx
    When: Its source is inspected
    Then: It has an items setter, a message listener, a fixtures fetch and a postMessage back to the host
    """
    code = _generate_fallback_assembled_app(_blueprint(*DOMAINS[0]))
    assert "const [items, setItems] = useState" in code
    assert "addEventListener('message'" in code
    assert "FIXTURES_UPDATED" in code and "postMessage" in code
    assert "/api/components/fixtures/update" in code
    assert "syncFixtureToBackendAndHost('catalog'" in code


def test_injected_sync_snippet_is_domain_neutral():
    """Verify the sync snippet injected into LLM-generated apps references only `items`.

    id: TST-FB-004
    Given: A minimal LLM-style App.tsx with an items state but no message listener
    When: Fixture sync is injected
    Then: The snippet handles `catalog` via setItems and never references cart/order state
    """
    src = "import React, {useState} from 'react';\nexport default function App() {\n  const [items] = useState([]);\n  return <div/>;\n}\n"
    out = inject_data_fixtures_sync_to_tsx(src, custom_fixtures={"catalog": [{"id": "a", "name": "Thing"}]})
    assert "setItems" in out and "FIXTURES_UPDATED" in out
    assert "setCart" not in out and "setOrders" not in out
    assert "Thing" in out
