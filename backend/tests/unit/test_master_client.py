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


def test_an_action_outlives_the_page_and_may_answer_with_a_new_record():
    """
    Given: A master aggregate
    When: Its client is generated
    Then: An action is sent so that it still reaches the server when the page is left while it is on its way,
          and its answer is typed with the record the action may have made
    """
    client = generate_master_client(ENTITY)
    action = client[client.index("export async function sendAction"):]
    assert "keepalive: true" in action
    assert "created: CareInquiryState | null;" in client


def _blocks(**sections):
    return "".join(f"<<<{name}>>>\n{code}\n" for name, code in sections.items())


_GOOD = dict(view_tsx="export const V = 1", controls_tsx="export const C = 1", history_tsx="export const H = 1",
             app_tsx="import {CareInquiryView} from './views/CareInquiryView'; export const App = 1")


def _synthesize(pps, tmp_path, monkeypatch, answer):
    monkeypatch.setattr(pps, "call_gemini", lambda prompt, stage="general", **k: answer)
    return pps.synthesize_and_write_presentation_projection(
        pitch="p", structure=STRUCTURE, inbox_specs=[SPEC], workspace_dir=str(tmp_path), action_manifest={"actions": []}, ux_blueprint="plan")


def test_presentation_stage_writes_the_deterministic_client_and_rejects_a_model_client(tmp_path, monkeypatch):
    """Verify the model cannot supply the client: an unknown section is rejected, the generated client is written.

    id: TST-CLI-002
    Given: An answer with an extra client section, then a well-formed answer
    When: The projection is synthesized
    Then: The first is rejected naming the section; the second writes the generated client
    """
    from onboarding import presentation_projection_synthesizer as pps
    rejected = _synthesize(pps, tmp_path, monkeypatch, _blocks(client_ts="FABRICATED", **_GOOD))
    assert rejected["success"] is False and "client_ts" in rejected["error"]
    result = _synthesize(pps, tmp_path, monkeypatch, _blocks(**_GOOD))
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
    result = _synthesize(pps, tmp_path, monkeypatch, _blocks(view_tsx="export const V = 1", app_tsx="export const App = 1"))
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


def test_file_blocks_carry_code_verbatim_and_malformed_answers_say_what_is_wrong():
    """Verify code with quotes, braces, backticks and fences survives, and bad answers are named precisely.

    id: TST-CLI-005
    Given: Block answers: one with awkward code, one fenced, and malformed ones
    When: They are parsed
    Then: Code is verbatim (a fence around a block is unwrapped); a missing marker, an unknown or a repeated section raises;
          the answer ends at its end marker, and the prompt asks for that marker and types lists as their client does
    """
    import pytest
    from onboarding.presentation_projection_synthesizer import parse_file_blocks
    code = 'const a = `x`; const s = "q\\"uote"; // ```\nexport const App = () => <div style={{ a: 1 }} />;'
    one = f"<<<view_tsx>>>\n{code}\n<<<app_tsx>>>\nexport const App = 1\n"
    assert parse_file_blocks(one) == {"view_tsx": code, "app_tsx": "export const App = 1"}
    fenced = "<<<app_tsx>>>\n```tsx\nexport const App = 1\n```\n"
    assert parse_file_blocks(fenced) == {"app_tsx": "export const App = 1"}
    closed = "<<<app_tsx>>>\nexport const App = 1\n<<<end>>>\nThat is the whole page.\n"
    assert parse_file_blocks(closed) == {"app_tsx": "export const App = 1"}
    import os
    import agent_orchestrator
    prompt = open(os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts",
                               "presentation_projection_synthesis.md"), encoding="utf-8").read()
    assert prompt.rstrip().endswith("<<<end>>>") and "Object.values" not in prompt
    for bad, fragment in (("just prose", "no <<<section>>> markers"), ("<<<nope>>>\nx", "unknown section"),
                          ("<<<app_tsx>>>\na\n<<<app_tsx>>>\nb", "appears twice")):
        with pytest.raises(ValueError, match=fragment):
            parse_file_blocks(bad)


