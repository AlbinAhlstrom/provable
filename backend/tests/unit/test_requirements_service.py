"""
Unit tests for Requirements service workflows using FakeUnitOfWork.
Tests requirement deletion, move, edit, update_param, create folder, bulk update, and feature toggle.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import Requirement
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services, exceptions


def test_delete_requirement_service():
    """
    Given a FakeUnitOfWork containing a parent requirement and child requirement
    When calling delete_requirement for parent_id
    Then parent and child requirements are deleted from FakeRepository and UoW is committed.
    """
    parent = Requirement(id="REQ-101", title="Parent Req", description="Parent Desc")
    child = Requirement(id="REQ-102", title="Child Req", description="Child Desc", parent_id="REQ-101")
    uow = FakeUnitOfWork(initial_requirements=[parent, child])

    services.delete_requirement(req_id="REQ-101", uow=uow)

    assert uow.requirements.get("REQ-101") is None
    assert uow.requirements.get("REQ-102") is None
    assert uow.committed is True


def test_move_requirement_service():
    """
    Given a FakeUnitOfWork containing a requirement
    When calling move_requirement with new parent_id
    Then parent_id is updated and UoW is committed.
    """
    req = Requirement(id="REQ-201", title="Req to move", description="Desc")
    uow = FakeUnitOfWork(initial_requirements=[req])

    updated = services.move_requirement(req_id="REQ-201", parent_id="FLD-999", uow=uow)

    assert updated.parent_id == "FLD-999"
    saved = uow.requirements.get("REQ-201")
    assert saved is not None
    assert saved.parent_id == "FLD-999"
    assert uow.committed is True


def test_edit_requirement_service():
    """
    Given a FakeUnitOfWork containing a requirement
    When calling edit_requirement with updated title, description, and priority
    Then requirement fields are updated and UoW is committed.
    """
    req = Requirement(id="REQ-301", title="Old Title", description="Old Desc", priority="Low")
    uow = FakeUnitOfWork(initial_requirements=[req])

    updated = services.edit_requirement(
        req_id="REQ-301",
        title="New Title",
        description="New Desc",
        priority="High",
        uow=uow
    )

    assert updated.title == "New Title"
    assert updated.description == "New Desc"
    assert updated.priority == "High"
    saved = uow.requirements.get("REQ-301")
    assert saved.title == "New Title"
    assert uow.committed is True


def test_update_requirement_param_service():
    """
    Given a brand_title param key and value
    When calling update_requirement_param service workflow
    Then param requirement is created in repository with status 'Done' and linked test case.
    """
    uow = FakeUnitOfWork()

    result = services.update_requirement_param(
        param_key="brand_title",
        value="Acme Storefront",
        ws_base="/tmp/fake_ws",
        generate_files=False,
        uow=uow
    )

    assert result["success"] is True
    assert result["param_key"] == "brand_title"
    assert result["value"] == "Acme Storefront"

    req = uow.requirements.get("REQ-BRAND-001")
    assert req is not None
    assert req.status == "Done"
    assert len(req.tests) == 1
    assert req.tests[0]["name"] == "test_storefront_brand_title_configured"
    assert uow.committed is True


def test_create_folder_service():
    """
    Given title, description, and parent_id
    When calling create_folder service workflow
    Then a Folder requirement is created and UoW is committed.
    """
    uow = FakeUnitOfWork()

    folder = services.create_folder(
        title="Architecture",
        description="Core architecture docs",
        parent_id="FLD-ROOT",
        uow=uow
    )

    assert folder.type == "Folder"
    assert folder.title == "Architecture"
    assert folder.parent_id == "FLD-ROOT"
    assert uow.requirements.get(folder.id) is not None
    assert uow.committed is True


def test_update_requirements_bulk_service():
    """
    Given a list of requirement dicts/entities
    When calling update_requirements
    Then requirements are updated/added in FakeRepository and UoW is committed.
    """
    r1 = Requirement(id="REQ-401", title="Req 1", description="Desc 1")
    uow = FakeUnitOfWork(initial_requirements=[r1])

    services.update_requirements(
        reqs=[
            {"id": "REQ-401", "title": "Updated Req 1", "description": "Desc 1", "status": "In_Progress", "priority": "High"},
            {"id": "REQ-402", "title": "Req 2", "description": "Desc 2", "status": "Backlog", "priority": "Med"}
        ],
        uow=uow
    )

    r1_saved = uow.requirements.get("REQ-401")
    r2_saved = uow.requirements.get("REQ-402")
    assert r1_saved.title == "Updated Req 1"
    assert r1_saved.status == "In_Progress"
    assert r2_saved is not None
    assert r2_saved.title == "Req 2"
    assert uow.committed is True
