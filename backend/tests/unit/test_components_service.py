"""
Unit tests for Component service workflows using FakeUnitOfWork.
Tests dynamic component addition, component deletion, sub-requirement addition, sub-requirement deletion, and component suggestion fetching.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import Requirement, Component
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_add_dynamic_component_service():
    """
    Given a FakeUnitOfWork and a prompt for a component ('catalog')
    When calling services.add_dynamic_component
    Then a Component requirement is saved in repository and UoW is committed.
    """
    uow = FakeUnitOfWork()

    result = services.add_dynamic_component(
        prompt="catalog",
        uow=uow,
        generate_files=False
    )

    assert result["success"] is True
    assert result["canonical_key"] == "catalog"
    assert result["component_type"] == "premade"
    assert result["req_id"] == "REQ-CMP-CATALOG-001"
    assert result["prompt"] == "catalog"

    req = uow.requirements.get("REQ-CMP-CATALOG-001")
    assert req is not None
    assert req.status == "Done"
    assert uow.committed is True


def test_delete_dynamic_component_service():
    """
    Given a FakeUnitOfWork with existing component requirements
    When calling services.delete_dynamic_component for 'cart'
    Then component requirement and related feature requirements are deleted from repository and UoW is committed.
    """
    cmp_req = Requirement(id="REQ-CMP-CART-001", title="Dynamic Component: Cart", description="Cart component")
    feat_req = Requirement(id="REQ-CART-001", title="Cart Feature", description="Cart feature")
    uow = FakeUnitOfWork(initial_requirements=[cmp_req, feat_req])

    result = services.delete_dynamic_component(
        canonical_key="cart",
        uow=uow,
        generate_files=False
    )

    assert result["success"] is True
    assert result["canonical_key"] == "cart"
    assert uow.requirements.get("REQ-CMP-CART-001") is None
    assert uow.requirements.get("REQ-CART-001") is None
    assert uow.committed is True


def test_add_sub_requirement_service():
    """
    Given a FakeUnitOfWork with parent requirement 'REQ-CATALOG-001'
    When calling services.add_sub_requirement
    Then a sub-requirement is created with parent_id set and saved to repository, and UoW is committed.
    """
    parent = Requirement(id="REQ-CATALOG-001", title="Catalog Main", description="Catalog")
    uow = FakeUnitOfWork(initial_requirements=[parent])

    result = services.add_sub_requirement(
        parent_canonical_key="catalog",
        prompt="Filter by Price",
        uow=uow,
        generate_files=False
    )

    assert result["success"] is True
    assert result["parent_canonical_key"] == "catalog"
    assert result["prompt"] == "Filter by Price"
    sub_id = result["sub_id"]
    assert sub_id.startswith("REQ-SUB-")

    sub_req = uow.requirements.get(sub_id)
    assert sub_req is not None
    assert sub_req.parent_id == "REQ-CATALOG-001"
    assert "Filter by Price" in sub_req.title
    assert uow.committed is True


def test_delete_sub_requirement_service():
    """
    Given a FakeUnitOfWork with sub-requirement 'REQ-SUB-123'
    When calling services.delete_sub_requirement
    Then sub-requirement is deleted from repository and UoW is committed.
    """
    sub_req = Requirement(id="REQ-SUB-123", title="Sub req", description="Sub desc", parent_id="REQ-CATALOG-001")
    uow = FakeUnitOfWork(initial_requirements=[sub_req])

    result = services.delete_sub_requirement(
        sub_id="REQ-SUB-123",
        parent_canonical_key="catalog",
        uow=uow,
        generate_files=False
    )

    assert result["success"] is True
    assert result["sub_id"] == "REQ-SUB-123"
    assert uow.requirements.get("REQ-SUB-123") is None
    assert uow.committed is True


def test_get_component_suggestions_service():
    """
    Given a FakeUnitOfWork
    When calling services.get_component_suggestions
    Then a list of domain component suggestions is returned.
    """
    uow = FakeUnitOfWork()

    result = services.get_component_suggestions(uow=uow)

    assert result["success"] is True
    assert isinstance(result["suggestions"], list)
    assert len(result["suggestions"]) > 0
