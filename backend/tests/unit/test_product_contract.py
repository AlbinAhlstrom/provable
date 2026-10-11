"""The product contract: one answer that says what is built, which every later stage is derived from (ADR-011).

The front of a kickstart used to be five model calls in a row (intent, expansion, decomposition, action protocol,
UX plan), each re-reading the one before and free to name things its own way. The contract is one call; the
domain structure, the rule deck, the action manifest, the intent and the page's blueprint are read out of it by
code, so they cannot disagree.
"""
import copy
import json

import pytest

import agent_orchestrator
import llm_provider
from onboarding import product_contract as pc
from onboarding.draft_theme import parse_draft_layout, parse_draft_theme
from onboarding.router_engine import AudienceRole, SpecKind

CONTRACT = {
    "product": {"name": "Table Booking", "product_type": "customer_app", "audience": "Guests of one restaurant",
                "loop": "Pick a table and a time, give a name, get a confirmation, cancel if needed.",
                "has": ["Pick a table (kept)", "Gift cards (left out: payment)"]},
    "look": {"summary": "A warm, plain booking page.",
             "tokens": "background=#faf6f1 surface=#ffffff text=#2b2b2b accent=#c2185b on_accent=#ffffff heading=serif",
             "palette": "#faf6f1 page background; #c2185b the chosen table", "type": "Serif headings, 16px text",
             "parts": ["Floor plan: centre, a grid of 48px tables, the chosen one filled #c2185b"],
             "narrow": "The floor plan scrolls inside itself.", "grid_columns": 4, "grid_rows": 3},
    "opening": "All tables exist and no booking yet. The floor plan shows every table free. On return, taken tables are grey.",
    "records": [
        {"name": "Booking", "origin": "created_by_page", "starting_records": "",
         "shown": ["ends_at = start plus stay_minutes"],
         "fields": [
             {"name": "table_id", "part_of": "", "type": "text", "starts_as": "", "holds": "the table booked",
              "values": [], "part_name": ""},
             {"name": "guests", "part_of": "", "type": "whole_number", "starts_as": "2", "holds": "how many come",
              "values": [], "part_name": ""},
             {"name": "reminded", "part_of": "", "type": "boolean", "starts_as": "false",
              "holds": "whether a reminder went out", "values": [], "part_name": ""},
             {"name": "status", "part_of": "", "type": "one_of", "starts_as": "confirmed",
              "holds": "where the booking stands", "part_name": "",
              "values": ['confirmed: the table is held; shown as "Confirmed"',
                         'cancelled: the table is free again; shown as "Cancelled"']},
             {"name": "courses", "part_of": "", "type": "list_of_parts", "starts_as": "none at first",
              "holds": "what was ordered ahead", "values": [], "part_name": "Course"},
             {"name": "dish", "part_of": "courses", "type": "text", "starts_as": "", "holds": "the dish", "values": [],
              "part_name": ""},
             {"name": "price", "part_of": "courses", "type": "decimal_number", "starts_as": "0", "holds": "its price",
              "values": [], "part_name": ""},
         ]},
        {"name": "Table", "origin": "exists_from_start", "shown": [],
         "starting_records": "Table 1, 2 seats; Table 2, 4 seats",
         "fields": [{"name": "seats", "part_of": "", "type": "whole_number", "starts_as": "", "holds": "how many fit",
                     "values": [], "part_name": ""}]},
    ],
    "fixed": ["max_guests = 8", "stay_minutes = 90"],
    "actions": [
        {"name": "create_booking", "record": "Booking", "performed_by": "audience",
         "params": ["table_id: text", "guests: whole_number"],
         "trigger": "Book button, click or tap, \"Book table\"", "does": "creates a Booking with status confirmed"},
        {"name": "expire_hold", "record": "Booking", "performed_by": "automatic", "params": [],
         "trigger": "when the page sees the hold has run out", "does": "sets status to cancelled"},
        {"name": "mark_no_show", "record": "Booking", "performed_by": "other", "params": [], "trigger": "",
         "does": "sets status to cancelled"},
    ],
    "read_out": ["Table · button · \"Table {number}, {status wording}\"", "Book button · button · \"Book table\""],
    "refusals": [{"name": "TooManyGuestsError", "action": "create_booking",
                  "raised_when": "guests is above max_guests", "sentence": "We seat at most 8 at one table.",
                  "appears": "under the form"}],
    "rules": [
        {"kind": "api", "title": "A booking holds its table", "record": "Booking", "action": "create_booking",
         "given": "a free table", "when": "create_booking(table_id, guests 2)", "then": "a Booking with status confirmed",
         "sees": "\"Table 1, taken\"", "states_limit": False},
        {"kind": "api", "title": "No more than eight guests", "record": "Booking", "action": "create_booking",
         "given": "a free table", "when": "create_booking with guests 9", "then": "TooManyGuestsError, nothing changes",
         "sees": "the sentence under the form", "states_limit": True},
        {"kind": "page", "title": "Book button waits for a table", "record": "Booking", "action": "",
         "given": "no table chosen", "when": "the page opens", "then": "", "sees": "\"Book table\" is unavailable",
         "states_limit": False},
    ],
}


