"""
Unit & Integration Tests for Onboarding Kickstart Engine & Aggregates Hydration.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from service_layer import services
from service_layer.unit_of_work import FakeUnitOfWork


def test_kickstart_domain_and_scaffold_service(tmp_path):
    uow = FakeUnitOfWork()
    pitch = "An industrial warehouse management system tracking Pallets, storage Zones, and forklift Operators."

    result = services.kickstart_domain_and_scaffold(
        pitch=pitch,
        uow=uow,
        workspace_dir=str(tmp_path)
    )

    assert result["success"] is True
    agg_names = [a.get("name") for a in result["aggregates"]]
    assert "Pallet" in agg_names
    assert "Zone" in agg_names
    assert "Operator" in agg_names
    assert len(result["created_files"]) > 0


def test_post_onboarding_kickstart_endpoint():
    client = TestClient(app)
    payload = {
        "pitch": "An industrial warehouse management system tracking Pallets, storage Zones, and forklift Operators."
    }
    res = client.post("/api/onboarding/kickstart", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    aggs = data.get("aggregates", [])
    names = [a.get("name") for a in aggs]
    assert "Pallet" in names


def test_get_onboarding_aggregates_endpoint():
    client = TestClient(app)
    res = client.get("/api/onboarding/aggregates")
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    assert len(data.get("aggregates", [])) >= 3
