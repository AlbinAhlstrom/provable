"""Status payloads report the retry policy: a first attempt plus at most one retry (.claude/rules/pipeline.md)."""
import agent_orchestrator
from domain.model import AgentRun


def test_agent_run_reports_one_retry():
    assert AgentRun(id="r").to_dict()["max_attempts"] == 2


def test_agent_status_reports_one_retry():
    assert agent_orchestrator.AGENT_STATUS["max_attempts"] == 2
