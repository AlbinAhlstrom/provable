"""
Unit Tests for Provable Hybrid Autonomous Engine.
Tests ExecutionRouter, OpenCodeGateway, AiderBridge, capability detection,
and graceful native fallback mechanics.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from onboarding.wayfinder import BddClause
from service_layer.opencode_gateway import OpenCodeGateway
from service_layer.aider_bridge import ProvableAiderBridge
from service_layer.execution_router import ExecutionRouter, TaskIntent


def test_system_capabilities_detection():
    router = ExecutionRouter()
    caps = router.get_system_capabilities()

    assert "native_scaffold_ready" in caps
    assert caps["native_scaffold_ready"] is True
    assert "opencode_connected" in caps
    assert "aider_available" in caps
    assert "active_greenfield_engine" in caps
    assert "active_precision_engine" in caps


def test_opencode_gateway_health_check_offline():
    # Points to non-existent port to simulate offline daemon
    gateway = OpenCodeGateway(server_url="http://127.0.0.1:49999")
    assert gateway.is_available() is False


def test_opencode_gateway_session_mocked_lifecycle():
    gateway = OpenCodeGateway(server_url="http://localhost:4096")

    # Mock HTTP session creation and prompt dispatch
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"version": "0.1.0"}

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "session-123", "status": "completed"}

        assert gateway.is_available() is True
        session_id = gateway.create_session(workspace_path="/tmp/test", title="Chess App")
        assert session_id == "session-123"

        result = gateway.send_prompt(session_id="session-123", prompt="Build a chess board")
        assert result.get("status") == "completed"


def test_aider_bridge_prompt_formatting():
    bridge = ProvableAiderBridge()
    bdd = BddClause(
        given="Active chess match",
        when="Player requests undo move",
        then="Revert last two half-moves and restore clock",
        unless="Move history is empty"
    )

    prompt = bridge.format_bdd_implementation_prompt(
        bdd_clause=bdd,
        test_code="def test_undo(): assert True"
    )

    assert "GIVEN Active chess match" in prompt
    assert "WHEN Player requests undo move" in prompt
    assert "THEN Revert last two half-moves and restore clock" in prompt
    assert "UNLESS Move history is empty" in prompt
    assert "def test_undo(): assert True" in prompt


def test_aider_bridge_fallback_when_uninstalled():
    bridge = ProvableAiderBridge()
    with patch("service_layer.aider_bridge.HAVE_AIDER", False):
        res = bridge.apply_bdd_patch(
            workspace_path="/tmp/mock_ws",
            target_files=["domain/model.py"],
            bdd_clause=BddClause("given", "when", "then"),
            test_code="def test_x(): pass"
        )
        # Should fallback gracefully without raising an unhandled exception
        assert res["success"] is False
        assert "Aider is not installed" in res["error"]


def test_execution_router_dispatches_greenfield_with_fallback():
    router = ExecutionRouter()
    # When OpenCode is offline, router must fallback to Native Scaffold + Internal Synthesis
    with patch.object(OpenCodeGateway, "is_available", return_value=False):
        plan = router.route_task(
            intent=TaskIntent.GREENFIELD_ONE_SHOT,
            prompt="Build a real-time Chess platform"
        )
        assert plan["engine"] == "NATIVE_SCAFFOLD"
        assert plan["status"] == "READY_FOR_SYNTHESIS"


def test_execution_router_dispatches_greenfield_to_opencode_when_online():
    router = ExecutionRouter()
    with patch.object(OpenCodeGateway, "is_available", return_value=True):
        plan = router.route_task(
            intent=TaskIntent.GREENFIELD_ONE_SHOT,
            prompt="Build a real-time Chess platform"
        )
        assert plan["engine"] == "OPENCODE_GATEWAY"


def test_wayfinder_capabilities_api():
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    res = client.get("/api/system/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert "native_scaffold_ready" in data
    assert data["native_scaffold_ready"] is True
    assert "opencode_connected" in data
    assert "aider_available" in data
