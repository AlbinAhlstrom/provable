"""
Unit test suite verifying Universal Domain Entity Linking across Catalog, Cart, and Order Tracking.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import KickstartState
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_get_component_entities_returns_default_catalog_and_empty_cart_tracking():
    """Verify that get_component_data_fixtures derives domain catalog and initializes empty cart/tracking."""
    initial_state = KickstartState(
        business_pitch="An app to order pizzas",
        custom_fixtures={}
    )
    uow = FakeUnitOfWork(initial_kickstart=initial_state)

    res = services.get_component_data_fixtures(uow=uow)
    assert res["success"] is True
    fixtures = res["fixtures"]
    assert "catalog" in fixtures
    assert len(fixtures["catalog"]) > 0
    assert "cart" in fixtures
    assert fixtures["cart"] == []
    assert "tracking" in fixtures
    assert fixtures["tracking"] == []


def test_update_cart_entity_preserves_catalog_reference_and_quantity():
    """Verify updating cart entities stores catalog item data with quantity."""
    initial_state = KickstartState(
        business_pitch="An app to order pizzas",
        custom_fixtures={}
    )
    uow = FakeUnitOfWork(initial_kickstart=initial_state)

    cart_item = {
        "id": "fix-cart-1",
        "name": "Margherita Pizza",
        "price": 12.99,
        "quantity": 2,
        "catalog_id": "fix-1"
    }

    res = services.update_component_data_fixtures(
        canonical_key="cart",
        fixtures=[cart_item],
        uow=uow
    )
    assert res["success"] is True
    assert uow.kickstart.get().custom_fixtures["cart"] == [cart_item]


def test_update_tracking_entity_creates_valid_order_transaction():
    """Verify updating tracking entities creates valid order transaction records with status."""
    initial_state = KickstartState(
        business_pitch="An app to order pizzas",
        custom_fixtures={}
    )
    uow = FakeUnitOfWork(initial_kickstart=initial_state)

    order_entity = {
        "id": "ORD-5432",
        "name": "Order #5432 (Margherita Pizza)",
        "price": 25.98,
        "status": "Preparing",
        "item": "Margherita Pizza (x2)"
    }

    res = services.update_component_data_fixtures(
        canonical_key="tracking",
        fixtures=[order_entity],
        uow=uow
    )
    assert res["success"] is True
    assert uow.kickstart.get().custom_fixtures["tracking"] == [order_entity]