def _contract() -> pc.ProductContract:
    return pc.ProductContract.from_dict(copy.deepcopy(CONTRACT))


def test_the_records_of_the_contract_are_the_domain_structure():
    """Verify the classes the skeleton builds are the contract's records, field for field.

    id: TST-CONTRACT-STRUCTURE
    Given: A contract with a record the page creates and one that exists from the start
    When: Its domain structure is read
    Then: Each record is an entity with an id, its fields carry Python-side types and typed starting values, a list
          of parts carries what one part holds, and the record the page creates is the one the page is organised around
    """
    structure = _contract().structure()

    assert structure.domain_name == "Table Booking"
    booking, table = structure.entities
    assert (booking.name, booking.audience_role) == ("Booking", AudienceRole.CREATED)
    assert (table.name, table.audience_role) == ("Table", AudienceRole.SHOWN)
    assert structure.master_entity() is booking
    fields = {a.name: a for a in booking.attributes}
    assert list(fields) == ["id", "table_id", "guests", "reminded", "status", "courses"]
    assert (fields["guests"].type, fields["guests"].default_value) == ("int", 2)
    assert (fields["reminded"].type, fields["reminded"].default_value) == ("boolean", False)
    assert (fields["status"].type, fields["status"].default_value) == ("string", "confirmed")
    assert fields["table_id"].default_value is None and not fields["table_id"].required
    assert fields["courses"].item_name == "Course"
    assert [(a.name, a.type) for a in fields["courses"].item_attributes] == [("dish", "string"), ("price", "float")]


def test_the_rules_of_the_contract_are_the_rule_deck():
    """Verify every rule becomes one spec, and a rule of the page alone is not sent through the domain's test loop.

    id: TST-CONTRACT-RULES
    Given: A contract with two rules the records obey (one stating a limit) and one rule of the page alone
    When: Its specs are read
    Then: They are numbered in order, the records' rules are behaviour specs with their Given, When and Then, the
          limit is marked, and the page's rule is a presentation spec that says what the person sees
    """
    first, limit, page = _contract().specs()

    assert [s.spec_id for s in (first, limit, page)] == ["SPEC-001", "SPEC-002", "SPEC-003"]
    assert first.kind == limit.kind == SpecKind.BEHAVIOR.value and page.kind == SpecKind.PRESENTATION.value
    assert first.target_aggregate == "Booking"
    assert first.given_when_then == ("Given a free table, When create_booking(table_id, guests 2), "
                                     "Then a Booking with status confirmed")
    assert "Table 1, taken" in first.description
    assert limit.is_mathematical_boundary and not first.is_mathematical_boundary
    assert page.given_when_then == 'Given no table chosen, When the page opens, Then "Book table" is unavailable'


def test_the_actions_of_the_contract_are_the_action_manifest():
    """Verify the manifest the page and the test writers read is the contract's actions, values and refusals.

    id: TST-CONTRACT-MANIFEST
    Given: A contract with an action of the audience, one that happens by itself and one of whoever runs the product
    When: Its action manifest is read
    Then: Each action keeps who performs it and its parameters, an automatic one says when the page sends it, the
          values of a fixed set and what a new record holds are listed, and a refusal carries its exact sentence
    """
    manifest = _contract().action_manifest()

    by_name = {a["name"]: a for a in manifest["actions"]}
    assert [a["performed_by"] for a in manifest["actions"]] == ["audience", "automatic", "other"]
    assert by_name["create_booking"]["params"] == ["table_id", "guests"] and by_name["create_booking"]["aggregate"] == "Booking"
    assert "when the page sees the hold has run out" in by_name["expire_hold"]["description"]
    vocabulary = manifest["vocabulary"][0]
    assert (vocabulary["aggregate"], vocabulary["field"]) == ("Booking", "status")
    assert [v["value"] for v in vocabulary["values"]] == ["confirmed", "cancelled"]
    assert vocabulary["values"][0]["meaning"].startswith("the table is held")
    refusal = manifest["rejections"][0]
    assert refusal["error"] == "TooManyGuestsError" and "We seat at most 8 at one table." in refusal["raised_when"]
    assert refusal["aggregate"] == "Booking"
    start = next(s for s in manifest["starting_states"] if s["aggregate"] == "Booking")["description"]
    assert "guests 2" in start and "status confirmed" in start and "courses" in start


