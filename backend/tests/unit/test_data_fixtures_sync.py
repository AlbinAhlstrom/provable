"""
Unit tests for Data Fixtures sync in the Service Layer (domain-neutral: `catalog` is the primary collection; other collections appear only once saved).
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import KickstartState, Requirement
from service_layer.unit_of_work import FakeUnitOfWork
from adapters.workspace import FakeWorkspaceAdapter
from service_layer import services


def test_get_component_data_fixtures_default_pizza_app():
    """
    Given a pizzeria kickstart state in FakeUnitOfWork
    When get_component_data_fixtures is called
    Then catalog fixtures contain the seed items and no other collections are invented.
    """
    ks = KickstartState(
        business_pitch="An app to order pizza online with cart and tracking",
        blocks=["catalog", "cart", "tracking"],
        extracted_requirements=[],
        synthesized=True
    )
    uow = FakeUnitOfWork(initial_kickstart=ks)

    res = services.get_component_data_fixtures(uow=uow)

    assert res["success"] is True
    fixtures = res["fixtures"]
    assert "catalog" in fixtures
    assert len(fixtures["catalog"]) >= 2
    # Verify pizza catalog item names
    catalog_names = [item["name"] for item in fixtures["catalog"]]
    assert any("Pizza" in name or "Margherita" in name or "Pepperoni" in name for name in catalog_names)

    # No commerce collections are invented: only `catalog` exists until something saves another one.
    assert set(fixtures) == {"catalog"}


def test_update_component_data_fixtures_crud_sync():
    """
    Given an active domain kickstart state
    When update_component_data_fixtures is called to add a new catalog item
    Then the new item is stored in the domain fixtures and returned by get_component_data_fixtures.
    """
    ks = KickstartState(
        business_pitch="An app to order pizza online",
        blocks=["catalog", "cart"],
        extracted_requirements=[],
        synthesized=True
    )
    uow = FakeUnitOfWork(initial_kickstart=ks)
    ws = FakeWorkspaceAdapter()

    # Initial fixtures
    init_res = services.get_component_data_fixtures(uow=uow)
    init_catalog = init_res["fixtures"]["catalog"]

    # Add new item: Hawaiian Supreme ($17.99)
    new_item = {"id": "fix-12345", "name": "Hawaiian Supreme", "price": 17.99}
    updated_catalog = init_catalog + [new_item]

    update_res = services.update_component_data_fixtures(
        canonical_key="catalog",
        fixtures=updated_catalog,
        uow=uow,
        workspace=ws
    )

    assert update_res["success"] is True

    # Verify updated fixtures
    res_after = services.get_component_data_fixtures(uow=uow)
    names_after = [i["name"] for i in res_after["fixtures"]["catalog"]]
    assert "Hawaiian Supreme" in names_after


def test_bidirectional_data_fixtures_sync_pm_studio_to_app_preview():
    """
    Direction A: PM Studio -> live App preview
    Given updated custom fixtures saved from PM Studio
    When sync_workspace_app_shell generates App.tsx template
    Then App.tsx initializes menu items from custom_fixtures and contains postMessage sync event handlers.
    """
    from onboarding.frontend_planning_engine import _generate_fallback_assembled_app
    from onboarding.planning_contracts import (
        UnifiedFrontendBlueprint, CategoryLayoutPlan, ComponentSlotAssignment, AestheticThemeSpec
    )

    custom_catalog = [
        {"id": "fix-1", "name": "Truffle Mushroom Supreme", "price": 24.99, "desc": "Gourmet mushroom pizza"},
        {"id": "fix-2", "name": "Four Cheese Delight", "price": 18.99, "desc": "Mozzarella, gorgonzola, parmesan"}
    ]

    bp = UnifiedFrontendBlueprint(
        business_pitch="An app to order pizza online",
        category_layout=CategoryLayoutPlan(
            category_id="e_commerce",
            layout_name="Storefront",
            category_reasoning="Pizza ordering app",
            slots=[]
        ),
        components=ComponentSlotAssignment(),
        aesthetics=AestheticThemeSpec(
            domain_display_title="Pizzeria App",
            hero_headline="Fresh Pizza Delivered",
            mock_seed_data=custom_catalog
        )
    )

    code = _generate_fallback_assembled_app(bp, custom_fixtures={"catalog": custom_catalog, "cart": [], "tracking": []})

    assert "Truffle Mushroom Supreme" in code
    assert "24.99" in code
    # Check for bidirectional window.parent.postMessage in App.tsx handlers
    assert "postMessage" in code
    assert "FIXTURES_UPDATED" in code


def test_bidirectional_data_fixtures_sync_app_preview_to_pm_studio():
    """
    Direction B: live App preview -> PM Studio
    Given live App preview sends an updated cart/order list via update_component_data_fixtures API
    When service layer updates custom_fixtures in KickstartState
    Then get_component_data_fixtures immediately returns the updated cart and tracking fixtures.
    """
    ks = KickstartState(
        business_pitch="An app to order pizza online",
        blocks=["catalog", "cart", "tracking"],
        synthesized=True
    )
    uow = FakeUnitOfWork(initial_kickstart=ks)
    ws = FakeWorkspaceAdapter()

    # Simulate live App preview adding an item to cart and syncing to backend
    live_cart = [{"id": "item-1", "title": "Margherita Speciale", "price_or_rate": "$16.99", "qty": 2}]
    res_cart = services.update_component_data_fixtures(
        canonical_key="cart",
        fixtures=live_cart,
        uow=uow,
        workspace=ws
    )
    assert res_cart["success"] is True

    # Simulate live App preview placing an order and syncing to tracking
    live_order = [{"id": "ORD-5555", "ref": "ORD-5555", "status": "Baking", "eta": "15 Mins", "item": "Margherita Speciale"}]
    res_track = services.update_component_data_fixtures(
        canonical_key="tracking",
        fixtures=live_order,
        uow=uow,
        workspace=ws
    )
    assert res_track["success"] is True

    # Verify PM Studio get_component_data_fixtures returns live cart & tracking
    all_fixtures = services.get_component_data_fixtures(uow=uow)["fixtures"]
    assert len(all_fixtures["cart"]) == 1
    assert all_fixtures["cart"][0]["title"] == "Margherita Speciale"
    assert len(all_fixtures["tracking"]) == 1
    assert all_fixtures["tracking"][0]["id"] == "ORD-5555"


def test_app_tsx_has_items_setter_and_message_listener():
    """
    Verify that generated App.tsx includes setItems state setter AND window.addEventListener('message')
    handler to dynamically update catalog items when PM Studio sends FIXTURES_UPDATED events.
    """
    from onboarding.frontend_planning_engine import _generate_fallback_assembled_app
    from onboarding.planning_contracts import (
        UnifiedFrontendBlueprint, CategoryLayoutPlan, ComponentSlotAssignment, AestheticThemeSpec
    )

    bp = UnifiedFrontendBlueprint(
        business_pitch="An app to order pizza online",
        category_layout=CategoryLayoutPlan(
            category_id="e_commerce",
            layout_name="Storefront",
            category_reasoning="Pizza ordering app",
            slots=[]
        ),
        components=ComponentSlotAssignment(),
        aesthetics=AestheticThemeSpec(
            domain_display_title="Pizzeria App",
            hero_headline="Fresh Pizza Delivered",
            mock_seed_data=[{"id": "1", "name": "Margherita Speciale", "price": 16.99}]
        )
    )

    code = _generate_fallback_assembled_app(bp)

    assert "const [items, setItems] = useState" in code, "items state missing setter function (setItems)!"
    assert "setItems(" in code, "App.tsx lacks setItems(...) call for dynamic catalog updates!"
    assert "addEventListener('message'" in code, "App.tsx lacks window message listener!"

