"""The product contract: one answer that says what is built, which every later stage is derived from (ADR-011).

The front of a kickstart used to be five model calls in a row (intent, expansion, decomposition, action protocol,
UX plan), each re-reading the one before and free to name things its own way. The contract is one call; the
domain structure, the rule deck, the action manifest, the intent and the page's blueprint are read out of it by
code, so they cannot disagree.
"""
import os
import copy
import json

import pytest

import agent_orchestrator
import llm_provider
from onboarding import product_contract as pc
from onboarding.draft_theme import parse_draft_layout, parse_draft_theme
from onboarding.router_engine import AudienceRole, SpecKind
from onboarding.skeleton_builder import build_and_write_skeleton

CONTRACT = {
    "product": {"name": "Table Booking", "product_type": "customer_app", "audience": "Guests of one restaurant",
                "loop": "Pick a table and a time, give a name, get a confirmation, cancel if needed.",
                "has": ["Pick a table (kept)", "Gift cards (left out: payment)"]},
    "look": {"summary": "A warm, plain booking page.",
             "tokens": "background=#faf6f1 surface=#ffffff text=#2b2b2b accent=#c2185b on_accent=#ffffff heading=serif",
             "palette": "#faf6f1 page background; #c2185b the chosen table",
             "parts": ["Floor plan: centre, a grid of 48px tables, the chosen one filled #c2185b"],
             "narrow": "The floor plan scrolls inside itself.", "grid": "columns=4 rows=3"},
    "opening": "All tables exist and no booking yet. The floor plan shows every table free. On return, taken tables are grey.",
    "records": [
        {"name": "Booking", "origin": "created_by_person", "starting_records": "",
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
             {"name": "courses", "part_of": "", "type": "list_of_parts", "starts_as": "",
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
    "fixed": "max_guests = 8; stay_minutes = 90",
    "actions": [
        {"name": "create_booking", "record": "Booking", "performed_by": "audience",
         "params": "table_id: text, guests: whole_number", "sent_to": "the_kind",
         "trigger": "Book button, click or tap, \"Book table\"", "does": "creates a Booking with status confirmed",
         "works_with": "Booking, Table"},
        {"name": "expire_hold", "record": "Booking", "performed_by": "automatic", "params": "", "sent_to": "one_record",
         "trigger": "when the page sees the hold has run out", "does": "sets status to cancelled", "works_with": ""},
        {"name": "mark_no_show", "record": "Booking", "performed_by": "other", "params": "", "trigger": "",
         "sent_to": "one_record", "does": "deletes the Booking", "works_with": "Booking"},
    ],
    "read_out": ["Table · button · \"Table {number}, {status wording}\"", "Book button · button · \"Book table\""],
    "refusals": [{"name": "TooManyGuestsError", "action": "create_booking",
                  "raised_when": "guests is above max_guests", "sentence": "We seat at most 8 at one table.",
                  "appears": "under the form"}],
    "situations": ["two_tables_free = two tables and nobody has booked: Table 1 with seats 2, Table 2 with seats 4; no Booking",
                   "table_1_taken = the first table is booked: as two_tables_free, and a Booking with table_id of Table 1, "
                   "guests 2, status confirmed"],
    "rules": [
        {"kind": "api", "title": "A booking holds its table", "action": "create_booking",
         "given": "two_tables_free", "when": "create_booking(table_id of Table 1, guests 2)",
         "then": "a Booking with status confirmed", "sees": "\"Table 1, taken\"",
         "plain": "Given a free table, When a guest books it for two, Then the table is theirs"},
        {"kind": "api", "title": "No more than eight guests", "action": "create_booking",
         "given": "two_tables_free", "when": "create_booking with guests 9", "then": "TooManyGuestsError, nothing changes",
         "sees": "the sentence under the form",
         "plain": "Given a free table, When a guest asks for nine seats, Then they are told eight is the most"},
        {"kind": "page", "title": "Book button waits for a table", "action": "",
         "given": "two_tables_free, no table chosen", "when": "the page opens", "then": "",
         "sees": "\"Book table\" is unavailable",
         "plain": "Given no table is chosen, When a guest arrives, Then booking is not yet offered"},
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
    assert first.given_when_then == ("Given two_tables_free, When create_booking(table_id of Table 1, guests 2), "
                                     "Then a Booking with status confirmed")
    assert "Table 1, taken" in first.description
    assert not limit.is_mathematical_boundary and not first.is_mathematical_boundary
    assert page.given_when_then == ('Given two_tables_free, no table chosen, When the page opens, '
                                    'Then "Book table" is unavailable')


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
                   "- max_guests = 8", "- stay_minutes = 90", "No more than eight guests", "ends_at = start plus stay_minutes"):
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

    assert weight(pc.CONTRACT_SCHEMA) <= pc.SCHEMA_WEIGHT_LIMIT == 65


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


def test_what_a_field_holds_reaches_the_class_every_writer_reads(tmp_path):
    """Verify the test writer, the code writer and the page read the same words about a field, from the class.

    id: TST-CONTRACT-FIELD-WORDS
    Given: A contract whose booking has described fields, a moment among them, and a list of described parts
    When: The skeleton is written from its structure
    Then: The class's description says what each field holds, the one form a moment is written in, and what each
          key of a part holds
    """
    data = copy.deepcopy(CONTRACT)
    data["records"][0]["fields"].append({"name": "made_at", "part_of": "", "type": "moment", "starts_as": "",
                                         "holds": "when it was made", "values": [], "part_name": ""})
    build_and_write_skeleton(pc.ProductContract.from_dict(data).structure(), target_dir=str(tmp_path))

    domain = (tmp_path / "src" / "domain" / "booking.py").read_text(encoding="utf-8")
    assert "    guests: how many come\n" in domain
    assert "2030-01-31T09:30:00+00:00" in pc.FORMS["moment"]
    assert f"    made_at: when it was made; {pc.FORMS['moment']}\n" in domain
    assert "with the keys dish (str, the dish), price (float, its price)." in domain


def test_the_contract_says_whether_a_new_record_is_whole_by_its_defaults():
    """Verify nobody is asked to prove a starting state the skeleton already wrote into the class.

    id: TST-CONTRACT-START-DEFAULTS
    Given: A booking whose fields all start as plain values and whose list starts empty; then the same booking with
           a list that holds parts from the start; then with a number whose start is said in words
    When: The action manifest is read
    Then: The first is held by the class's defaults, the other two are not; all three still say what a new one holds
    """
    def booking_start(data):
        manifest = pc.ProductContract.from_dict(data).action_manifest()
        return next(s for s in manifest["starting_states"] if s["aggregate"] == "Booking")

    plain, filled, worded = copy.deepcopy(CONTRACT), copy.deepcopy(CONTRACT), copy.deepcopy(CONTRACT)
    filled["records"][0]["fields"][4]["starts_as"] = "three courses, each without a dish"
    worded["records"][0]["fields"][1]["starts_as"] = "as many as the table seats"

    assert booking_start(plain)["held_by_defaults"] is True
    assert booking_start(filled)["held_by_defaults"] is False
    assert booking_start(worded)["held_by_defaults"] is False
    assert all("status confirmed" in booking_start(d)["description"] for d in (plain, filled, worded))


def test_the_contract_decides_who_makes_the_first_record():
    """Verify whether the page makes its record by itself on opening is a fact of the contract, not a sentence.

    id: TST-CONTRACT-OPENING-RECORD
    Given: A record a person creates with the page; then the same record created by the page when it opens
    When: The domain structure and the brief are read
    Then: Both are records the audience works with, only the second is marked as made on opening, and the brief
          says which it is; the schema offers the three origins
    """
    by_person, on_opening = copy.deepcopy(CONTRACT), copy.deepcopy(CONTRACT)
    on_opening["records"][0]["origin"] = "created_on_opening"

    person = pc.ProductContract.from_dict(by_person)
    opening = pc.ProductContract.from_dict(on_opening)

    assert person.structure().entities[0].audience_role == AudienceRole.CREATED
    assert person.structure().entities[0].created_on_opening is False
    assert opening.structure().entities[0].audience_role == AudienceRole.CREATED
    assert opening.structure().entities[0].created_on_opening is True
    assert opening.structure().master_entity().name == "Booking"
    assert "### Booking: a person creates it with the page" in person.brief()
    assert "### Booking: the page creates one when it opens and none exists" in opening.brief()
    origins = pc.CONTRACT_SCHEMA["properties"]["records"]["items"]["properties"]["origin"]["enum"]
    assert origins == ["created_by_person", "created_on_opening", "exists_from_start"]


def test_a_rule_starts_from_a_situation_the_contract_wrote_once():
    """Verify a rule's starting point reaches its test writers as the contract wrote it, values and all, so two
    writers of the same rule arrange the same records.

    id: TST-CONTRACT-SITUATIONS
    Given: A contract with two situations, and rules whose Given names one of them
    When: Its specs and its brief are read
    Then: Each spec carries the situation its Given names, as its name and what it holds; a Given that names one
          and adds to it still finds it; and the brief lists every situation once
    """
    contract = _contract()
    first, _, page = contract.specs()

    assert first.situation == ("`two_tables_free`: two tables and nobody has booked: Table 1 with seats 2, "
                               "Table 2 with seats 4; no Booking")
    assert page.situation.startswith("`two_tables_free`: ")
    assert contract.brief().count("table_1_taken = the first table is booked") == 1


def test_a_given_that_names_no_situation_carries_none():
    """Verify a rule whose Given is written in words of its own is passed on as it is, with nothing made up for it.

    id: TST-CONTRACT-SITUATIONS-NONE
    Given: A contract whose first rule's Given names no situation
    When: Its specs are read
    Then: That spec carries no situation
    """
    data = copy.deepcopy(CONTRACT)
    data["rules"][0]["given"] = "a free table"

    assert pc.ProductContract.from_dict(data).specs()[0].situation == ""


def test_a_rule_is_also_said_in_the_words_of_the_person_who_uses_the_product():
    """Verify the card a person reads is not the line a test is written from: the rule carries both.

    id: TST-CONTRACT-PLAIN
    Given: A contract whose rules each have a plain wording beside their exact one
    When: Its specs are read
    Then: Each spec carries the plain wording, and its exact Given, When and Then are unchanged by it
    """
    first = _contract().specs()[0]

    assert first.plain == "Given a free table, When a guest books it for two, Then the table is theirs"
    assert "create_booking" in first.given_when_then and "create_booking" not in first.plain


def test_a_rule_is_about_the_record_its_action_is_sent_to():
    """Verify the record a rule is about follows from the contract and is not written a second time by the model.

    id: TST-CONTRACT-RULE-RECORD
    Given: A contract with two records, a rule on an action of the first and a rule of the page alone
    When: Its specs are read
    Then: The action's rule is about the action's record, and the page's rule about the record a person makes
    """
    first, _, page = _contract().specs()

    assert first.target_aggregate == "Booking" and page.target_aggregate == "Booking"
    assert "record" not in pc.CONTRACT_SCHEMA["properties"]["rules"]["items"]["properties"]


def test_a_rule_names_the_action_it_proves():
    """Verify the round can tell which actions the deck's rules already prove.

    id: TST-CONTRACT-RULE-ACTION
    Given: A contract with two rules on one action and a rule of the page alone
    When: Its specs are read
    Then: The first two carry the action's name, the page's rule carries none
    """
    assert [spec.action for spec in _contract().specs()] == ["create_booking", "create_booking", ""]


def test_a_limit_is_two_rules_and_no_flag():
    """Verify a rule of the contract is one call with one outcome, also where it states a limit.

    A flag on the rule made the test gate ask for both sides of the limit in that one rule's test. The contract had
    already written the two sides as two rules (or the rule refused nothing at all), so the first test was sent
    back to a writer every time.

    id: TST-CONTRACT-LIMIT
    Given: The contract's schema and prompt
    When: They are read
    Then: A rule has no limit flag, and the prompt asks for the value at the limit and the value past it as two rules
    """
    rule = pc.CONTRACT_SCHEMA["properties"]["rules"]["items"]["properties"]
    assert "states_limit" not in rule
    path = os.path.join(os.path.dirname(pc.__file__), "..", "prompts", "product_contract.md")
    text = open(path, encoding="utf-8").read()
    assert "states_limit" not in text and "A limit is two rules" in text


def test_a_part_reached_by_its_place_holds_that_place():
    """Verify the contract decides how a part is found, so no writer after it has to.

    A contract's rules spoke of the part at a row and a column, and its parts held no such fields. The writer of the
    class's tests gave every part the two keys, the class was written to need them, and every test that arranged
    the parts as the contract lists them (the page's tests) broke on the first action.

    id: TST-CONTRACT-PART-PLACE
    Given: The contract's prompt
    When: It is read
    Then: It asks for a part that is reached by where it is to hold that place as fields of its own
    """
    path = os.path.join(os.path.dirname(pc.__file__), "..", "prompts", "product_contract.md")
    text = open(path, encoding="utf-8").read()
    assert "holds that place as fields of its own" in text


def test_an_action_says_which_stored_records_it_is_handed():
    """Verify the contract decides how an action reaches the records it depends on, so no writer invents a way.

    A rule refused a booking because another booking held the table. The class under test was one booking, and
    nothing said where the other bookings or the tables were: the code that passed the tests held the tests' own
    tables and taken hour as constants.

    id: TST-CONTRACT-WORKS-WITH
    Given: A contract with an action sent to the kind that works with its own kind and another, an action on one
           record that works with nothing, and one on one record that removes it and so works with its own kind
    When: Its action manifest is read
    Then: Each action lists the kinds it is handed and says whether it is sent to one record, its parameters are
          read from one text, every kind's fields are listed, and the schema and the prompt ask for both
    """
    manifest = _contract().action_manifest()
    by_name = {a["name"]: a for a in manifest["actions"]}

    assert by_name["create_booking"]["given"] == ["Booking", "Table"] and by_name["create_booking"]["on_kind"] is True
    assert by_name["create_booking"]["params"] == ["table_id", "guests"]
    assert by_name["expire_hold"]["given"] == [] and by_name["expire_hold"]["on_kind"] is False
    assert by_name["expire_hold"]["params"] == []
    assert by_name["mark_no_show"]["given"] == ["Booking"] and by_name["mark_no_show"]["on_kind"] is False
    assert "sent_to" in pc.CONTRACT_SCHEMA["properties"]["actions"]["items"]["properties"]
    assert {"aggregate": "Table", "fields": ["id", "seats"]} in manifest["records"]
    assert "works_with" in pc.CONTRACT_SCHEMA["properties"]["actions"]["items"]["properties"]
    path = os.path.join(os.path.dirname(pc.__file__), "..", "prompts", "product_contract.md")
    assert "`works_with`" in open(path, encoding="utf-8").read()


def test_the_contract_is_kept_with_the_build_state():
    """Verify a later change can start from the contract the app was built from (ADR-014): it is stored as it was
    answered, and read back as the typed contract.

    id: TST-CONTRACT-STORED
    Given: A build state holding a contract, and one from a build that wrote none
    When: Each is saved and read back
    Then: The first gives the same answer and the typed contract with its rules; the second gives no contract
    """
    from adapters.repository import SqliteKickstartRepository
    from domain.model import KickstartState
    repository = SqliteKickstartRepository()

    repository.save(KickstartState(contract=copy.deepcopy(CONTRACT)))
    state = repository.get()
    assert state.contract == CONTRACT
    assert [r.title for r in pc.stored_contract(state).rules] == [r["title"] for r in CONTRACT["rules"]]

    repository.save(KickstartState())
    assert repository.get().contract == {} and pc.stored_contract(repository.get()) is None


def test_a_kickstart_stores_the_contract_it_built_from(monkeypatch, tmp_path):
    """Verify the kickstart keeps the contract, not only what was read out of it.

    id: TST-CONTRACT-STORED-BY-KICKSTART
    Given: A kickstart whose front is the product contract
    When: It has run
    Then: The build state holds the contract as it was answered
    """
    from onboarding import kickstart_front as kf
    from service_layer import services
    from service_layer.unit_of_work import FakeUnitOfWork
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: json.dumps(CONTRACT))
    monkeypatch.setattr(kf, "build_front", lambda pitch, live: kf.contract_front(pitch))
    uow = FakeUnitOfWork()

    services.kickstart_domain_and_scaffold(pitch="A table booking page", uow=uow, workspace_dir=str(tmp_path))

    assert uow.kickstart.get().contract == CONTRACT


def test_a_rule_names_the_feature_it_proves_and_its_kind_follows_from_its_action():
    """Verify the rules are grouped by the product's own list of what it offers, and that the schema did not grow:
    whether a rule is of the page alone is read from its having no action, so the feature takes that key's place.

    id: TST-CONTRACT-FEATURE
    Given: The contract's schema; a contract whose rules name a feature of `has`, with and without the "(kept)"
           the list ends each entry in, one rule naming none, and no rule saying its kind
    When: The schema's rule is read, and the contract's rules and specs
    Then: A rule has a `feature` and no `kind` to write; a rule with an action is one the records obey and one
          without is of the page alone; each spec's chapter is its feature as the list names it, and "General"
          where the rule names none
    """
    rule_keys = pc.CONTRACT_SCHEMA["properties"]["rules"]["items"]["properties"]
    assert "feature" in rule_keys and "kind" not in rule_keys

    data = copy.deepcopy(CONTRACT)
    for rule, feature in zip(data["rules"], ("Pick a table", "pick a table (kept)", "")):
        del rule["kind"]
        rule["feature"] = feature
    contract = pc.ProductContract.from_dict(data)

    assert [r.kind for r in contract.rules] == ["api", "api", "page"]
    assert [s.chapter for s in contract.specs()] == ["Pick a table", "Pick a table", "General"]
    assert [s.kind for s in contract.specs()] == [SpecKind.BEHAVIOR.value, SpecKind.BEHAVIOR.value,
                                                  SpecKind.PRESENTATION.value]


def test_a_contract_stored_before_rules_named_a_feature_still_loads():
    """
    id: TST-CONTRACT-FEATURE-STORED
    Given: A stored contract whose rules say their kind and name no feature
    When: It is read
    Then: Each rule keeps the kind it was stored with, and its spec is in the chapter "General"
    """
    contract = _contract()

    assert [r.kind for r in contract.rules] == ["api", "api", "page"]
    assert {s.chapter for s in contract.specs()} == {"General"}


def test_the_features_of_a_contract_are_what_it_kept():
    """
    id: TST-CONTRACT-FEATURES
    Given: A contract that offers one thing and leaves one out
    When: Its features are read
    Then: They are the kept entries, without the mark
    """
    assert _contract().features() == ["Pick a table"]


def test_the_prompt_asks_each_rule_for_its_feature():
    """
    id: TST-CONTRACT-FEATURE-PROMPT
    Given: The contract's prompt
    When: It is read
    Then: It asks each rule for the `feature` it proves, as an entry of `has`
    """
    prompt = open(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "product_contract.md"),
                  encoding="utf-8").read()

    assert "`feature`" in prompt and "`kind`" not in prompt


def test_the_review_of_a_contracts_rules_is_shown_what_its_actions_do(monkeypatch):
    """Verify the rules of a contract are reviewed against the contract's own actions.

    id: TST-CONTRACT-REVIEW
    Given: The front of a kickstart built from a contract
    When: Its review stage is run on the rule deck
    Then: The review receives the deck and each action as the plan describes it, by name
    """
    from onboarding import kickstart_front as kf, spec_review
    monkeypatch.delenv("KICKSTART_FRONT", raising=False)
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: json.dumps(CONTRACT))
    front, seen = kf.build_front("A table booking page", live=True), {}
    monkeypatch.setattr(spec_review, "review_spec_consistency",
                        lambda specs, intent=None, actions=None: seen.update(specs=specs, actions=actions) or {"success": True, "conflicts": []})

    result = front.stage_overrides()["review"](front.inbox_specs, intent=front.intent)

    assert result == {"success": True, "conflicts": []} and seen["specs"] is front.inbox_specs
    assert list(seen["actions"]) == ["create_booking", "expire_hold", "mark_no_show"]
    assert seen["actions"]["create_booking"] == ("`create_booking(table_id: text, guests: whole_number)`: creates a "
                                                 "Booking with status confirmed")