def test_the_look_of_the_contract_is_the_pages_blueprint():
    """Verify the page is planned from the contract: its theme, its outline, its controls and the names it is read by.

    id: TST-CONTRACT-BLUEPRINT
    Given: A contract with a look, an opening, controls, read-out names and a refusal
    When: Its blueprint is read
    Then: The draft theme and the outline of the main view can be taken from it, and it states the opening, each
          control with its label, the names parts are read out by, and where a refusal's sentence appears
    """
    blueprint = _contract().blueprint()

    theme, layout = parse_draft_theme(blueprint), parse_draft_layout(blueprint)
    assert (theme.background, theme.accent, theme.heading) == ("#faf6f1", "#c2185b", "serif")
    assert (layout.columns, layout.rows) == (4, 3)
    assert "### 6. Visual Direction" in blueprint
    for stated in ("The floor plan shows every table free.", '"Book table"', 'shown as "Cancelled"',
                   "when the page sees the hold has run out", '"Table {number}, {status wording}"',
                   "We seat at most 8 at one table.", "under the form", "The floor plan scrolls inside itself."):
        assert stated in blueprint


def test_the_brief_says_what_is_built_in_words():
    """Verify the text later writers are given in place of an expanded pitch holds the product, its records and rules.

    id: TST-CONTRACT-BRIEF
    Given: A contract
    When: Its brief is read
    Then: It names the product, what it has, each record with its fields and starting records, the fixed values
          and every rule
    """
    brief = _contract().brief()

    for stated in ("Table Booking", "Pick a table (kept)", "guests: whole_number = 2", "Table 2, 4 seats",
                   "max_guests = 8", "No more than eight guests", "ends_at = start plus stay_minutes"):
        assert stated in brief


def test_the_intent_follows_from_the_contract():
    """Verify the stages that ask what kind of product this is are answered from the contract.

    id: TST-CONTRACT-INTENT
    Given: A contract
    When: Its intent is read
    Then: It carries the product's kind, audience and loop, covers its records and rules out what is left out
    """
    intent = _contract().intent()

    assert (intent.product_type, intent.audience) == ("customer_app", "Guests of one restaurant")
    assert intent.model_focus == ["Booking", "Table"] and intent.out_of_scope == ["Gift cards (left out: payment)"]


def test_the_contract_is_written_in_one_call_on_the_model_chosen_for_it(monkeypatch):
    """Verify the contract is one call with a schema, given the time a long answer takes.

    id: TST-CONTRACT-CALL
    Given: A model that answers with a contract
    When: The contract of a pitch is written
    Then: One call is made for the stage `product_contract` with the pitch in its prompt, the contract's schema and
          more time than an ordinary call
    """
    seen = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini",
                        lambda prompt, stage="general", **k: seen.append((prompt, stage, k)) or json.dumps(CONTRACT))

    contract = pc.write_product_contract("A table booking page")

    (prompt, stage, options), = seen
    assert stage == "product_contract" and '"A table booking page"' in prompt
    assert options["json_schema"] is pc.CONTRACT_SCHEMA and options["timeout_s"] > agent_orchestrator.DEFAULT_TIMEOUT_S
    assert contract.product.name == "Table Booking" and len(contract.rules) == 3


def test_a_contract_that_was_not_delivered_fails_with_the_reason(monkeypatch):
    """Verify nothing is built on a missing contract.

    id: TST-CONTRACT-FAILS
    Given: A provider that answers nothing, and one that answers with something that is no contract
    When: The contract is written
    Then: Each fails by name with the reason, and nothing is retried
    """
    calls = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: calls.append(1) or "")
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", "APITimeoutError: timed out", raising=False)
    with pytest.raises(pc.ContractError, match="APITimeoutError"):
        pc.write_product_contract("A table booking page")
    assert len(calls) == 1

    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k:
                        '{"product": {"name": "x"}, "look": {"summary": "s"}, "opening": "s"}')
    with pytest.raises(pc.ContractError, match="records"):
        pc.write_product_contract("A table booking page")


