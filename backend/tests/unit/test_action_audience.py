"""The UI serves the product's audience only: actions performed by anyone else get no controls."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import agent_orchestrator
from onboarding.action_protocol import format_action_protocol
from onboarding.intent import ProductIntent
from onboarding.router_engine import AttributeSpec, BusinessSpec, DomainStructureSchema, EntitySpec

MANIFEST = {"actions": [
    {"name": "submit_inquiry", "performed_by": "audience", "params": ["email"], "description": "Send an enquiry"},
    {"name": "acknowledge_inquiry", "performed_by": "other", "params": [], "description": "Mark as seen"},
    {"name": "legacy_action", "params": []},
]}
INTENT = ProductIntent(product_type="public_website", audience="visitors", primary_goal="g", scope_summary="s",
                       model_focus=["enquiries"], out_of_scope=[])
STRUCTURE = DomainStructureSchema(domain_name="Demo", entities=[EntitySpec(
    name="Enquiry", is_aggregate_root=True, attributes=[AttributeSpec(name="id", type="str", required=True)])])
SPEC = BusinessSpec(spec_id="S1", title="T", description="d", given_when_then="Given a When b Then c", target_aggregate="Enquiry")


def test_protocol_separates_ui_actions_from_api_only_actions():
    """Verify actions by other roles are listed as API-only, never as UI actions.

    id: TST-AUD-001
    Given: A manifest with audience, other-role and unlabelled actions
    When: The protocol block is formatted
    Then: Audience and unlabelled actions are UI actions; the other-role action is under API-only
    """
    block = format_action_protocol(MANIFEST)
    ui, _, api_only = block.partition("API-only")
    assert "submit_inquiry" in ui and "legacy_action" in ui
    assert "acknowledge_inquiry" not in ui
    assert "acknowledge_inquiry" in api_only


def test_protocol_without_manifest_says_so():
    """Verify an absent manifest is stated, not invented.

    id: TST-AUD-002
    Given: No manifest
    When: The block is formatted
    Then: It says no action protocol is available
    """
    assert "No action protocol" in format_action_protocol(None)


def test_the_page_is_told_what_a_new_object_holds():
    """Verify the page writer learns the starting state from the protocol, not from methods it has not seen.

    id: TST-AUD-STARTING-STATE
    Given: A manifest that states what a newly created object of one class holds (the page is written while the
           class's methods are, so the class it is shown does not set itself up yet)
    When: The protocol block is formatted for the page
    Then: The block states it, by class
    """
    manifest = {**MANIFEST, "starting_states": [
        {"aggregate": "Enquiry", "description": "status is \"new\" and replies is empty"}]}
    block = format_action_protocol(manifest)
    assert "A newly created `Enquiry`" in block and 'status is "new" and replies is empty' in block
    assert "newly created" not in format_action_protocol(MANIFEST)


def test_action_protocol_prompt_asks_who_performs_each_action(tmp_path, monkeypatch):
    """Verify the action-design prompt asks for performed_by relative to the intent's audience.

    id: TST-AUD-003
    Given: An intent with an audience
    When: The action protocol is synthesized
    Then: The prompt asks each action to declare whether the audience or someone else performs it
    """
    from onboarding.domain_engine_synthesizer import synthesize_action_protocol
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        seen["p"] = prompt
        return '{"action_manifest": {"actions": []}}'

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    synthesize_action_protocol("p", STRUCTURE, [SPEC], str(tmp_path), intent=INTENT)
    assert "performed_by" in seen["p"] and "audience" in seen["p"]


def test_presentation_prompt_forbids_controls_for_api_only_actions(tmp_path, monkeypatch):
    """Verify the UI prompt lists the other-role action as API-only with an explicit no-controls rule.

    id: TST-AUD-004
    Given: A manifest with an other-role action
    When: The presentation projection is synthesized
    Then: The prompt names it under API-only and tells the model to render no controls for such actions
    """
    from onboarding import presentation_projection_synthesizer as pps
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        if stage == "presentation_projection_synthesis":
            seen["p"] = prompt
        return "{}"

    monkeypatch.setattr(pps, "call_gemini", fake)
    pps.synthesize_and_write_presentation_projection(
        pitch="p", structure=STRUCTURE, inbox_specs=[SPEC], workspace_dir=str(tmp_path),
        action_manifest=MANIFEST, ux_blueprint="plan", intent=INTENT)
    ui, _, api_only = seen["p"].partition("API-only")
    assert "acknowledge_inquiry" not in ui.split("Authoritative Backend Action Protocol")[-1]
    assert "acknowledge_inquiry" in api_only
    assert "no buttons" in seen["p"].lower() or "no controls" in seen["p"].lower()


def test_the_page_call_is_given_the_time_the_largest_answer_needs(tmp_path, monkeypatch):
    """Verify the call that writes the whole page is not cut off by the time allowed for a short answer.

    id: TST-AUD-PAGE-TIME
    Given: A recording model
    When: The presentation projection is synthesized
    Then: The call carries the page's own time limit, longer than the default of a call
    """
    from onboarding import presentation_projection_synthesizer as pps
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        seen.update(kwargs)
        return "{}"

    monkeypatch.setattr(pps, "call_gemini", fake)
    pps.synthesize_and_write_presentation_projection(
        pitch="p", structure=STRUCTURE, inbox_specs=[SPEC], workspace_dir=str(tmp_path),
        action_manifest=MANIFEST, ux_blueprint="plan", intent=INTENT)
    assert seen["timeout_s"] == pps.PAGE_TIMEOUT_S > agent_orchestrator.DEFAULT_TIMEOUT_S


def test_the_action_protocol_is_held_to_a_schema_and_asks_for_starting_states(tmp_path, monkeypatch):
    """Verify the protocol's answer is constrained by the provider and covers what a new object holds.

    id: TST-AUD-SCHEMA
    Given: A domain with a master aggregate
    When: The action protocol is synthesized and the model answers with actions and a starting state
    Then: The call carried a JSON schema naming both lists, the prompt asks for starting states, and the manifest
          keeps the starting state
    """
    from onboarding.domain_engine_synthesizer import synthesize_action_protocol
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        seen.update(prompt=prompt, **kwargs)
        return ('{"action_manifest": {"actions": [], "starting_states": '
                '[{"aggregate": "Inquiry", "description": "status is new"}]}}')

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    result = synthesize_action_protocol("p", STRUCTURE, [SPEC], str(tmp_path), intent=INTENT)
    manifest_schema = seen["json_schema"]["properties"]["action_manifest"]["properties"]
    assert {"actions", "starting_states"} <= set(manifest_schema)
    assert "starting_states" in seen["prompt"]
    assert result["success"] and result["action_manifest"]["starting_states"][0]["description"] == "status is new"


def test_the_action_protocol_fixes_the_shared_words(tmp_path, monkeypatch):
    """Verify the protocol is asked for field values and refusal names, and the schema carries them.

    id: TST-AUD-WORDS
    Given: A domain with a master aggregate
    When: The action protocol is synthesized
    Then: The schema requires `vocabulary` and `rejections` beside the actions, and the prompt asks for both
    """
    from onboarding.domain_engine_synthesizer import synthesize_action_protocol
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        seen.update(prompt=prompt, **kwargs)
        return '{"action_manifest": {"actions": [], "starting_states": [], "vocabulary": [], "rejections": []}}'

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    synthesize_action_protocol("p", STRUCTURE, [SPEC], str(tmp_path), intent=INTENT)
    manifest_schema = seen["json_schema"]["properties"]["action_manifest"]
    assert {"vocabulary", "rejections"} <= set(manifest_schema["required"])
    assert "vocabulary" in seen["prompt"] and "rejections" in seen["prompt"]


def test_an_action_nobody_performs_by_hand_is_the_pages_own_to_send():
    """Verify an action that happens by itself is handed to the page to perform, with no control.

    id: TST-AUD-AUTOMATIC
    Given: A manifest with an action marked automatic (a game's clock was marked as someone else's, the page was
           told to leave it alone, and nothing in the running product ever performed it: the time stood still)
    When: The protocol block is formatted, and the prompts of the action protocol and the page are read
    Then: The action is listed apart from the controls and from the API-only actions, with the client that sends
          it; the protocol's prompt offers that performer and the page's prompt says the page sends such actions
    """
    manifest = {"actions": MANIFEST["actions"] + [
        {"name": "advance_clock", "aggregate": "Enquiry", "performed_by": "automatic", "params": ["seconds"],
         "description": "Counts the time on"}]}
    block = format_action_protocol(manifest)
    controls, _, rest = block.partition("Actions the page performs by itself")
    by_itself, _, api_only = rest.partition("API-only")
    assert "advance_clock" not in controls and "advance_clock" not in api_only
    assert "advance_clock" in by_itself and "enquiryClient.ts" in by_itself
    assert "acknowledge_inquiry" in api_only
    prompts = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")
    with open(os.path.join(prompts, "domain_engine_synthesis.md"), encoding="utf-8") as handle:
        protocol = handle.read()
    assert '"automatic"' in protocol and "Nothing runs beside the page and the API" in protocol
    with open(os.path.join(prompts, "presentation_projection_synthesis.md"), encoding="utf-8") as handle:
        page = handle.read()
    assert 'Actions listed under "Actions the page performs by itself"' in page


def test_the_page_is_told_which_actions_are_sent_to_the_kind():
    """Verify the page sends an action done to no one record without an id, and makes records through it.

    id: TST-AUD-KIND-ACTION
    Given: A manifest with an action sent to the kind and one sent to a record
    When: The action protocol is written out for the page
    Then: Each is listed as the call of its own function of the client: the first takes no id, the second the
          record's id, and params only where the action has them
    """
    from onboarding.action_protocol import format_action_protocol
    text = format_action_protocol({"actions": [
        {"name": "place_order", "aggregate": "Order", "params": ["dish_id"], "on_kind": True, "given": ["Order"]},
        {"name": "cancel_order", "aggregate": "Order", "params": []}]})
    place, cancel = (next(l for l in text.splitlines() if f"`{n}`" in l) for n in ("place_order", "cancel_order"))

    assert "`orderActions.place_order(params)` of `src/api/orderClient.ts`" in place and "no id" in place
    assert "`orderActions.cancel_order(id)` of `src/api/orderClient.ts`" in cancel and "the id of that Order" in cancel
    assert "sendAction" not in text and "sendKindAction" not in text
