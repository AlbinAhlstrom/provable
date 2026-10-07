"""The master aggregate is the one the audience creates, not merely the first aggregate root."""

import os

import pytest

import agent_orchestrator
from onboarding.router_engine import AudienceRole, DomainStructureSchema, EntitySpec


def _structure(*entities):
    return DomainStructureSchema(domain_name="Site", entities=list(entities))


def test_master_is_the_entity_the_audience_creates():
    """Verify the master follows the audience's role, not list order.

    id: TST-ROLE-001
    Given: A published catalog entity listed first and a submission entity listed later
    When: The master is chosen
    Then: The submission entity (what visitors create) is the master
    """
    structure = _structure(
        EntitySpec(name="Offering", audience_role=AudienceRole.SHOWN),
        EntitySpec(name="Inquiry", audience_role=AudienceRole.CREATED),
    )
    assert structure.master_entity().name == "Inquiry"


def test_master_falls_back_to_the_first_aggregate_root_then_the_first_entity():
    """Verify structures without roles keep the old rule.

    id: TST-ROLE-002
    Given: Entities with no audience role (internal by default)
    When: The master is chosen
    Then: The first aggregate root wins; with no roots, the first entity; with no entities, None
    """
    assert _structure(EntitySpec(name="Part", is_aggregate_root=False), EntitySpec(name="Order")).master_entity().name == "Order"
    assert _structure(EntitySpec(name="A", is_aggregate_root=False)).master_entity().name == "A"
    assert _structure().master_entity() is None


def test_audience_role_is_validated_and_the_decomposition_prompt_asks_for_it():
    """Verify an unknown role is rejected and the prompt defines all three roles.

    id: TST-ROLE-003
    Given: An entity with a made-up role, and the decomposition prompt
    When: They are read
    Then: The role raises a validation error and the prompt names every role value
    """
    with pytest.raises(ValueError):
        EntitySpec(name="X", audience_role="whatever")
    body = open(os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts", "router_decomposition.md"), encoding="utf-8").read()
    assert all(role.value in body for role in AudienceRole) and "audience_role" in body


def test_entities_with_a_role_get_content_endpoints_listed():
    """Verify helper methods split entities by role for the presentation and seeding stages.

    id: TST-ROLE-004
    Given: One entity of each role
    When: shown_entities and presented_entities are asked for
    Then: shown has only the catalog entity; presented has the master and the catalog entity, never the internal one
    """
    structure = _structure(
        EntitySpec(name="Offering", audience_role=AudienceRole.SHOWN),
        EntitySpec(name="Inquiry", audience_role=AudienceRole.CREATED),
        EntitySpec(name="Audit", audience_role=AudienceRole.INTERNAL),
    )
    assert [e.name for e in structure.shown_entities()] == ["Offering"]
    assert [e.name for e in structure.presented_entities()] == ["Offering", "Inquiry"]


def _site_structure():
    return _structure(
        EntitySpec(name="ServiceOffering", audience_role=AudienceRole.SHOWN,
                   attributes=[{"name": "id", "type": "string"}, {"name": "title", "type": "string"}]),
        EntitySpec(name="ClientInquiry", audience_role=AudienceRole.CREATED,
                   attributes=[{"name": "id", "type": "string"}, {"name": "parent_name", "type": "string"}]),
        EntitySpec(name="AuditNote", audience_role=AudienceRole.INTERNAL, attributes=[{"name": "id", "type": "string"}]),
    )


def test_presentation_gets_a_client_for_the_master_and_for_shown_content_only(tmp_path, monkeypatch):
    """Verify the presentation stage writes clients for what the audience creates and sees, and tells the model so.

    id: TST-ROLE-005
    Given: A site with a shown offering, a created inquiry and an internal note
    When: The projection is synthesized
    Then: Clients exist for the inquiry (master) and the offering, not the note; the prompt lists both with their roles
    """
    from onboarding import presentation_projection_synthesizer as pps
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        seen["prompt"] = prompt
        return ("<<<view_tsx>>>\nexport const V = 1\n<<<app_tsx>>>\n"
                "import {ClientInquiryView} from './views/ClientInquiryView'; export const App = 1\n")

    monkeypatch.setattr(pps, "call_gemini", fake)
    result = pps.synthesize_and_write_presentation_projection(
        pitch="p", structure=_site_structure(), inbox_specs=[], workspace_dir=str(tmp_path), ux_blueprint="plan")
    assert result["success"] is True and result["master_name"] == "ClientInquiry"
    api = tmp_path / "src" / "api"
    assert (api / "client_inquiryClient.ts").exists() and (api / "service_offeringClient.ts").exists()
    assert not (api / "audit_noteClient.ts").exists()
    assert "createClientInquiry" in seen["prompt"] and "listServiceOffering()" in seen["prompt"]
    assert "shown to the audience" in seen["prompt"] and "AuditNote" not in seen["prompt"].split("API clients")[1].split("Content that")[0]


def test_presentation_prompt_forbids_literal_content_and_fake_success():
    """Verify the prompt makes content come from the API and success come from the server.

    id: TST-ROLE-006
    Given: The presentation prompt
    When: It is read
    Then: It tells the model to render shown content from the list functions, never as literals, and to report form success only after create resolves
    """
    body = open(os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts", "presentation_projection_synthesis.md"), encoding="utf-8").read()
    assert "never contains the records themselves as literals" in body
    assert "only after its `create...` call resolves" in body
    assert "{clients_block}" in body
