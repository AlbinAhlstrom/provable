"""Planning a change from the Studio: a request becomes the card a person reads before anything is built (ADR-014)."""
import copy

from fastapi.testclient import TestClient

from onboarding import change_ticket as ct
from service_layer import change_tickets
from service_layer.unit_of_work import FakeUnitOfWork
from test_change_ticket import TICKET
from test_product_contract import CONTRACT


def _app(contract=CONTRACT) -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    state = uow.kickstart.get()
    state.contract = copy.deepcopy(contract) if contract else {}
    uow.kickstart.save(state)
    return uow


class _Planner:
    def __init__(self, answer=TICKET, error=None):
        self.calls, self.answer, self.error = [], answer, error

    def __call__(self, request, contract):
        self.calls.append((request, contract))
        if self.error:
            raise ct.TicketError(self.error)
        return ct.ChangeTicket.from_dict(copy.deepcopy(self.answer), request=request)


def test_a_planned_request_is_a_card_in_the_persons_words():
    """
    id: TST-TICKET-CARD
    Given: A built app with a stored contract of three rules, and a planner that answers with a ticket of one rule
    When: A request is planned
    Then: The planner is given the request and the app's contract once, and the card holds the title, what was
          understood, each new rule by its title and its sentence, what the ticket adds by kind and name, and how many
          rules will be checked too; nothing of the app is changed
    """
    uow, planner = _app(), _Planner()

    card = change_tickets.plan_change("  let guests leave a note ", uow=uow, planner=planner)

    assert len(planner.calls) == 1 and planner.calls[0][0] == "let guests leave a note"
    assert [r.title for r in planner.calls[0][1].rules] == [r["title"] for r in CONTRACT["rules"]]
    assert card["success"] is True and card["problem"] is None
    assert (card["request"], card["title"]) == ("let guests leave a note", "Guests can leave a note")
    assert card["understood"] == TICKET["understood"]
    assert card["rules"] == [{"title": "A booking takes a note",
                              "plain": "Given a booked table, When the guest writes a note, Then the booking shows it"}]
    assert card["stays_green"] == 3
    assert card["adds"] == [{"kind": "field", "name": "Booking.note"}, {"kind": "action", "name": "add_note"},
                            {"kind": "refusal", "name": "NoteTooLongError"}]
    assert uow.kickstart.get().contract == CONTRACT


def test_an_action_the_app_has_is_shown_as_changed():
    """
    id: TST-TICKET-CARD-CHANGED-ACTION
    Given: A ticket whose action is one the app already has, with a parameter added
    When: The request is planned
    Then: The card names it as a changed action, not as a new one
    """
    grown = {**CONTRACT["actions"][0], "params": "table_id: text, guests: whole_number, note: text"}
    rule = {**TICKET["rules"][0], "action": "create_booking", "given": "two_tables_free"}
    planner = _Planner({**TICKET, "actions": [grown], "refusals": [], "rules": [rule]})

    card = change_tickets.plan_change("a note on the form", uow=_app(), planner=planner)

    assert {"kind": "changed action", "name": "create_booking"} in card["adds"]


def test_a_ticket_the_app_cannot_take_is_shown_with_the_reason():
    """Verify the person sees what was planned and why it cannot be built, in place of an error with nothing to read.

    id: TST-TICKET-CARD-PROBLEM
    Given: A planner whose ticket names a record the app does not have
    When: The request is planned
    Then: The card is returned with the rules, and its problem names what is wrong
    """
    planner = _Planner({**TICKET, "fields": [{**TICKET["fields"][0], "record": "Guest"}]})

    card = change_tickets.plan_change("let guests leave a note", uow=_app(), planner=planner)

    assert card["success"] is True and "'Guest'" in card["problem"]
    assert card["rules"][0]["title"] == "A booking takes a note"


def test_a_request_that_was_not_planned_fails_with_the_reason():
    """
    id: TST-TICKET-CARD-FAILS
    Given: An app built without a stored contract; an empty request; a planner that fails
    When: Each is planned
    Then: Each answers with no card and a reason, and the planner is only called where there is something to plan
    """
    planner = _Planner()
    no_contract = change_tickets.plan_change("let guests leave a note", uow=_app(contract=None), planner=planner)
    empty = change_tickets.plan_change("   ", uow=_app(), planner=planner)
    failed = change_tickets.plan_change("let guests leave a note", uow=_app(),
                                        planner=_Planner(error="The change was not planned: quota"))

    assert planner.calls == []
    assert no_contract["success"] is False and "built again" in no_contract["error"]
    assert empty["success"] is False and "what should change" in empty["error"].lower()
    assert failed == {"success": False, "error": "The change was not planned: quota"}


def test_the_studio_plans_a_change_over_the_api(monkeypatch):
    """
    id: TST-TICKET-PLAN-API
    Given: The engine API, with the planning use case replaced
    When: A request is posted to /api/tickets/plan
    Then: The use case is given the request, and its card is the answer
    """
    from app import app
    seen = []
    monkeypatch.setattr("entrypoints.routers.tickets.change_tickets.plan_change",
                        lambda request, uow: seen.append(request) or {"success": True, "title": "A note"})

    answer = TestClient(app).post("/api/tickets/plan", json={"request": "let guests leave a note"})

    assert answer.status_code == 200 and answer.json() == {"success": True, "title": "A note"}
    assert seen == ["let guests leave a note"]