def test_every_key_of_the_schema_is_required():
    """Verify the answer cannot leave a key out: a structured answer is only held to keys the schema requires.

    id: TST-CONTRACT-SCHEMA
    Given: The contract's schema
    When: Every object in it is visited
    Then: Each requires all of its properties
    """
    def objects(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                yield node
            for value in node.values():
                yield from objects(value)
        elif isinstance(node, list):
            for value in node:
                yield from objects(value)

    found = list(objects(pc.CONTRACT_SCHEMA))
    assert len(found) >= 8
    for node in found:
        assert sorted(node["required"]) == sorted(node["properties"])


def test_the_schema_is_one_the_provider_compiles():
    """Verify the schema stays inside what the provider turns into a grammar: a larger one is refused before a
    single token is written ("The compiled grammar is too large"), which is how the first shape of the contract failed.

    id: TST-CONTRACT-SCHEMA-SIZE
    Given: The contract's schema
    When: Its properties and its lists are counted
    Then: Together they are no more than the largest shape the provider was measured to accept
    """
    def weight(node):
        if not isinstance(node, dict):
            return 0
        own = len(node.get("properties", {})) + (1 if node.get("type") == "array" else 0)
        return own + sum(weight(child) for child in list(node.get("properties", {}).values()) + [node.get("items")])

    assert weight(pc.CONTRACT_SCHEMA) <= pc.SCHEMA_WEIGHT_LIMIT == 66


def test_a_part_and_what_it_holds_are_fields_of_the_same_list():
    """Verify what one part of a list holds is read from the fields that name the list as theirs.

    id: TST-CONTRACT-PARTS
    Given: A record whose fields include a list of parts and two fields that are part of it
    When: The contract is read
    Then: The record has the list as one field holding the two, and they are not fields of the record itself
    """
    booking = _contract().records[0]

    assert [f.name for f in booking.fields] == ["table_id", "guests", "reminded", "status", "courses"]
    assert [f.name for f in booking.fields[-1].part_fields] == ["dish", "price"]


def test_the_contract_runs_on_the_middle_model(monkeypatch):
    """Verify the one call everything is built on runs on the steadier model (measured alone: it answered in a third
    of the time of the small one and wrote a tenth of its hidden thinking).

    id: TST-CONTRACT-MODEL
    Given: The Anthropic provider
    When: The connection of the contract stage is asked for
    Then: It is the middle model, while an ordinary stage stays on the small one
    """
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("LLM_MODEL_PRODUCT_CONTRACT", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    assert llm_provider.connection("product_contract").model == "claude-sonnet-5-5"
    assert llm_provider.connection("red_test_generation").model == "claude-haiku-5-5"


def test_a_live_kickstart_starts_from_the_contract_and_an_offline_one_from_the_earlier_stages(monkeypatch):
    """Verify which front a kickstart runs, and that the earlier one can still be chosen for a comparison.

    id: TST-CONTRACT-FRONT-KIND
    Given: A live kickstart, an offline one, and a live one with KICKSTART_FRONT=stages
    When: The kind of front is asked for
    Then: Live is the contract; offline and the setting are the earlier stages
    """
    from onboarding import kickstart_front as kf
    monkeypatch.delenv("KICKSTART_FRONT", raising=False)
    assert (kf.front_kind(live=True), kf.front_kind(live=False)) == ("contract", "stages")
    monkeypatch.setenv("KICKSTART_FRONT", "stages")
    assert kf.front_kind(live=True) == "stages"


def test_the_contract_front_answers_the_stages_it_replaces(monkeypatch):
    """Verify everything the builders start from comes out of the one contract, and that the action protocol and
    the UX plan are answered from it without a call of their own.

    id: TST-CONTRACT-FRONT
    Given: A model that answers with a contract
    When: The front of a live kickstart is built
    Then: The structure, the rule deck and the intent are the contract's; the stored specification also holds the
          page's plan; and the action protocol and UX plan stages return the contract's manifest and blueprint
    """
    from onboarding import kickstart_front as kf
    monkeypatch.delenv("KICKSTART_FRONT", raising=False)
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: json.dumps(CONTRACT))

    front = kf.build_front("A table booking page", live=True)

    assert [e.name for e in front.structure.entities] == ["Booking", "Table"]
    assert len(front.inbox_specs) == 3 and front.intent.product_type == "customer_app"
    assert "## Rules" in front.pitch_text and "### 6. Visual Direction" not in front.pitch_text
    assert "### 6. Visual Direction" in front.stored_pitch
    overrides = front.stage_overrides()
    protocol = overrides["protocol"](pitch="", structure=None, inbox_specs=[], workspace_dir="", intent=None)
    assert protocol["success"] and protocol["master_name"] == "Booking"
    assert [a["name"] for a in protocol["action_manifest"]["actions"]] == ["create_booking", "expire_hold", "mark_no_show"]
    assert "TOKENS background=#faf6f1" in overrides["ux"](pitch="", structure=None)
