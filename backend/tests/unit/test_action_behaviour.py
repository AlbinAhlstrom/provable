"""The kickstart writes the methods behind the actions the page offers (backend/onboarding/action_behaviour.py).

The action protocol only names the actions. Until a method of that name exists on the aggregate, the generated API
answers every action with "Unknown action": the page looks finished and nothing on it works.
"""
import os

from onboarding.action_behaviour import action_specs, specs_of_actions
from onboarding.dynamic_test_generator import write_acceptance_suites
from onboarding.router_engine import DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton

STRUCTURE = DomainStructureSchema(domain_name="Salon", entities=[
    EntitySpec(name="Appointment", is_aggregate_root=True, attributes=[
        {"name": "id", "type": "string"}, {"name": "status", "type": "string"}]),
    EntitySpec(name="Stylist", attributes=[{"name": "id", "type": "string"}, {"name": "name", "type": "string"}]),
])

MANIFEST = {"actions": [
    {"name": "confirm_booking", "aggregate": "Appointment", "performed_by": "audience",
     "params": ["guest_name", "guest_phone"], "description": "The guest confirms the held slot with contact details"},
    {"name": "cancel_appointment", "aggregate": "Appointment", "performed_by": "audience", "params": [],
     "description": "The guest cancels the appointment"},
    {"name": "set_availability", "aggregate": "Stylist", "performed_by": "other", "params": ["available"],
     "description": "The salon marks a stylist as available or away"},
]}


def _workspace(tmp_path):
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    return str(tmp_path)


def test_every_action_is_a_spec_of_its_own():
    """Verify each action is stated on its own, so its test is written beside the others and not after them.

    id: TST-ACTB-001
    Given: The two actions the manifest gives Appointment
    When: Their specs are built
    Then: There is one per action, each targets Appointment, joins the regression suite's naming (test_spec_...),
          and states its action with its parameters and what it does
    """
    confirm, cancel = action_specs("Appointment", [a for a in MANIFEST["actions"] if a["aggregate"] == "Appointment"])
    assert (confirm.spec_id, cancel.spec_id) == ("SPEC-ACT-APPOINTMENT-CONFIRM_BOOKING", "SPEC-ACT-APPOINTMENT-CANCEL_APPOINTMENT")
    assert confirm.target_aggregate == cancel.target_aggregate == "Appointment"
    assert "confirm_booking(guest_name, guest_phone)" in confirm.given_when_then
    assert "The guest confirms the held slot with contact details" in confirm.given_when_then
    assert "cancel_appointment()" in cancel.given_when_then and "confirm_booking" not in cancel.given_when_then


def test_every_class_with_actions_gets_its_specs_and_a_run_to_fill_in(tmp_path):
    """Verify the round is handed a spec for every action, with a record of each to report on.

    id: TST-ACTB-002
    Given: A skeleton and a manifest with actions on two aggregates
    When: The specs of its actions are built
    Then: There are three specs in the manifest's order, and one open run per spec naming its aggregate
    """
    specs, runs = specs_of_actions(MANIFEST, _workspace(tmp_path))

    assert [s.target_aggregate for s in specs] == ["Appointment", "Appointment", "Stylist"]
    assert [(r["aggregate"], r["spec_id"], r["status"]) for r in runs] == [(s.target_aggregate, s.spec_id, "") for s in specs]


def test_a_product_without_actions_has_no_action_specs(tmp_path):
    """Verify nothing is asked for when the manifest offers no action.

    id: TST-ACTB-004
    Given: An empty manifest
    When: The specs of its actions are built
    Then: There is none, and no run
    """
    assert specs_of_actions({"actions": []}, _workspace(tmp_path)) == ([], [])


def test_browser_checks_stay_out_of_the_domain_regression_suite(tmp_path):
    """Verify the page's browser acceptance tests are not in the folder every domain change re-runs.

    id: TST-ACTB-005
    Given: A workspace
    When: The acceptance suites are written
    Then: The domain suite is in tests/unit and the browser suite is in tests/acceptance
    """
    written = [os.path.relpath(p, tmp_path).replace(os.sep, "/") for p in write_acceptance_suites(str(tmp_path), "Salon", [])]
    assert written == ["tests/unit/test_salon_acceptance.py", "tests/acceptance/test_salon_frontend_acceptance.py"]
    assert "run_responsive_qa_audit" in (tmp_path / "tests" / "acceptance" / "test_salon_frontend_acceptance.py").read_text(encoding="utf-8")
    assert not any("frontend" in name for name in os.listdir(tmp_path / "tests" / "unit"))


STARTING = {**MANIFEST, "starting_states": [
    {"aggregate": "Appointment", "description": "status is 'held' and no guest details are set"}]}


def test_what_a_new_object_holds_is_a_spec_of_its_own():
    """Verify the class is asked to start in the state its first action needs.

    id: TST-ACTB-START-001
    Given: A manifest that says what a newly created Appointment holds
    When: The aggregate's specs are built
    Then: The first is about an object nothing was called on, in the manifest's words
    """
    new = action_specs("Appointment", [a for a in STARTING["actions"] if a["aggregate"] == "Appointment"],
                       starting_state="status is 'held' and no guest details are set")[0]
    assert new.spec_id == "SPEC-NEW-APPOINTMENT" and "nothing is called on it" in new.given_when_then
    assert "status is 'held' and no guest details are set" in new.given_when_then


