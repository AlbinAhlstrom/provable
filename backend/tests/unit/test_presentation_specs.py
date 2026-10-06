"""Presentation specs: declared by the spec itself, applied to the aggregate's view, proved by a frontend build."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest

import agent_orchestrator
from onboarding import presentation_specs as ps
from onboarding.router_engine import BusinessSpec, SpecKind

ORIGINAL = "export const EnquiryView = () => <div>old</div>;\n"
UPDATED = "export const EnquiryView = () => <div>new</div>;"
SPEC = {"spec_id": "S1", "title": "Show a confirmation", "given_when_then": "Given a sent enquiry When the page reloads Then it shows a confirmation",
        "target_aggregate": "Enquiry"}


@pytest.fixture
def workspace(tmp_path):
    views = tmp_path / "src" / "views"
    views.mkdir(parents=True)
    (views / "EnquiryView.tsx").write_text(ORIGINAL, encoding="utf-8")
    return tmp_path


def _llm(monkeypatch, replies):
    prompts = []

    def fake(prompt, stage="general", **kwargs):
        prompts.append(prompt)
        return replies[len(prompts) - 1]

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    return prompts


def _builds(monkeypatch, outcomes):
    calls = []

    def fake(ws, timeout=180):
        calls.append(ws)
        return outcomes[len(calls) - 1]

    monkeypatch.setattr(ps, "run_workspace_build", fake)
    return calls


def _view(workspace):
    return (workspace / "src" / "views" / "EnquiryView.tsx").read_text(encoding="utf-8")


def test_kind_is_declared_by_the_spec_not_guessed_from_words():
    """Verify routing follows the declared kind, never keywords in the text.

    id: TST-PSPEC-001
    Given: Specs whose text mentions "button", "display" and "light" but declare different kinds
    When: Their kind is read
    Then: Only the spec that declares presentation (or a VIEW rule card) is presentation
    """
    words = {"title": "Display a button in light mode", "given_when_then": "Given a b When c Then display a button"}
    assert ps.spec_kind({**words, "kind": "behavior"}) is SpecKind.BEHAVIOR
    assert ps.spec_kind(words) is SpecKind.BEHAVIOR
    assert ps.spec_kind({**words, "kind": "presentation"}) is SpecKind.PRESENTATION
    assert ps.spec_kind({**words, "card_type": "VIEW"}) is SpecKind.PRESENTATION
    assert BusinessSpec(spec_id="s", title="t", description="d", given_when_then="g", target_aggregate="A").kind == "behavior"


def test_view_that_builds_is_fulfilled(workspace, monkeypatch):
    """Verify a view change is FULFILLED only after the frontend build passes.

    id: TST-PSPEC-002
    Given: An LLM answer that replaces the aggregate's view and a passing build
    When: The presentation spec is executed
    Then: The view is rewritten, the build ran once and the status is FULFILLED
    """
    _llm(monkeypatch, [f"```tsx\n{UPDATED}\n```"])
    builds = _builds(monkeypatch, [{"ok": True, "output": ""}])
    result = ps.execute_presentation_spec(SPEC, str(workspace))
    assert result["status"] == "FULFILLED" and result["success"] is True
    assert "new" in _view(workspace) and len(builds) == 1
    assert [a["approved"] for a in result["attempts"]] == [True]


def test_build_failure_is_fed_back_once_then_rolled_back(workspace, monkeypatch):
    """Verify a failing build gets exactly one feedback retry and the original view is restored.

    id: TST-PSPEC-003
    Given: Two LLM answers that both fail the build
    When: The presentation spec is executed
    Then: The second prompt carries the build error, no third attempt is made, the original view is restored
    """
    prompts = _llm(monkeypatch, [f"```tsx\n{UPDATED}\n```", f"```tsx\n{UPDATED}\n```", f"```tsx\n{UPDATED}\n```"])
    _builds(monkeypatch, [{"ok": False, "output": "error TS2304: boom"}] * 3)
    result = ps.execute_presentation_spec(SPEC, str(workspace))
    assert result["status"] == "REQUIRES_HUMAN_INTERVENTION" and result["rolled_back"] is True
    assert len(prompts) == 2 and "error TS2304: boom" in prompts[1] and "boom" not in prompts[0]
    assert _view(workspace) == ORIGINAL
    assert len(result["attempts"]) == 2


def test_retry_succeeds_after_feedback(workspace, monkeypatch):
    """Verify the single feedback retry can fix a build error.

    id: TST-PSPEC-004
    Given: A first answer that fails the build and a second that passes
    When: The presentation spec is executed
    Then: The status is FULFILLED with two recorded attempts
    """
    _llm(monkeypatch, ["```tsx\nexport const A = () => <div>;\n```", f"```tsx\n{UPDATED}\n```"])
    _builds(monkeypatch, [{"ok": False, "output": "syntax error"}, {"ok": True, "output": ""}])
    result = ps.execute_presentation_spec(SPEC, str(workspace))
    assert result["status"] == "FULFILLED"
    assert [a["approved"] for a in result["attempts"]] == [False, True]


def test_provider_and_parse_errors_are_not_retried(workspace, monkeypatch):
    """Verify non-verdict failures fail loudly after one attempt (rule 03 section 4).

    id: TST-PSPEC-005
    Given: An empty LLM answer, then an answer with no code
    When: The presentation spec is executed
    Then: Each ends after one attempt, the build never runs and the view is untouched
    """
    for reply in ("", "I changed the view for you."):
        prompts = _llm(monkeypatch, [reply, reply])
        builds = _builds(monkeypatch, [])
        result = ps.execute_presentation_spec(SPEC, str(workspace))
        assert result["status"] == "REQUIRES_HUMAN_INTERVENTION" and len(prompts) == 1 and not builds
        assert _view(workspace) == ORIGINAL


def test_missing_view_fails_loudly_instead_of_guessing_another_file(tmp_path, monkeypatch):
    """Verify a spec for an aggregate without a view is not applied to some other view.

    id: TST-PSPEC-006
    Given: A workspace whose only view belongs to a different aggregate
    When: A presentation spec for Enquiry is executed
    Then: It reports the missing view and calls neither the LLM nor the build
    """
    views = tmp_path / "src" / "views"
    views.mkdir(parents=True)
    (views / "OtherView.tsx").write_text(ORIGINAL, encoding="utf-8")
    prompts = _llm(monkeypatch, [])
    builds = _builds(monkeypatch, [])
    result = ps.execute_presentation_spec(SPEC, str(tmp_path))
    assert result["status"] == "REQUIRES_HUMAN_INTERVENTION" and "EnquiryView.tsx" in result["error"]
    assert not prompts and not builds
    assert (views / "OtherView.tsx").read_text(encoding="utf-8") == ORIGINAL


def test_service_routes_a_presentation_spec_away_from_the_tdd_loop(workspace, monkeypatch):
    """Verify the inbox executes presentation specs through the build-verified path and stores the summary.

    id: TST-PSPEC-007
    Given: A presentation spec in the inbox and a TDD loop that must not run
    When: execute_inbox_spec_tdd is called
    Then: The view path runs, the spec status is stored with a Studio-readable attempt summary, and the TDD loop is untouched
    """
    from service_layer import services
    from service_layer.unit_of_work import FakeUnitOfWork
    uow = FakeUnitOfWork()
    services.add_inbox_spec({**SPEC, "kind": "presentation", "status": "PENDING"}, uow=uow)
    _llm(monkeypatch, [f"```tsx\n{UPDATED}\n```"])
    _builds(monkeypatch, [{"ok": True, "output": ""}])
    monkeypatch.setattr("service_layer.tdd_machine.execute_spec_tdd_loop",
                        lambda *a, **k: pytest.fail("a presentation spec must not enter the TDD loop"))
    result = services.execute_inbox_spec_tdd("S1", uow=uow, workspace_dir=str(workspace))
    stored = next(s for s in services.get_inbox_specs(uow=uow) if s["spec_id"] == "S1")
    assert result["status"] == stored["status"] == "FULFILLED"
    assert stored["tdd"]["phase"] == "presentation" and stored["tdd"]["attempts"][0]["approved"] is True
