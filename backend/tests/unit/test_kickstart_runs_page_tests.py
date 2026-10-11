"""A kickstart that built a page has every rule's page test run once it has answered (ADR-010).

The lights of a new app were all grey until someone pressed Run, though the kickstart had just reported it done.
Writing and running the tests takes minutes and money, so the answer does not wait for them: they start when the
kickstart has answered, and each light is stored as its test finishes.
"""
import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def _kickstart(monkeypatch, result):
    """Posts a kickstart whose pipeline answers `result`; returns the labels of the rule test runs it started."""
    started = []
    monkeypatch.setattr("entrypoints.routers.onboarding.services.kickstart_domain_and_scaffold", lambda **_: result)
    monkeypatch.setattr("entrypoints.routers.onboarding.rule_tests.run_all_rule_tests",
                        lambda uow, label="deck": started.append(label))
    assert client.post("/api/onboarding/kickstart", json={"pitch": "A booking page"}).json() == result
    return started


@pytest.mark.slow
def test_a_kickstart_that_built_a_page_has_its_rules_tested_after_it_answers(monkeypatch):
    """Verify the page tests of a new app are started by the kickstart itself.

    id: TST-KICKSTART-LIGHTS-001
    Given: A kickstart that built a page (it carries a QA verdict)
    When: It answers
    Then: One run of every rule's page test is started, labelled as following the kickstart
    """
    assert _kickstart(monkeypatch, {"success": True, "qa": {"verdict": "passed"}}) == ["after kickstart"]


@pytest.mark.slow
def test_a_kickstart_without_a_page_has_nothing_to_test(monkeypatch):
    """Verify no page tests are started when there is no page to test.

    id: TST-KICKSTART-LIGHTS-002
    Given: A kickstart that failed, and one that built no page (offline or mock mode: no QA verdict)
    When: Each answers
    Then: No rule test run is started
    """
    assert _kickstart(monkeypatch, {"success": False, "error": "no key"}) == []
    assert _kickstart(monkeypatch, {"success": True, "qa": None}) == []
