import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from domain.model import resolve_canonical_feature
from onboarding.requirement_generator import _link_logic_reqs_to_ui_components

def test_resolve_canonical_feature_returns_req_ui_prefix():
    info = resolve_canonical_feature('catalog')
    assert info['canonical_key'] == 'catalog'
    assert 'REQ-UI-CATALOG' in info['req_ids']

def test_link_logic_reqs_attaches_to_active_components_without_ghosts():
    schema = {
        "title": "Pizza Ordering Website",
        "item_singular": "pizza",
        "item_plural": "pizzas",
        "pitch": "Order pizzas online with real-time tracking",
        "components": [
            {"canonical_key": "catalog", "name": "Product Catalog & Menu Grid"},
            {"canonical_key": "cart", "name": "Shopping Cart & Checkout Modal"},
            {"canonical_key": "tracking", "name": "Order Status & Tracking Pipeline"}
        ]
    }
    
    raw_logic_reqs = [
        {
            "id": "REQ-DOM-ORDER-001",
            "title": "Pizza Order State Machine & Integrity",
            "description": "Order entity state transitions for cart checkout.",
            "layer": "LOGIC"
        },
        {
            "id": "REQ-SVC-TRACK-001",
            "title": "Real-Time Order Tracking Service",
            "description": "Backend service calculating status pipeline for active pizzas.",
            "layer": "LOGIC"
        },
        {
            "id": "REQ-SVC-CATALOG-001",
            "title": "Catalog Search & Filter Engine",
            "description": "Fetch catalog items and filter pizzas by toppings.",
            "layer": "LOGIC"
        }
    ]

    linked = _link_logic_reqs_to_ui_components(raw_logic_reqs, schema)

    # 1. Verify top-level Presentation components use REQ-UI-* IDs
    presentation_ids = [r["id"] for r in linked if r.get("layer") == "PRESENTATION"]
    assert "REQ-UI-CATALOG" in presentation_ids
    assert "REQ-UI-CART" in presentation_ids
    assert "REQ-UI-TRACKING" in presentation_ids

    # 2. Verify ZERO ghost components (no REQ-UI-WORKFLOW or REQ-UI-STATUS)
    assert "REQ-UI-WORKFLOW" not in presentation_ids
    assert "REQ-UI-STATUS" not in presentation_ids

    # 3. Verify logic requirements have parent_id pointing to active presentation components
    catalog_logic = next(r for r in linked if r["id"] == "REQ-SVC-CATALOG-001")
    cart_logic = next(r for r in linked if r["id"] == "REQ-DOM-ORDER-001")
    track_logic = next(r for r in linked if r["id"] == "REQ-SVC-TRACK-001")

    assert catalog_logic.get("parentId") == "REQ-UI-CATALOG" or catalog_logic.get("parent_id") == "REQ-UI-CATALOG"
    assert cart_logic.get("parentId") == "REQ-UI-CART" or cart_logic.get("parent_id") == "REQ-UI-CART"
    assert track_logic.get("parentId") == "REQ-UI-TRACKING" or track_logic.get("parent_id") == "REQ-UI-TRACKING"


def test_synthesize_kickstart_stack_preserves_parent_linkage():
    from service_layer.services import synthesize_kickstart_stack
    from service_layer.unit_of_work import FakeUnitOfWork
    
    uow = FakeUnitOfWork()
    res = synthesize_kickstart_stack(
        business_pitch="Order artisan pizzas with real-time tracking",
        selected_blocks=["catalog", "cart", "tracking"],
        uow=uow
    )

    all_reqs = uow.requirements.list()
    presentation_reqs = [r for r in all_reqs if r.layer == "PRESENTATION" or r.id.startswith("REQ-UI")]
    child_reqs = [r for r in all_reqs if r.parent_id is not None]

    assert len(presentation_reqs) >= 3
    assert len(child_reqs) >= 1
    for child in child_reqs:
        assert child.parent_id in [p.id for p in presentation_reqs]

