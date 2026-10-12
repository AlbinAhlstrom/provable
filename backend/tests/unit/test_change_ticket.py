"""A change ticket: one change to a built app, as a delta of its product contract (ADR-014)."""
import copy

import pytest

from onboarding import change_ticket as ct
from onboarding import product_contract as pc
from test_product_contract import CONTRACT

NOTE = {"name": "note", "part_of": "", "type": "text", "starts_as": "", "holds": "what the guest asked for",
        "values": [], "part_name": ""}
TICKET = {
    "title": "Guests can leave a note",
    "understood": "A guest can add a short note to a booking.",
    "decided": ["A note is at most 200 characters.", "The note is shown on the booking."],
    "fields": [{"record": "Booking", **NOTE}],
    "actions": [{"name": "add_note", "record": "Booking", "performed_by": "audience", "params": "note: text",
                 "sent_to": "one_record", "trigger": "Note field, type and press \"Save note\"",
                 "does": "sets note", "works_with": ""}],
    "situations": ["table_1_noted = the first table is booked with a note: as table_1_taken, and note \"window seat\""],
    "refusals": [{"name": "NoteTooLongError", "action": "add_note", "raised_when": "note is longer than 200 characters",
                  "sentence": "Keep the note under 200 characters.", "appears": "under the note field"}],
    "read_out": ["Note · text · \"{note}\""],
    "rules": [{"kind": "api", "title": "A booking takes a note", "action": "add_note", "given": "table_1_taken",
               "when": "add_note(note \"window seat\")", "then": "note is \"window seat\"",
               "sees": "\"window seat\"",
               "plain": "Given a booked table, When the guest writes a note, Then the booking shows it"}],
}


def _contract() -> pc.ProductContract:
    return pc.ProductContract.from_dict(copy.deepcopy(CONTRACT))


def _ticket(**changes) -> ct.ChangeTicket:
    return ct.ChangeTicket.from_dict({**copy.deepcopy(TICKET), **changes}, request="let guests leave a note")


def test_a_ticket_applied_is_the_contract_with_what_it_adds():
    """Verify a change is a change of the one contract and never a second description of the app.

    id: TST-TICKET-APPLIED
    Given: A contract, and a ticket that adds a field, an action, a situation, a refusal, a read-out name and a rule
    When: The ticket is applied
    Then: The contract after holds everything it held, in the same order, with the additions after it; the
          contract before is untouched; and the new rule is read out as a spec like any other
    """
    before = _contract()

    after = _ticket().applied_to(before)

    assert [f.name for f in after.records[0].fields] == [f.name for f in before.records[0].fields] + ["note"]
    assert [a.name for a in after.actions] == [a.name for a in before.actions] + ["add_note"]
    assert [r.title for r in after.rules] == [r.title for r in before.rules] + ["A booking takes a note"]
    assert after.situations[:2] == before.situations and len(after.situations) == 3
    assert after.refusals[-1].name == "NoteTooLongError" and after.read_out[-1].startswith("Note")
    assert "note" not in [f.name for f in before.records[0].fields] and before.source == CONTRACT
    new = after.specs()[-1]
    assert (new.spec_id, new.action, new.target_aggregate) == ("SPEC-004", "add_note", "Booking")
    assert new.situation.startswith("`table_1_taken`")
    assert pc.ProductContract.from_dict(after.source).rules[-1].title == "A booking takes a note"


def test_the_rules_a_ticket_leaves_alone_are_the_ones_that_must_stay_green():
    """
    id: TST-TICKET-STAYS-GREEN
    Given: A contract with three rules and a ticket that adds one
    When: The ticket is asked which rules must stay green
    Then: They are the three the contract already had
    """
    assert _ticket().stays_green(_contract()) == [rule["title"] for rule in CONTRACT["rules"]]


def test_an_action_the_app_has_can_gain_a_parameter():
    """Verify a change done through an action the app already has is that action with more to say, not a second
    action beside it: what a person adds to a form they already fill in is sent with the form.

    id: TST-TICKET-ACTION-GAINS
    Given: A ticket whose action has the name of one the contract holds, with every parameter it had and one more
    When: The ticket is applied
    Then: The contract after holds that action once, in its place, as the ticket wrote it
    """
    before = _contract()
    grown = {**CONTRACT["actions"][0], "params": "table_id: text, guests: whole_number, note: text",
             "does": "creates a Booking with status confirmed and the note"}
    rule = {**TICKET["rules"][0], "action": "create_booking", "given": "two_tables_free",
            "when": "create_booking(table_id of Table 1, guests 2, note \"window seat\")"}

    after = _ticket(actions=[grown], refusals=[], rules=[rule]).applied_to(before)

    assert [a.name for a in after.actions] == [a.name for a in before.actions]
    assert after.actions[0].params == ["table_id: text", "guests: whole_number", "note: text"]
    assert after.actions[0].does.endswith("and the note") and before.actions[0].params[-1] == "guests: whole_number"


@pytest.mark.parametrize("changes, reason", [
    ({"rules": []}, "adds no rule"),
    ({"title": " "}, "title"),
    ({"fields": [{"record": "Guest", **NOTE}]}, "'Guest'"),
    ({"fields": [{"record": "Booking", **{**NOTE, "name": "guests"}}]}, "already has a field 'guests'"),
    ({"fields": [{"record": "Booking", **{**NOTE, "type": "whole_number", "starts_as": "as many as the table seats"}}]},
     "starting value"),
    ({"actions": [{**CONTRACT["actions"][0], "params": "guests: whole_number, note: text"}]}, "'table_id'"),
    ({"actions": [{**CONTRACT["actions"][0], "sent_to": "one_record"}]}, "sent"),
    ({"actions": [{**TICKET["actions"][0], "record": "Guest"}]}, "'Guest'"),
    ({"rules": [{**TICKET["rules"][0], "title": "No more than eight guests"}]}, "already has a rule"),
    ({"rules": [{**TICKET["rules"][0], "action": "remove_note"}]}, "'remove_note'"),
    ({"rules": [{**TICKET["rules"][0], "given": "a booked table"}]}, "situation"),
    ({"refusals": [{**TICKET["refusals"][0], "action": "remove_note"}]}, "'remove_note'"),
])
def test_a_ticket_the_contract_cannot_take_is_refused_by_name(changes, reason):
    """Verify nothing is built from a ticket that names what the contract after it does not hold, or that would
    leave a saved record without a value.

    id: TST-TICKET-REFUSED
    Given: A ticket with one thing wrong
    When: It is applied
    Then: It is refused with a reason that names the thing, and the contract is untouched
    """
    before = _contract()

    with pytest.raises(ct.TicketError, match=reason):
        _ticket(**changes).applied_to(before)

    assert before.source == CONTRACT
