import pytest
from fastapi.testclient import TestClient
from app import app
from service_layer.unit_of_work import FakeUnitOfWork
from domain.model import KickstartState
import service_layer.services as services

client = TestClient(app)

def test_add_and_get_inbox_spec_router(monkeypatch):
    fake_state = KickstartState()
    
    # Mock SqliteUnitOfWork in router to use FakeUnitOfWork
    class MockUoW(FakeUnitOfWork):
        def __init__(self):
            super().__init__()
            self.kickstart._state = fake_state

    monkeypatch.setattr("entrypoints.routers.specs.SqliteUnitOfWork", MockUoW)
    
    payload = {
        "title": "Temperature Control Zone Limit",
        "description": "Cold zones must stay between 2 and 6 degrees Celsius.",
        "given_when_then": "Given temp outside 2-6C When checking Then alert",
        "target_aggregate": "Zone",
        "is_mathematical_boundary": True
    }
    
    # 1. Add spec
    res = client.post("/api/specs/inbox/add", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["spec"]["title"] == payload["title"]
    
    # 2. Get inbox specs
    res_list = client.get("/api/specs/inbox")
    assert res_list.status_code == 200
    specs = res_list.json()
    assert len(specs) >= 1
    assert any(s["title"] == payload["title"] for s in specs)
