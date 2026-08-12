"""
Unit tests for MessageBus and Domain Event dispatching.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import Requirement, Component
from domain.events import (
    RequirementCreated, ComponentAdded, ComponentDeleted, RequirementEdited
)
from adapters.workspace import FakeWorkspaceAdapter
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import messagebus, services

def test_requirement_created_event_collection_and_dispatch():
    uow = FakeUnitOfWork()
    workspace = FakeWorkspaceAdapter()

    req = services.create_requirement(
        req_id="REQ-TEST-101",
        title="Test Requirement",
        description="Testing event collection",
        uow=uow,
        workspace=workspace
    )

    assert req.id == "REQ-TEST-101"
    assert workspace.sdoc_synced is True

def test_component_added_event_dispatch():
    uow = FakeUnitOfWork()
    workspace = FakeWorkspaceAdapter()

    comp_event = ComponentAdded(canonical_key="cart", prompt="add shopping cart", req_id="REQ-CMP-CART-001")
    messagebus.handle(comp_event, uow=uow, workspace=workspace)

    assert workspace.sdoc_synced is True
    assert workspace.app_shell_synced is True

def test_component_deleted_event_dispatch():
    uow = FakeUnitOfWork()
    workspace = FakeWorkspaceAdapter()

    del_event = ComponentDeleted(canonical_key="cart")
    messagebus.handle(del_event, uow=uow, workspace=workspace)

    assert workspace.sdoc_synced is True
    assert workspace.app_shell_synced is True

def test_requirement_edited_event_collection_and_dispatch():
    uow = FakeUnitOfWork(initial_requirements=[
        Requirement(id="REQ-001", title="Old Title", description="Old Desc")
    ])
    workspace = FakeWorkspaceAdapter()

    edited_req = services.edit_requirement(
        req_id="REQ-001",
        title="New Title",
        description="New Desc",
        priority="High",
        uow=uow,
        workspace=workspace
    )

    assert edited_req.title == "New Title"
    assert workspace.sdoc_synced is True
    assert workspace.app_shell_synced is True
