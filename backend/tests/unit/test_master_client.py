"""The master aggregate's API client is generated from the entity (never by the LLM) and matches the skeleton router."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import agent_orchestrator
from onboarding.router_engine import AttributeSpec, BusinessSpec, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import generate_master_client, generate_router_module

ENTITY = EntitySpec(name="CareInquiry", is_aggregate_root=True, attributes=[
    AttributeSpec(name="id", type="str", required=True), AttributeSpec(name="parent_email", type="str", required=False),
    AttributeSpec(name="hours", type="int", required=True)])
STRUCTURE = DomainStructureSchema(domain_name="Demo", entities=[ENTITY])
SPEC = BusinessSpec(spec_id="S1", title="T", description="d", given_when_then="Given a When b Then c", target_aggregate="CareInquiry")


def test_client_matches_the_router_and_invents_nothing():
    """Verify the client calls exactly the routes the router serves and never fabricates data.

    id: TST-CLI-001
    Given: A master aggregate
    When: Its client and router are generated
    Then: The client uses the router's plural prefix, has list/get/create/action, no "default" id and no fallback record
    """
    client, router = generate_master_client(ENTITY), generate_router_module(ENTITY)
    assert "/api/care_inquiries" in client and 'prefix="/api/care_inquiries"' in router
    for name in ("listCareInquiry", "getCareInquiry", "createCareInquiry", "sendAction", "CareInquiryState"):
        assert name in client
    assert "hours: number;" in client and "parent_email?: string;" in client
    assert "default" not in client.replace("export default", "") and "catch (err" not in client
    assert "/action" in client


def test_presentation_stage_writes_the_deterministic_client_and_ignores_a_model_client(tmp_path, monkeypatch):
    """Verify a client in the model's answer is not written; the generated one is.

    id: TST-CLI-002
    Given: A presentation answer that includes its own client_ts with a fabricated fallback
    When: The projection is synthesized
    Then: src/api/<slug>Client.ts is the generated client
    """
    from onboarding import presentation_projection_synthesizer as pps
    answer = '{"client_ts": "FABRICATED", "view_tsx": "export const V = 1", "controls_tsx": "export const C = 1", "history_tsx": "export const H = 1", "app_tsx": "import {CareInquiryView} from \'./views/CareInquiryView\'; export const App = 1"}'
    monkeypatch.setattr(pps, "call_gemini", lambda prompt, stage="general", **k: answer)
    result = pps.synthesize_and_write_presentation_projection(
        pitch="p", structure=STRUCTURE, inbox_specs=[SPEC], workspace_dir=str(tmp_path), action_manifest={"actions": []}, ux_blueprint="plan")
    assert result["success"] is True
    written = (tmp_path / "src" / "api" / "care_inquiryClient.ts").read_text(encoding="utf-8")
    assert "FABRICATED" not in written and "listCareInquiry" in written


def test_app_that_does_not_wire_the_master_view_fails_loudly(tmp_path, monkeypatch):
    """Verify no substitute App shell is invented when the model's App is unusable.

    id: TST-CLI-003
    Given: An answer whose App does not import the master view
    When: The projection is synthesized
    Then: The stage reports failure with the reason and writes no files
    """
    from onboarding import presentation_projection_synthesizer as pps
    answer = '{"view_tsx": "export const V = 1", "app_tsx": "export const App = 1"}'
    monkeypatch.setattr(pps, "call_gemini", lambda prompt, stage="general", **k: answer)
    result = pps.synthesize_and_write_presentation_projection(
        pitch="p", structure=STRUCTURE, inbox_specs=[SPEC], workspace_dir=str(tmp_path), action_manifest={"actions": []}, ux_blueprint="plan")
    assert result["success"] is False and "master view" in result["error"] and result["files"] == []
    assert not (tmp_path / "src" / "App.tsx").exists()


def test_presentation_prompt_states_the_real_api():
    """Verify the prompt no longer promises a default record, a reset route or a model-written client.

    id: TST-CLI-004
    Given: The presentation prompt
    When: It is read
    Then: It says there is no default record and no reset endpoint, and does not ask for client_ts
    """
    path = os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts", "presentation_projection_synthesis.md")
    body = open(path, encoding="utf-8").read()
    assert "no \"default\" record" in body and "no reset endpoint" in body
    assert "client_ts" not in body and "/reset`: Resets" not in body
