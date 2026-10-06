"""Every stage that designs behavior or UI after the intent step must see the intent, not only the decomposition."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import agent_orchestrator
from onboarding.intent import ProductIntent
from onboarding.router_engine import AttributeSpec, BusinessSpec, DomainStructureSchema, EntitySpec

INTENT = ProductIntent(
    product_type="public_website",
    audience="visitors",
    primary_goal="Present the business and let visitors get in touch",
    scope_summary="An informational site with an enquiry form",
    model_focus=["services", "enquiries"],
    out_of_scope=["staff back-office management", "payments"],
)
STRUCTURE = DomainStructureSchema(domain_name="Demo", entities=[EntitySpec(
    name="Enquiry", is_aggregate_root=True, attributes=[AttributeSpec(name="id", type="str", required=True)])])
SPEC = BusinessSpec(spec_id="S1", title="T", description="d", given_when_then="Given a When b Then c", target_aggregate="Enquiry")


def _capture(monkeypatch, reply):
    seen = []

    def fake(prompt, stage="general", **kwargs):
        seen.append((stage, prompt))
        return reply

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    for mod in ("onboarding.domain_engine_synthesizer", "onboarding.ux_planner", "onboarding.presentation_projection_synthesizer"):
        m = __import__(mod, fromlist=["call_gemini"])
        if hasattr(m, "call_gemini"):
            monkeypatch.setattr(m, "call_gemini", fake)
    return seen


def _assert_scoped(prompt):
    assert "public_website" in prompt
    assert "staff back-office management" in prompt and "payments" in prompt


def test_action_protocol_prompt_carries_the_intent(tmp_path, monkeypatch):
    """Verify the action protocol is designed within the product scope.

    id: TST-INTP-001
    Given: A public-website intent that rules out back-office management
    When: The action protocol is synthesized with that intent
    Then: The prompt states the scope and the exclusions
    """
    from onboarding.domain_engine_synthesizer import synthesize_action_protocol
    seen = _capture(monkeypatch, '{"action_manifest": {"actions": []}}')
    synthesize_action_protocol("p", STRUCTURE, [SPEC], str(tmp_path), intent=INTENT)
    _assert_scoped(seen[0][1])


def test_ux_planning_prompt_carries_the_intent(monkeypatch):
    """Verify the UX blueprint is planned within the product scope.

    id: TST-INTP-002
    Given: A public-website intent
    When: The UX blueprint is planned with it
    Then: The prompt states the scope and the exclusions
    """
    from onboarding.ux_planner import plan_ux_blueprint
    seen = _capture(monkeypatch, "blueprint " * 20)
    plan_ux_blueprint("p", STRUCTURE, {"actions": []}, "", "Enquiry", "enquiry", intent=INTENT)
    _assert_scoped(seen[0][1])


def test_presentation_prompt_carries_the_intent(tmp_path, monkeypatch):
    """Verify the UI is generated within the product scope.

    id: TST-INTP-003
    Given: A public-website intent
    When: The presentation projection is synthesized with it
    Then: The prompt states the scope and the exclusions
    """
    from onboarding.presentation_projection_synthesizer import synthesize_and_write_presentation_projection
    seen = _capture(monkeypatch, "{}")
    synthesize_and_write_presentation_projection(
        pitch="p", structure=STRUCTURE, inbox_specs=[SPEC], workspace_dir=str(tmp_path),
        action_manifest={"actions": []}, ux_blueprint="plan", intent=INTENT)
    presentation = [p for stage, p in seen if stage == "presentation_projection_synthesis"]
    assert presentation, "the presentation stage must have been called"
    _assert_scoped(presentation[0])


def test_ux_fallback_blueprint_does_not_assume_a_booking_product(monkeypatch):
    """Verify the UX fallback text does not inject one product type into every app.

    id: TST-INTP-004
    Given: The UX planning call fails
    When: The fallback blueprint is returned
    Then: It does not tell the UI to default to a booking workflow
    """
    from onboarding.ux_planner import plan_ux_blueprint
    _capture(monkeypatch, "")
    text = plan_ux_blueprint("p", STRUCTURE, None, "", "Enquiry", "enquiry", intent=INTENT).lower()
    assert "booking" not in text
