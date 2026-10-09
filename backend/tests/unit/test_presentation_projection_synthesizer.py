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