def test_presentation_prompt_asks_for_marked_blocks_not_json():
    """Verify the prompt and the parser agree on the answer format.

    id: TST-CLI-006
    Given: The presentation prompt
    When: It is read
    Then: It names every section marker the parser accepts and does not ask for JSON
    """
    from onboarding.presentation_projection_synthesizer import SECTIONS
    path = os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts", "presentation_projection_synthesis.md")
    body = open(path, encoding="utf-8").read()
    assert all(f"<<<{name}>>>" in body for name in SECTIONS)
    assert "JSON object" not in body and "STRICTLY with a JSON" not in body


def test_an_optional_file_the_model_did_not_write_is_not_created(tmp_path, monkeypatch):
    """Verify an empty module is not written as a component (styling later turned one into 440 lines nothing imports).

    id: TST-CLI-020
    Given: An answer with a view and an App, an empty-module controls block and no history block
    When: The projection is synthesized
    Then: Only the view and App are written as components, and the result names both omitted files
    """
    from onboarding import presentation_projection_synthesizer as pps
    answer = _blocks(view_tsx=_GOOD["view_tsx"], controls_tsx="export {};", app_tsx=_GOOD["app_tsx"])
    result = _synthesize(pps, tmp_path, monkeypatch, answer)
    assert result["success"] is True
    assert not (tmp_path / "src" / "components" / "Controls" / "CareInquiryControls.tsx").exists()
    assert not (tmp_path / "src" / "components" / "History" / "CareInquiryHistory.tsx").exists()
    assert result["omitted"] == ["controls_tsx", "history_tsx"]
    assert not any("Controls" in f or "History" in f for f in result["files"])
    assert result["component_lines"] == {"src/views/CareInquiryView.tsx": 1, "src/App.tsx": 1}


def test_presentation_prompt_asks_for_only_the_files_that_are_needed():
    """Verify the prompt tells the model to leave an unneeded file's marker out, not to fill it with a stub.

    id: TST-CLI-021
    Given: The presentation prompt
    When: It is read
    Then: It says a marker is written only for a file that has a component in it
    """
    path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "presentation_projection_synthesis.md")
    with open(path, encoding="utf-8") as f:
        text = " ".join(f.read().split())
    assert "Write a marker only for a file you actually write" in text


def test_the_prompt_tells_the_form_which_fields_a_create_needs(tmp_path, monkeypatch):
    """Verify the form is told what to send, so a create is not rejected for a field the visitor never enters.

    id: TST-CLI-022
    Given: A master aggregate with a required field, an optional field and an id
    When: The presentation prompt is built
    Then: It says the server assigns the id and names the required field to send, not the optional one
    """
    from onboarding import presentation_projection_synthesizer as pps
    prompts = []
    monkeypatch.setattr(pps, "call_gemini", lambda prompt, stage="general", **k: prompts.append(prompt) or _blocks(**_GOOD))
    pps.synthesize_and_write_presentation_projection(
        pitch="p", structure=STRUCTURE, inbox_specs=[SPEC], workspace_dir=str(tmp_path), action_manifest={"actions": []}, ux_blueprint="plan")
    line = next(l for l in prompts[0].splitlines() if "care_inquiryClient.ts" in l)
    assert "the server assigns `id`" in line and "must carry: `hours`" in line and "parent_email" not in line.split("must carry:")[1]


def test_a_record_made_on_opening_is_opened_by_the_client(tmp_path):
    """Verify the page is handed the record it works on, so that making the first one is not left to its writer.

    id: TST-CLI-OPEN
    Given: A master the page makes by itself when it opens, and one a person creates
    When: Their clients and the prompt's description of them are generated
    Then: The first client exports an open function that gives the newest record or creates one in its starting
          state, and the prompt tells the page to call it on opening; the second has neither
    """
    from onboarding.presentation_projection_synthesizer import _clients_block
    session = EntitySpec(name="Session", is_aggregate_root=True, audience_role="created_by_audience",
                         created_on_opening=True, attributes=[AttributeSpec(name="id", type="str", required=True)])

    client = generate_master_client(session)
    assert "export function openSession(): Promise<SessionState>" in client
    assert "all.length ? all[all.length - 1] : createSession({})" in client
    told = _clients_block([session], "Session")
    assert "`openSession(): Promise<SessionState>`" in told and "when the page opens" in told

    assert "openCareInquiry" not in generate_master_client(ENTITY)
    assert "openCareInquiry" not in _clients_block([ENTITY], "CareInquiry")


