"""
Planning a change from the Studio (ADR-014): a request in a person's words becomes the card they read before anything
is built. The card is the ticket in everyday words (its title, what was understood, each new rule as a sentence) with
what it adds to the app by name, and it says when the app cannot take the ticket. Planning changes nothing of the app.
"""
from typing import Any, Callable, Dict, List, Optional

from onboarding.change_ticket import ChangeTicket, TicketError
from onboarding.product_contract import ProductContract, stored_contract
from run_recorder import recorded
from service_layer.unit_of_work import AbstractUnitOfWork

Planner = Callable[[str, ProductContract], ChangeTicket]


def _adds(ticket: ChangeTicket, contract: ProductContract) -> List[Dict[str, str]]:
    """What the ticket adds to the app besides rules, by kind and name: what a person may open the card to see."""
    had = {action.name for action in contract.actions}
    return ([{"kind": "field", "name": f"{entry.get('record')}.{entry.get('name')}"} for entry in ticket.fields]
            + [{"kind": "changed action" if action.get("name") in had else "action", "name": str(action.get("name"))}
               for action in ticket.actions]
            + [{"kind": "refusal", "name": str(refusal.get("name"))} for refusal in ticket.refusals])


@recorded("ticket_plan", label="request")
def plan_change(request: str, uow: AbstractUnitOfWork, planner: Optional[Planner] = None) -> Dict[str, Any]:
    """Plans one request against the built app's contract and answers with its card. `problem` on the card is why the
    app cannot take the ticket as planned; a request that was not planned at all answers with `error` and no card."""
    request = request.strip()
    if not request:
        return {"success": False, "error": "Say what should change."}
    with uow:
        contract = stored_contract(uow.kickstart.get())
    if contract is None:
        return {"success": False, "error": "This app was built before changes could be planned. It can take a change "
                                           "once it is built again."}
    if planner is None:
        from onboarding.ticket_planner import plan_ticket as planner
    try:
        ticket = planner(request, contract)
    except TicketError as err:
        return {"success": False, "error": str(err)}
    problem = None
    try:
        ticket.applied_to(contract)
    except TicketError as err:
        problem = str(err)
    return {"success": True, "request": ticket.request, "title": ticket.title, "understood": ticket.understood,
            "rules": [{"title": str(rule.get("title") or ""), "plain": str(rule.get("plain") or "")}
                      for rule in ticket.rules],
            "adds": _adds(ticket, contract), "stays_green": len(ticket.stays_green(contract)), "problem": problem}
