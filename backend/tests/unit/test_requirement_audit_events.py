"""
TDD Suite: Requirement Invariant Audit Events (Vanilla Antigravity Test).
Verifies that Requirement state transitions record domain events,
service layer exposes event history, and FastAPI router exposes GET /api/requirements/{req_id}/events.
"""

import pytest
from fastapi.testclient import TestClient
from domain.model import Requirement
from domain.events import RequirementStatusChanged
from adapters.repository import FakeRequirementRepository, FakeProjectRepository, FakeKickstartRepository
from service_layer.unit_of_work import AbstractUnitOfWork
from service_layer import services


class FakeAuditUoW(AbstractUnitOfWork):
    def __init__(self):
        self.requirements = FakeRequirementRepository()
        self.projects = FakeProjectRepository()
        self.kickstart = FakeKickstartRepository()
        self.committed = False

    def _commit(self):
        self.committed = True

    def _rollback(self):
        pass


def test_requirement_transition_records_domain_event():
    req = Requirement(id="REQ-001", title="Test Req", description="Desc", status="Backlog")
    assert len(req.events) == 0

    req.transition_to("In_Progress")
    assert req.status == "In_Progress"
    assert len(req.events) == 1

    event = req.events[0]
    assert isinstance(event, RequirementStatusChanged)
    assert event.req_id == "REQ-001"
    assert event.old_status == "Backlog"
    assert event.new_status == "In_Progress"


def test_get_requirement_events_service():
    uow = FakeAuditUoW()
    req = Requirement(id="REQ-AUDIT-1", title="Audit Test", description="Desc", status="Backlog")
    with uow:
        uow.requirements.add(req)
        uow.commit()

    req.transition_to("In_Progress")
    req.transition_to("Review")

    events_list = services.get_requirement_events_service("REQ-AUDIT-1", uow)
    assert len(events_list) == 2
    assert events_list[0]["event_type"] == "RequirementStatusChanged"
    assert events_list[0]["old_status"] == "Backlog"
    assert events_list[0]["new_status"] == "In_Progress"
    assert events_list[1]["new_status"] == "Review"


def test_get_requirement_events_endpoint(monkeypatch):
    import app
    client = TestClient(app.app)

    uow = FakeAuditUoW()
    req = Requirement(id="REQ-EP-1", title="Endpoint Req", description="Desc", status="Backlog")
    with uow:
        uow.requirements.add(req)
        uow.commit()

    req.transition_to("In_Progress")

    from entrypoints.routers.requirements import get_uow
    app.app.dependency_overrides[get_uow] = lambda: uow

    try:
        resp = client.get("/api/requirements/REQ-EP-1/events")
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data
        assert len(data["events"]) == 1
        assert data["events"][0]["new_status"] == "In_Progress"
    finally:
        app.app.dependency_overrides.clear()
