"""The kickstart writes the methods behind the actions the page offers (backend/onboarding/action_behaviour.py).

The action protocol only names the actions. Until a method of that name exists on the aggregate, the generated API
answers every action with "Unknown action": the page looks finished and nothing on it works.
"""
import os

from onboarding.action_behaviour import ActionBehaviour, action_spec, implement_actions
from onboarding.dynamic_test_generator import write_acceptance_suites
from onboarding.router_engine import BusinessSpec, DomainStructureSchema, EntitySpec
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


def _writes_methods(*names_by_aggregate):
    """A stand-in for the TDD loop that appends the given methods to the aggregate's class, as GREEN would."""
    wanted = dict(names_by_aggregate)
    specs = []

    def run_spec(spec, workspace_dir, action_manifest=None):
        specs.append(spec)
        path = os.path.join(workspace_dir, "src", "domain", f"{spec.target_aggregate.lower()}.py")
        with open(path, "a", encoding="utf-8") as f:
            for name in wanted.get(spec.target_aggregate, []):
                f.write(f"\n    def {name}(self, **params):\n        self.status = '{name}'\n")
        return {"success": True, "status": "FULFILLED", "attempts": [{"attempt": 1, "approved": True}]}

    run_spec.specs = specs
    return run_spec


def test_one_spec_per_aggregate_states_every_action_it_must_carry_out():
    """Verify the spec handed to the TDD loop names each action with its parameters and what it does.

    id: TST-ACTB-001
    Given: The two actions the manifest gives Appointment
    When: Their spec is built
    Then: It targets Appointment, joins the regression suite's naming (test_spec_...), and states both actions
    """
    spec = action_spec("Appointment", [a for a in MANIFEST["actions"] if a["aggregate"] == "Appointment"])
    assert spec.target_aggregate == "Appointment" and spec.spec_id == "SPEC-ACT-APPOINTMENT"
    text = spec.given_when_then
    assert "confirm_booking(guest_name, guest_phone)" in text and "cancel_appointment()" in text
    assert "The guest confirms the held slot with contact details" in text


def test_every_aggregate_with_actions_gets_its_methods_and_the_contract_holds(tmp_path):
    """Verify the stage runs the TDD loop once per aggregate and then checks the code against the manifest.

    id: TST-ACTB-002
    Given: A skeleton, a manifest with actions on two aggregates, and a loop that writes all of their methods
    When: The actions are implemented
    Then: The loop ran once per aggregate with the manifest, every action is implemented and nothing is missing
    """
    run_spec = _writes_methods(("Appointment", ["confirm_booking", "cancel_appointment"]), ("Stylist", ["set_availability"]))
    result = implement_actions(MANIFEST, _workspace(tmp_path), run_spec=run_spec)

    assert isinstance(result, ActionBehaviour) and result.success and result.error == ""
    assert [s.target_aggregate for s in run_spec.specs] == ["Appointment", "Stylist"]
    assert sorted(result.implemented) == ["cancel_appointment", "confirm_booking", "set_availability"]
    assert result.missing == []


def test_an_action_left_without_a_method_fails_the_stage_by_name(tmp_path):
    """Verify a page action nothing implements is reported, with the loop's own reason, instead of passing silently.

    id: TST-ACTB-003
    Given: A loop that dead-ends on Appointment and writes only one of its two methods for nobody
    When: The actions are implemented
    Then: The result is not a success, names the missing actions and carries why the loop stopped
    """
    def run_spec(spec, workspace_dir, action_manifest=None):
        if spec.target_aggregate == "Appointment":
            return {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "error": "assert status == 'Confirmed'",
                    "attempts": [{"attempt": 1, "approved": False}, {"attempt": 2, "approved": False}]}
        return _writes_methods(("Stylist", ["set_availability"]))(spec, workspace_dir, action_manifest)

    result = implement_actions(MANIFEST, _workspace(tmp_path), run_spec=run_spec)

    assert not result.success
    assert [m["action"] for m in result.missing] == ["confirm_booking", "cancel_appointment"]
    assert "confirm_booking" in result.error and "assert status == 'Confirmed'" in result.error
    assert result.implemented == ["set_availability"]


