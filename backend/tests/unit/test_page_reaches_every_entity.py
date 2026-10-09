"""The page can reach every entity its audience works with, and sends each action to the entity that owns it.

An internal tool's users create customers, jobs and invoices. Built around one master with one client, its page sent
job and invoice actions to the customer record, where no such method exists.
"""
from onboarding import presentation_projection_synthesizer as presentation
from onboarding.action_protocol import format_action_protocol
from onboarding.router_engine import AudienceRole, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton

STRUCTURE = DomainStructureSchema(domain_name="Plumbing", entities=[
    EntitySpec(name="Customer", audience_role=AudienceRole.CREATED,
               attributes=[{"name": "id", "type": "string"}, {"name": "name", "type": "string"}]),
    EntitySpec(name="Job", audience_role=AudienceRole.CREATED,
               attributes=[{"name": "id", "type": "string"}, {"name": "customer_id", "type": "string"}, {"name": "status", "type": "string"}]),
    EntitySpec(name="AuditEntry", audience_role=AudienceRole.INTERNAL, attributes=[{"name": "id", "type": "string"}]),
])

MANIFEST = {"actions": [
    {"name": "update_contact_info", "aggregate": "Customer", "performed_by": "audience", "params": ["phone"], "description": "Change the phone number"},
    {"name": "start_job", "aggregate": "Job", "performed_by": "audience", "params": [], "description": "Work begins"},
]}


def test_every_entity_the_audience_creates_is_presented():
    """Verify the interface is given all the records its audience works with, not only the first.

    id: TST-REACH-001
    Given: Two entities the audience creates and an internal one
    When: The presented entities are asked for
    Then: Both created entities are presented and the internal one is not; the first is still the master
    """
    assert [e.name for e in STRUCTURE.presented_entities()] == ["Customer", "Job"]
    assert STRUCTURE.master_entity().name == "Customer"


def test_each_action_names_the_entity_and_client_it_is_sent_through():
    """Verify the protocol the page is written from says where each action goes.

    id: TST-REACH-002
    Given: A manifest with one action on Customer and one on Job
    When: The protocol block is formatted
    Then: Each line names its aggregate and that aggregate's client
    """
    lines = format_action_protocol(MANIFEST).splitlines()
    assert "`update_contact_info`" in lines[0] and "`Customer`" in lines[0] and "customerClient" in lines[0]
    assert "`start_job`" in lines[1] and "`Job`" in lines[1] and "jobClient" in lines[1]


def test_the_page_is_written_knowing_every_created_class_and_client(tmp_path, monkeypatch):
    """Verify the presentation prompt carries the classes and clients of all entities the audience creates.

    id: TST-REACH-003
    Given: A skeleton with two created entities, and a model call that records the prompt
    When: The presentation is synthesized
    Then: The prompt shows both domain classes, offers both clients, and says an action is sent through the client
          of the entity it is listed on
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    prompts = []
    monkeypatch.setattr(presentation, "call_gemini", lambda prompt, stage="": prompts.append(prompt) or "")
    presentation.synthesize_and_write_presentation_projection(
        pitch="a tool for a plumbing company", structure=STRUCTURE, inbox_specs=[], workspace_dir=str(tmp_path),
        action_manifest=MANIFEST, ux_blueprint="plan")

    prompt = prompts[0]
    assert "class Customer:" in prompt and "class Job:" in prompt and "class AuditEntry:" not in prompt
    assert "src/api/customerClient.ts" in prompt and "src/api/jobClient.ts" in prompt
    assert "the client of the entity it is listed on" in prompt
