"""
Unit tests for Data Fixtures sync and empty cart/tracking initial state in Service Layer.
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
    Then catalog fixtures contain pizza seed items, while cart and tracking fixtures start empty.
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

    # Cart and tracking fixtures MUST start empty by default (no pre-existing order!)
    assert fixtures.get("cart") == []
    assert fixtures.get("tracking") == []


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
