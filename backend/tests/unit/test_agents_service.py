"""
Unit tests for Agent service workflows and AgentRun domain model using FakeUnitOfWork.
Tests agent status fetching, agent loop triggering, ticket reset operations, and log retrieval.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import Requirement, AgentRun
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_agent_run_domain_entity():
    """
    Given a list of Backlog requirements
    When calling AgentRun.analyze_backlog
    Then it correctly prioritizes the top ticket and constructs reasoning.
    """
    req1 = Requirement(id="REQ-001", title="Feature Alpha", description="Alpha description", status="Backlog")
    analysis = AgentRun.analyze_backlog([req1])

    assert analysis["ticket"] == "REQ-001"
    assert analysis["title"] == "Feature Alpha"
    assert "REQ-001" in analysis["reasoning"]

    empty_analysis = AgentRun.analyze_backlog([])
    assert empty_analysis["ticket"] is None
    assert empty_analysis["title"] is None
    assert "No active tasks" in empty_analysis["reasoning"]


def test_get_agent_status_service():
    """
    Given a FakeUnitOfWork with a Backlog requirement
    When calling services.get_agent_status
    Then return agent status and backlog analysis prioritizing the requirement.
    """
    req = Requirement(id="REQ-101", title="Implement Login", description="Login description", status="Backlog")
    uow = FakeUnitOfWork(initial_requirements=[req])

    result = services.get_agent_status(uow=uow)

    assert "status" in result
    assert result["backlog_analysis"] is not None
    assert result["backlog_analysis"]["ticket"] == "REQ-101"
    assert result["backlog_analysis"]["title"] == "Implement Login"


def test_get_agent_status_empty_backlog():
    """
    Given a FakeUnitOfWork with no Backlog requirements
    When calling services.get_agent_status
    Then backlog analysis indicates idling.
    """
    uow = FakeUnitOfWork()

    result = services.get_agent_status(uow=uow)

    assert "status" in result
    assert result["backlog_analysis"]["ticket"] is None
    assert "idling" in result["backlog_analysis"]["action"].lower()


def test_trigger_agents_service():
    """
    Given a FakeUnitOfWork and a mock BackgroundTasks
    When calling services.trigger_agents
    Then background_tasks gets a task added and clean message returned.
    """
    uow = FakeUnitOfWork()
    bg_tasks = MagicMock()

    result = services.trigger_agents(uow=uow, background_tasks=bg_tasks)

    assert result["message"] == "Agent loop triggered"
    bg_tasks.add_task.assert_called_once()


def test_trigger_ticket_service():
    """
    Given a FakeUnitOfWork and ticket_id
    When calling services.trigger_ticket
    Then background_tasks gets run_openhands_loop added for ticket_id.
    """
    uow = FakeUnitOfWork()
    bg_tasks = MagicMock()

    result = services.trigger_ticket(ticket_id="REQ-202", uow=uow, background_tasks=bg_tasks)

    assert result["message"] == "Agent loop triggered for ticket REQ-202"
    bg_tasks.add_task.assert_called_once()


def test_abandon_ticket_service():
    """
    Given a FakeUnitOfWork with a requirement in In_Progress with assigned agents
    When calling services.abandon_ticket
    Then ticket is reset to Backlog, assigned agents emptied, and UoW committed.
    """
    req = Requirement(id="REQ-303", title="Bug Fix", description="Fix bug desc", status="In_Progress", assigned_agents=["Agent1"])
    uow = FakeUnitOfWork(initial_requirements=[req])

    result = services.abandon_ticket(ticket_id="REQ-303", uow=uow)

    assert result["message"] == "Ticket REQ-303 reset to Backlog"
    updated_req = uow.requirements.get("REQ-303")
    assert updated_req.status == "Backlog"
    assert updated_req.assigned_agents == []
    assert uow.committed is True



def test_get_agent_logs_service(tmp_path):
    """
    Given a temporary log file directory
    When calling services.get_agent_logs
    Then returns log contents if file exists, or clean fallback message if missing.
    """
    uow = FakeUnitOfWork()
    log_file = tmp_path / "REQ-404.log"
    log_file.write_text("Execution step 1: test passing.", encoding="utf-8")

    # Test file exists
    logs_result = services.get_agent_logs(ticket_id="REQ-404", uow=uow, log_dir=str(tmp_path))
    assert logs_result["logs"] == "Execution step 1: test passing."

    # Test file missing
    missing_result = services.get_agent_logs(ticket_id="REQ-999", uow=uow, log_dir=str(tmp_path))
    assert "Log file for ticket REQ-999 not found." in missing_result["logs"]
