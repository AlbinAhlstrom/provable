"""
The ticket planner: a request in a person's words becomes a change ticket of the app's contract (ADR-014).

One call. It is shown the request and the contract the app was built from, as it is stored, and answers with what the
contract gains (`change_ticket.ChangeTicket`). The answer is held to a schema made of the contract's own parts, so
what a ticket adds has the form the contract already holds it in. Whether the contract can take the ticket is decided
afterwards by code (`ChangeTicket.applied_to`); a ticket that was not delivered fails with the reason and nothing is
asked again.
"""

from typing import Any, Dict

import agent_orchestrator
from onboarding.change_ticket import ChangeTicket, TicketError
from onboarding.product_contract import CONTRACT_SCHEMA, ProductContract, to_json
from pipeline_trace import traced

STAGE = "change_ticket"
# Seconds the call may take: it reads a whole contract and thinks before it writes, as the contract's call does
PLAN_TIMEOUT_S = 180.0

_TEXT = {"type": "string"}
_CONTRACT = CONTRACT_SCHEMA["properties"]
_FIELD = _CONTRACT["records"]["items"]["properties"]["fields"]["items"]["properties"]


def _object(**properties: Any) -> Dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(properties)}


TICKET_SCHEMA: Dict[str, Any] = _object(
    title=_TEXT, understood=_TEXT, decided={"type": "array", "items": _TEXT},
    fields={"type": "array", "items": _object(record=_TEXT, **_FIELD)},
    actions=_CONTRACT["actions"], situations=_CONTRACT["situations"], refusals=_CONTRACT["refusals"],
    read_out=_CONTRACT["read_out"], rules=_CONTRACT["rules"],
)


@traced("ticket.plan")
def plan_ticket(request: str, contract: ProductContract) -> ChangeTicket:
    """Plans a request against an app's contract with one LLM call. Raises TicketError on any failure."""
    request = request.strip()
    prompt = agent_orchestrator.load_prompt("change_ticket.md", {"request": request, "contract": to_json(contract)})
    raw = agent_orchestrator.call_gemini(prompt, stage=STAGE, json_mode=True, json_schema=TICKET_SCHEMA,
                                         timeout_s=PLAN_TIMEOUT_S)
    if not raw or not raw.strip():
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        raise TicketError(f"The change was not planned: {reason}")
    try:
        data = agent_orchestrator.extract_json_object(raw)
    except Exception as exc:
        raise TicketError(f"The planned change is not valid JSON: {exc}") from exc
    return ChangeTicket.from_dict(data, request=request)
