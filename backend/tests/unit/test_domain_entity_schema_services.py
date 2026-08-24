"""
Unit tests for Domain Entity Schema & DDD Evolution services using FakeUnitOfWork.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import KickstartState, EntityAttribute, DomainEntitySchema
from service_layer import services
from service_layer.unit_of_work import FakeUnitOfWork
from adapters.workspace import FakeWorkspaceAdapter


def test_get_component_entity_schemas_default_pizzeria():
    """
    GIVEN a FakeUnitOfWork with a pizzeria KickstartState
    WHEN get_component_entity_schemas is called
    THEN it returns default entity schemas for 'catalog' with entity_name 'Pizza' and attributes [name, price, ingredients]
    """
    ks = KickstartState(business_pitch="An app to order pizzas")
    uow = FakeUnitOfWork(initial_kickstart=ks)

    result = services.get_component_entity_schemas(uow=uow)
    assert result["success"] is True
    schemas = result["schemas"]
    assert "catalog" in schemas
    catalog_schema = schemas["catalog"]
    assert catalog_schema["entity_name"].lower() == "pizza"
    
    attr_names = [a["name"] for a in catalog_schema["attributes"]]
    assert "name" in attr_names
    assert "price" in attr_names
    assert any(tag in attr_names for tag in ["specs", "ingredients", "specialties"])


def test_update_component_entity_schema_adds_attribute():
    """
    GIVEN a FakeUnitOfWork with existing catalog fixtures
    WHEN update_component_entity_schema adds a new attribute 'calories' of type 'number'
    THEN the schema is updated in kickstart state and existing fixtures receive default attribute values
    """
    existing_catalog = [
        {"id": "fix-1", "name": "Margherita", "price": 14.99, "ingredients": ["Tomato", "Mozzarella"]}
    ]
    ks = KickstartState(
        business_pitch="An app to order pizzas",
        custom_fixtures={"catalog": existing_catalog}
    )
    uow = FakeUnitOfWork(initial_kickstart=ks)
    ws = FakeWorkspaceAdapter()

    new_attributes = [
        {"name": "name", "type": "string", "required": True},
        {"name": "price", "type": "currency", "required": True},
        {"name": "ingredients", "type": "tags", "required": False},
        {"name": "calories", "type": "number", "required": False, "default_value": 800}
    ]

    res = services.update_component_entity_schema(
        canonical_key="catalog",
        entity_name="Pizza",
        attributes=new_attributes,
        uow=uow,
        workspace=ws
    )

    assert res["success"] is True
    assert uow.committed is True

    # Verify schema in kickstart state
    saved_ks = uow.kickstart.get()
    assert "catalog" in saved_ks.entity_schemas
    schema = saved_ks.entity_schemas["catalog"]
    assert schema.entity_name == "Pizza"
    assert len(schema.attributes) == 4

    # Verify fixture normalized
    fixtures = saved_ks.custom_fixtures.get("catalog", [])
    assert len(fixtures) == 1
    assert fixtures[0]["calories"] == 800
    assert fixtures[0]["ingredients"] == ["Tomato", "Mozzarella"]
