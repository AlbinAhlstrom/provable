"""
Unit tests for Presentation Projection Synthesizer and Resilient Entrypoints.
Verifies fallback templates adhere to Viewport Containment and resilient module imports.
"""

import pytest
from onboarding.skeleton_builder import generate_frontend_main_tsx


def test_resilient_main_tsx_entrypoint_handles_any_export_pattern():
    """Verifies that main.tsx handles both default and named export without requiring monkey patches."""
    main_tsx = generate_frontend_main_tsx()
    assert "* as AppModule" in main_tsx
    assert "(AppModule as any).default || (AppModule as any).App" in main_tsx



def _structure():
    from onboarding.router_engine import DomainStructureSchema
    return DomainStructureSchema.model_validate({"domain_name": "Care", "entities": [
        {"name": "Inquiry", "is_aggregate_root": True, "attributes": [{"name": "id", "type": "string"}]}]}) \
        if hasattr(DomainStructureSchema, "model_validate") else DomainStructureSchema(
            domain_name="Care", entities=[{"name": "Inquiry", "is_aggregate_root": True,
                                           "attributes": [{"name": "id", "type": "string"}]}])


@pytest.mark.parametrize("answer, llm_error, expected", [
    ("", "RateLimitError: quota exceeded", "quota exceeded"),
    ("", None, "empty response"),
    ("this is not json", None, "no <<<section>>> markers"),
])
def test_a_failed_presentation_stage_reports_why(monkeypatch, tmp_path, answer, llm_error, expected):
    """Verify every failure path returns the reason, so the run summary can state the cause.

    id: TST-PPS-REASON
    Given: The model returns nothing, an error, or text that is not JSON
    When: The presentation projection is synthesized
    Then: success is False and error names the provider error, the empty answer or the bad JSON
    """
    import agent_orchestrator
    from onboarding import presentation_projection_synthesizer as synth

    def fake_llm(prompt, stage="general", **kwargs):
        agent_orchestrator.LAST_LLM_ERROR = llm_error
        return answer

    monkeypatch.setattr(synth, "call_gemini", fake_llm)
    result = synth.synthesize_and_write_presentation_projection(
        pitch="p", structure=_structure(), inbox_specs=[], workspace_dir=str(tmp_path), ux_blueprint="plan")
    assert result["success"] is False and expected in result["error"]


def _page_prompt(monkeypatch, tmp_path, master):
    from onboarding import presentation_projection_synthesizer as synth
    from onboarding.router_engine import DomainStructureSchema
    structure = DomainStructureSchema(domain_name="Product", entities=[
        {"name": master, "is_aggregate_root": True, "attributes": [{"name": "id", "type": "string"}]}])
    prompts = []
    monkeypatch.setattr(synth, "call_gemini", lambda prompt, stage="general", **kwargs: prompts.append(prompt) or "")
    synth.synthesize_and_write_presentation_projection(
        pitch="p", structure=structure, inbox_specs=[], workspace_dir=str(tmp_path), ux_blueprint="plan")
    return prompts[0]


@pytest.mark.parametrize("master, route", [("Match", "/api/matches"), ("Inquiry", "/api/inquiries"), ("Order", "/api/orders")])
def test_the_page_is_told_the_routes_the_backend_really_serves(monkeypatch, tmp_path, master, route):
    """Verify the endpoint list uses the plural the skeleton's router is mounted on, not the name plus an "s".

    id: TST-PPS-ROUTES
    Given: A master whose plural is irregular for a plain "s" (a name ending in "ch" or "y"), and a regular one
    When: The page-writer prompt is built
    Then: Every endpoint line names the served route
    """
    prompt = _page_prompt(monkeypatch, tmp_path, master)
    for line in (f"`GET {route}`", f"`POST {route}`", f"`GET {route}/{{id}}`", f"`POST {route}/{{id}}/action`"):
        assert line in prompt


def test_the_page_is_told_which_record_it_opens_on(monkeypatch, tmp_path):
    """Verify a page that works on one record at a time opens the newest: a page that opened the first record of the
    list showed, after a reload, the record the visitor had replaced.

    id: TST-PPS-CURRENT-RECORD
    Given: The page-writer prompt
    When: It is read
    Then: It states the order of a list and that the record being worked on is the most recently created one
    """
    prompt = _page_prompt(monkeypatch, tmp_path, "Inquiry")
    assert "in the order they were created" in prompt
    assert "most recently created" in prompt


def test_a_control_is_offered_while_its_action_is_allowed(monkeypatch, tmp_path):
    """Verify the action protocol decides when a control appears: the plan is made beside the protocol and cannot see
    when an action is allowed, and a page that followed the plan offered an action the backend refuses.

    id: TST-PPS-ALLOWED
    Given: The page-writer prompt
    When: It is read
    Then: It says a control is offered while its action's description allows it, and that the description decides over the blueprint
    """
    prompt = _page_prompt(monkeypatch, tmp_path, "Inquiry")
    assert "offered while that holds for the record on screen" in prompt
    assert "the description decides" in prompt