def test_the_client_sends_an_action_to_the_kind():
    """Verify the page has a way to send an action that is done to no one record.

    id: TST-CLIENT-KIND-ACTION
    Given: An entity
    When: Its client is generated
    Then: It exports a function that posts to the kind's action endpoint and answers the record made and the
          kind's records afterwards
    """
    from onboarding.router_engine import AttributeSpec, EntitySpec
    from onboarding.skeleton_builder import generate_master_client
    client = generate_master_client(EntitySpec(name="Order", is_aggregate_root=True, attributes=[
        AttributeSpec(name="id", type="str", required=True)]))

    assert "export async function sendKindAction(" in client
    assert "fetch(`${BASE_URL}/action`" in client
    assert "created: OrderState | null;" in client and "records: OrderState[];" in client


ORDER = EntitySpec(name="Order", is_aggregate_root=True, attributes=[AttributeSpec(name="id", type="str", required=True)])
ORDER_ACTIONS = [
    {"name": "place_order", "aggregate": "Order", "params": ["dish_id", "quantity"], "on_kind": True},
    {"name": "clear_served", "aggregate": "Order", "params": [], "on_kind": True},
    {"name": "add_line", "aggregate": "Order", "params": ["dish_id"]},
    {"name": "cancel_order", "aggregate": "Order", "params": []},
    {"name": "restock", "aggregate": "Dish", "params": []}]


def test_the_client_has_one_function_per_action_sent_the_way_the_plan_says():
    """Verify how an action is sent is written by the generator, so that no page writer has to work it out.

    id: TST-CLIENT-ACTIONS
    Given: A class with an action done to no one record and an action done to one, with and without params,
           and an action of another class
    When: Its client is generated with the plan's actions
    Then: It exports one function per action of the class under the action's own name: the first kind takes no id
          and goes to the kind, the second takes the record's id; each takes exactly the action's params; the other
          class's action is not there
    """
    client = generate_master_client(ORDER, actions=ORDER_ACTIONS)

    assert "export const orderActions = {" in client
    assert ("  place_order: (params: { dish_id: unknown; quantity: unknown }): Promise<KindActionResponse> =>\n"
            "    sendKindAction('place_order', params),") in client
    assert "  clear_served: (): Promise<KindActionResponse> =>\n    sendKindAction('clear_served')," in client
    assert ("  add_line: (id: string, params: { dish_id: unknown }): Promise<ActionResponse> =>\n"
            "    sendAction(id, 'add_line', params),") in client
    assert "  cancel_order: (id: string): Promise<ActionResponse> =>\n    sendAction(id, 'cancel_order')," in client
    assert "restock" not in client


def test_a_client_of_a_class_without_actions_has_no_action_functions():
    """
    id: TST-CLIENT-ACTIONS-NONE
    Given: A class none of the plan's actions belongs to
    When: Its client is generated with the plan's actions
    Then: It is the client the class has without them
    """
    assert generate_master_client(ENTITY, actions=ORDER_ACTIONS) == generate_master_client(ENTITY)
    assert "Actions = {" not in generate_master_client(ENTITY)


def test_the_page_is_told_of_the_action_functions_and_of_no_other_way_to_send():
    """Verify the page is given one way to send each action.

    id: TST-CLIENT-ACTIONS-TOLD
    Given: A class with actions and a class with none
    When: The prompt's description of their clients is written
    Then: The first is described with its action functions and what each kind answers; neither description offers
          a sender that takes the action's name as text
    """
    from onboarding.presentation_projection_synthesizer import _clients_block
    told = _clients_block([ORDER, ENTITY], "Order", actions=ORDER_ACTIONS)
    order, inquiry = told.splitlines()

    assert "`orderActions`" in order and "records: OrderState[]" in order and "state: OrderState" in order
    assert "Actions`" not in inquiry
    assert "sendAction" not in told and "sendKindAction" not in told