def test_a_product_without_actions_needs_no_behaviour(tmp_path):
    """Verify nothing runs when the manifest offers no action.

    id: TST-ACTB-004
    Given: An empty manifest
    When: The actions are implemented
    Then: The loop is never called and the result says why it was skipped
    """
    run_spec = _writes_methods()
    result = implement_actions({"actions": []}, _workspace(tmp_path), run_spec=run_spec)
    assert result.success and result.skipped and run_spec.specs == []


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


def test_the_spec_states_what_a_new_object_holds_before_any_action():
    """Verify the class is asked to start in the state its first action needs.

    id: TST-ACTB-START-001
    Given: A manifest that says what a newly created Appointment holds
    When: The aggregate's spec is built
    Then: The spec has a scenario for an object created with only its required fields, in the manifest's words
    """
    spec = action_spec("Appointment", [a for a in STARTING["actions"] if a["aggregate"] == "Appointment"],
                       starting_state="status is 'held' and no guest details are set")
    assert "created with only its required fields" in spec.given_when_then
    assert "status is 'held' and no guest details are set" in spec.given_when_then


def test_the_manifests_starting_state_reaches_the_aggregates_spec(tmp_path):
    """Verify implement_actions hands each aggregate its own starting state.

    id: TST-ACTB-START-002
    Given: A manifest with a starting state for Appointment and none for Stylist
    When: The actions are implemented
    Then: Appointment's spec carries the starting state and Stylist's spec has no such scenario
    """
    run_spec = _writes_methods(("Appointment", ["confirm_booking", "cancel_appointment"]), ("Stylist", ["set_availability"]))
    implement_actions(STARTING, _workspace(tmp_path), run_spec=run_spec)
    by_aggregate = {s.target_aggregate: s.given_when_then for s in run_spec.specs}
    assert "status is 'held'" in by_aggregate["Appointment"]
    assert "created with only its required fields" not in by_aggregate["Stylist"]


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
    When: The interface contract and the actions' spec for Appointment are rendered
    Then: Both state every status value with its meaning and the refusal with its name; Stylist's contract has none
    """
    from onboarding.action_protocol import format_interface_contract
    contract = format_interface_contract(WORDS, "Appointment")
    spec = action_spec("Appointment", [a for a in WORDS["actions"] if a["aggregate"] == "Appointment"], manifest=WORDS)
    for text in (contract, spec.description + spec.given_when_then):
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


def test_the_actions_spec_goes_through_the_loop_that_can_reconsider_a_test(tmp_path, monkeypatch):
    """Verify the actions' spec is executed by the batch, whose test writer may correct a test no code could meet.

    id: TST-ACTB-RECONSIDER
    Given: No executor injected (a kickstart), and a batch executor that records what it is given (the actions'
           test once read a field under a misspelt name; two code answers could not satisfy it, the stage failed,
           and the build had no domain at all)
    When: The actions are implemented
    Then: Each aggregate's spec was executed through the batch, on its own, with the manifest
    """
    from service_layer import tdd_batch
    seen = []

    decks = []

    def together(specs, workspace_dir, action_manifest=None, on_result=None, deck=None):
        decks.append([s.spec_id for s in deck])
        seen.append(([s.spec_id for s in specs], action_manifest is MANIFEST))
        return {s.spec_id: {"success": True, "status": "FULFILLED", "attempts": []} for s in specs}

    monkeypatch.setattr(tdd_batch, "execute_specs_together", together)
    rule = BusinessSpec(spec_id="SPEC-001", title="t", description="d", given_when_then="g", target_aggregate="Appointment")
    result = implement_actions(MANIFEST, _workspace(tmp_path), rules=[rule])
    assert seen == [(["SPEC-ACT-APPOINTMENT"], True), (["SPEC-ACT-STYLIST"], True)]
    assert decks[0] == ["SPEC-ACT-APPOINTMENT", "SPEC-001"]  # the test writer is shown the rules that come next
    assert [r["status"] for r in result.runs] == ["FULFILLED", "FULFILLED"]
