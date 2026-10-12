"""The ticket planner: a request in a person's words becomes a change ticket of the app's contract (ADR-014)."""
import copy
import json

import pytest

import agent_orchestrator
import llm_provider
from onboarding import change_ticket as ct
from onboarding import product_contract as pc
from onboarding import ticket_planner as tp
from test_change_ticket import TICKET
from test_product_contract import CONTRACT


def _contract() -> pc.ProductContract:
    return pc.ProductContract.from_dict(copy.deepcopy(CONTRACT))


def test_a_request_is_planned_in_one_call_that_reads_the_contract(monkeypatch):
    """Verify the planner is shown the app as its contract says it and answers with a ticket the contract takes.

    id: TST-TICKET-PLAN
    Given: A model that answers with a ticket
    When: A request is planned against an app's contract
    Then: One call is made for the stage `change_ticket`, with the request and the contract as it is stored in its
          prompt and the ticket's schema; the answer is the typed ticket with the person's words, and it applies
    """
    seen = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini",
                        lambda prompt, stage="general", **k: seen.append((prompt, stage, k)) or json.dumps(TICKET))

    ticket = tp.plan_ticket("  let guests leave a note ", _contract())

    (prompt, stage, options), = seen
    assert stage == "change_ticket" and '"let guests leave a note"' in prompt
    assert pc.to_json(_contract()) in prompt
    assert options["json_schema"] is tp.TICKET_SCHEMA and options["timeout_s"] > agent_orchestrator.DEFAULT_TIMEOUT_S
    assert (ticket.request, ticket.title) == ("let guests leave a note", "Guests can leave a note")
    assert ticket.applied_to(_contract()).rules[-1].title == "A booking takes a note"


def test_a_ticket_that_was_not_delivered_fails_with_the_reason(monkeypatch):
    """
    id: TST-TICKET-PLAN-FAILS
    Given: A provider that answers nothing, and one that answers with something that is no JSON object
    When: A request is planned
    Then: Each fails by name with the reason, and nothing is asked again
    """
    calls = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: calls.append(1) or "")
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", "APITimeoutError: timed out", raising=False)
    with pytest.raises(ct.TicketError, match="APITimeoutError"):
        tp.plan_ticket("let guests leave a note", _contract())

    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **k: calls.append(1) or "a note")
    with pytest.raises(ct.TicketError, match="not valid JSON"):
        tp.plan_ticket("let guests leave a note", _contract())
    assert len(calls) == 2


def test_a_ticket_is_written_in_the_form_of_the_contract():
    """Verify what a ticket adds has the form the contract holds it in, so that applying it is appending it: the
    ticket's schema is made of the contract's own parts and cannot drift from them.

    id: TST-TICKET-SCHEMA
    Given: The ticket's schema and the contract's
    When: Their parts are compared
    Then: An action, a refusal and a rule are the contract's own; a field is the contract's with the record it is
          added to; every key is required; and the whole is inside what the provider compiles
    """
    ticket, contract = tp.TICKET_SCHEMA["properties"], pc.CONTRACT_SCHEMA["properties"]
    for part in ("actions", "refusals", "rules", "situations", "read_out"):
        assert ticket[part] is contract[part]
    field_of_contract = contract["records"]["items"]["properties"]["fields"]["items"]["properties"]
    assert ticket["fields"]["items"]["properties"] == {"record": {"type": "string"}, **field_of_contract}

    def objects(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                yield node
            for value in node.values():
                yield from objects(value)

    def weight(node):
        if not isinstance(node, dict):
            return 0
        own = len(node.get("properties", {})) + (1 if node.get("type") == "array" else 0)
        return own + sum(weight(child) for child in list(node.get("properties", {}).values()) + [node.get("items")])

    assert ticket["decided"] == {"type": "array", "items": {"type": "string"}}
    for node in objects(tp.TICKET_SCHEMA):
        assert sorted(node["required"]) == sorted(node["properties"])
    assert weight(tp.TICKET_SCHEMA) <= pc.SCHEMA_WEIGHT_LIMIT


def test_the_planner_runs_on_the_middle_model(monkeypatch):
    """Verify the one call a change is built on runs where the contract does.

    id: TST-TICKET-MODEL
    Given: The Anthropic provider
    When: The connection of the planner's stage is asked for
    Then: It is the model the contract is written on
    """
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("LLM_MODEL_CHANGE_TICKET", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    assert llm_provider.connection("change_ticket").model == llm_provider.connection("product_contract").model
