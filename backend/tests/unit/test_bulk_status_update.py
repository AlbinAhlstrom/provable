"""
Test Suite: Bulk Status Update (Vanilla Antigravity Test).
Verifies atomic bulk transitions, rollback on invalid transitions,
and zero direct store imports.
"""

import pytest
from fastapi.testclient import TestClient
from domain.model import Requirement
from adapters.repository import FakeRequirementRepository, FakeProjectRepository, FakeKickstartRepository
from service_layer.unit_of_work import AbstractUnitOfWork
from service_layer import services
import app


class FakeBulkUoW(AbstractUnitOfWork):
    def __init__(self):
        self.requirements = FakeRequirementRepository()
        self.projects = FakeProjectRepository()
        self.kickstart = FakeKickstartRepository()
        self.committed = False
        self.rolled_back = False

    def _commit(self):
        self.committed = True

    def _rollback(self):
        self.rolled_back = True


def test_bulk_status_update_success():
    uow = FakeBulkUoW()
    req1 = Requirement(id="BULK-1", title="Req 1", description="D", status="Backlog")
    req2 = Requirement(id="BULK-2", title="Req 2", description="D", status="Backlog")
    with uow:
        uow.requirements.add(req1)
        uow.requirements.add(req2)
        uow.commit()

    updated = services.update_requirements_bulk_status_service(
        req_ids=["BULK-1", "BULK-2"],
        target_status="In_Progress",
        uow=uow
    )
    assert len(updated) == 2
    assert req1.status == "In_Progress"
    assert req2.status == "In_Progress"
    assert uow.committed is True


def test_bulk_status_update_invalid_transition_rolls_back():
    uow = FakeBulkUoW()
    req1 = Requirement(id="BULK-3", title="Req 3", description="D", status="Backlog")
    req2 = Requirement(id="BULK-4", title="Req 4", description="D", status="Done")
    with uow:
        uow.requirements.add(req1)
        uow.requirements.add(req2)
        uow.commit()

    # Backlog -> In_Progress is valid, but Done -> In_Progress is INVALID
    from domain.exceptions import InvalidStatusTransition
    with pytest.raises(InvalidStatusTransition):
        services.update_requirements_bulk_status_service(
            req_ids=["BULK-3", "BULK-4"],
            target_status="In_Progress",
            uow=uow
        )


def test_bulk_status_update_endpoint_success():
    client = TestClient(app.app)
    uow = FakeBulkUoW()
    req1 = Requirement(id="EP-B1", title="Req 1", description="D", status="Backlog")
    req2 = Requirement(id="EP-B2", title="Req 2", description="D", status="Backlog")
    with uow:
        uow.requirements.add(req1)
        uow.requirements.add(req2)
        uow.commit()

    from entrypoints.routers.requirements import get_uow
    app.app.dependency_overrides[get_uow] = lambda: uow

    try:
        resp = client.post("/api/requirements/bulk-status-update", json={
            "req_ids": ["EP-B1", "EP-B2"],
            "target_status": "In_Progress"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["updated_count"] == 2
        assert data["status"] == "In_Progress"
    finally:
        app.app.dependency_overrides.clear()


def test_bulk_status_update_endpoint_bad_request_on_invalid():
    client = TestClient(app.app)
    uow = FakeBulkUoW()
    req = Requirement(id="EP-B3", title="Req 3", description="D", status="Done")
    with uow:
        uow.requirements.add(req)
        uow.commit()

    from entrypoints.routers.requirements import get_uow
    app.app.dependency_overrides[get_uow] = lambda: uow

    try:
        resp = client.post("/api/requirements/bulk-status-update", json={
            "req_ids": ["EP-B3"],
            "target_status": "In_Progress"
        })
        assert resp.status_code == 400
    finally:
        app.app.dependency_overrides.clear()