def test_the_manifests_starting_state_reaches_its_own_class_only(tmp_path):
    """Verify each aggregate is given its own starting state.

    id: TST-ACTB-START-002
    Given: A manifest with a starting state for Appointment and none for Stylist
    When: The specs of its actions are built
    Then: Appointment has a spec for a new object and Stylist has none
    """
    specs, _ = specs_of_actions(STARTING, _workspace(tmp_path))
    assert [s.spec_id for s in specs if s.spec_id.startswith("SPEC-NEW-")] == ["SPEC-NEW-APPOINTMENT"]


def test_the_rule_writers_are_told_the_starting_state_too():
    """Verify the rules' tests are written knowing what a new object holds, so they agree with the actions' test.

    id: TST-ACTB-START-003
    Given: A manifest with a starting state for Appointment
    When: The interface contract for Appointment is rendered
    Then: It states the starting state; another aggregate's contract does not
    """
    from onboarding.action_protocol import format_interface_contract
    assert "status is 'held'" in format_interface_contract(STARTING, "Appointment")
    assert "status is 'held'" not in format_interface_contract(STARTING, "Stylist")


WORDS = {**STARTING,
         "vocabulary": [{"aggregate": "Appointment", "field": "status", "values": [
             {"value": "held", "meaning": "a slot is reserved and not yet confirmed"},
             {"value": "confirmed", "meaning": "the guest gave contact details"}]}],
         "rejections": [{"aggregate": "Appointment", "error": "SlotTakenError", "raised_when": "the slot is no longer free"}]}


def test_the_shared_words_reach_every_writer_of_the_class():
    """Verify field values and refusal names are fixed once and handed to the tests' and the code's writers.

    id: TST-ACTB-WORDS-001
    Given: A manifest that fixes the values of Appointment.status and the name of its one refusal (tests written
           side by side each invented their own: one expected ValueError, another IllegalMoveError, and no code
           could satisfy both)
    When: The interface contract and the actions' specs for Appointment are rendered
    Then: All state every status value with its meaning and the refusal with its name; Stylist's contract has none
    """
    from onboarding.action_protocol import format_interface_contract
    contract = format_interface_contract(WORDS, "Appointment")
    specs = action_specs("Appointment", [a for a in WORDS["actions"] if a["aggregate"] == "Appointment"], manifest=WORDS)
    for text in [contract] + [spec.description + spec.given_when_then for spec in specs]:
        assert '"held"' in text and "a slot is reserved and not yet confirmed" in text and '"confirmed"' in text
        assert "SlotTakenError" in text and "the slot is no longer free" in text
    assert "SlotTakenError" not in format_interface_contract(WORDS, "Stylist")


def test_the_page_writer_is_given_the_field_values_too():
    """Verify the page compares a status against the value the domain stores, not one it guessed.

    id: TST-ACTB-WORDS-002
    Given: A manifest that fixes the values of Appointment.status
    When: The action protocol is rendered for the page writer
    Then: It lists the values, and not the refusal names (the page shows the refusal's message)
    """
    from onboarding.action_protocol import format_action_protocol
    text = format_action_protocol(WORDS)
    assert '"held"' in text and '"confirmed"' in text and "SlotTakenError" not in text


def test_a_state_the_class_already_starts_in_needs_no_spec(tmp_path):
    """Verify no test is asked for where there is nothing to write: such a test passes on the empty class.

    id: TST-ACTB-START-004
    Given: A manifest whose starting state for Appointment is held by the class's defaults
    When: The specs of its actions are built
    Then: There is no spec for a new Appointment, every spec has its run, and the writers are still told the state
    """
    from onboarding.action_protocol import format_interface_contract
    held = {**MANIFEST, "starting_states": [
        {"aggregate": "Appointment", "description": "status held", "held_by_defaults": True}]}

    specs, runs = specs_of_actions(held, _workspace(tmp_path))

    assert not [s.spec_id for s in specs if s.spec_id.startswith("SPEC-NEW-")]
    assert [r["spec_id"] for r in runs] == [s.spec_id for s in specs]
    assert "status held" in format_interface_contract(held, "Appointment")


def test_an_actions_spec_is_one_call_and_its_other_cases_are_the_rules():
    """Verify an action's test shows the action once: each further case in it is one more expectation that can be
    wrong, and the rules already prove those cases one by one.

    id: TST-ACTB-ONE-CALL
    Given: An action of Appointment
    When: Its spec is built
    Then: It asks for the simplest state the action is allowed in and one call, and leaves what the action refuses,
          ignores or does from another state to the rules' own tests
    """
    confirm = action_specs("Appointment", [a for a in MANIFEST["actions"] if a["aggregate"] == "Appointment"])[0]
    assert "the simplest state in which the action is allowed" in confirm.given_when_then
    assert "is called once with valid values" in confirm.given_when_then
    assert "each with a test of its own" in confirm.given_when_then
