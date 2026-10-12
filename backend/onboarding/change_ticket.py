"""
A change ticket: one change to a built app, as a delta of its product contract (ADR-014).

An app is built from its contract (`product_contract.py`, ADR-011), so a change of the app is a change of the
contract. A ticket names what is added, in the contract's own form, and the contract after the ticket is the contract
before it with that appended: nothing the app already has is restated, so the two cannot disagree. The builders are
then given the contract after, and the rules the ticket left alone are the ones that must still be green.

So far a ticket only adds: a field, an action, a parameter of an action the app has, a rule. A saved record must stay
valid without being rewritten, so a field it adds is one the class's default is enough for. Changing or retiring a rule waits for rules to have an identity of their own: a
spec's id is its place in the contract (`ProductContract.specs`), and taking one out would rename every later one.
"""

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List

from onboarding.product_contract import ContractError, Field, ProductContract


def _params(action: Dict[str, Any]) -> List[str]:
    return [entry.strip() for entry in str(action.get("params") or "").split(",") if entry.strip()]


def _check_grown(had: Dict[str, Any], has: Dict[str, Any]) -> None:
    """An action the app already has may gain parameters and do more. The rules that send it today must still be
    able to: it goes to the same record in the same way and keeps every parameter it had."""
    for key in ("record", "sent_to"):
        if had.get(key) != has.get(key):
            raise TicketError(f"Action '{has['name']}' is sent differently after the ticket ({key}: '{had.get(key)}' "
                              f"became '{has.get(key)}'), so the rules that send it today could not.")
    for param in _params(had):
        if param not in _params(has):
            raise TicketError(f"Action '{has['name']}' no longer takes '{param.split(':')[0].strip()}', "
                              f"which the rules that send it today give it.")


class TicketError(ValueError):
    """The ticket cannot be applied to the contract. The reason names what is wrong; nothing is built from it."""


@dataclass
class ChangeTicket:
    request: str                 # the person's own words
    title: str
    understood: str              # the request as the planner read it: one short paragraph the person can correct
    rules: List[Dict[str, Any]]  # each in the contract's form of a rule
    fields: List[Dict[str, Any]] = field(default_factory=list)   # the contract's form of a field, with its `record`
    actions: List[Dict[str, Any]] = field(default_factory=list)
    situations: List[str] = field(default_factory=list)
    refusals: List[Dict[str, Any]] = field(default_factory=list)
    read_out: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], request: str) -> "ChangeTicket":
        return cls(request=request, title=str(data.get("title") or ""), understood=str(data.get("understood") or ""),
                   rules=[dict(r) for r in data.get("rules") or []], fields=[dict(f) for f in data.get("fields") or []],
                   actions=[dict(a) for a in data.get("actions") or []],
                   situations=[str(s) for s in data.get("situations") or []],
                   refusals=[dict(r) for r in data.get("refusals") or []],
                   read_out=[str(r) for r in data.get("read_out") or []])

    def stays_green(self, contract: ProductContract) -> List[str]:
        """The rules the ticket leaves alone, by title: each must be as green after the build as before it."""
        return [rule.title for rule in contract.rules]

    def applied_to(self, contract: ProductContract) -> ProductContract:
        """The contract after the ticket. Raises TicketError naming the first thing the contract cannot take;
        the contract given is never changed."""
        if not self.title.strip():
            raise TicketError("The ticket has no title.")
        if not self.rules:
            raise TicketError("The ticket adds no rule, so nothing would prove the change.")
        after = copy.deepcopy(contract.source)
        records = {record["name"]: record for record in after["records"]}

        for entry in self.fields:
            added = {key: value for key, value in entry.items() if key != "record"}
            record = records.get(entry.get("record"))
            if record is None:
                raise TicketError(f"Field '{added.get('name')}' is of '{entry.get('record')}', which is no record of the app.")
            if any(existing["name"] == added["name"] for existing in record["fields"]):
                raise TicketError(f"{record['name']} already has a field '{added['name']}'.")
            if not Field.from_dict(added).starts_by_default():
                raise TicketError(f"Field '{added['name']}' has no plain starting value ('{added.get('starts_as')}'), "
                                  f"so the {record['name']} records already saved would be left without one.")
            record["fields"].append(added)

        for action in self.actions:
            if action.get("record") not in records:
                raise TicketError(f"Action '{action['name']}' is sent to '{action.get('record')}', which is no record of the app.")
            place = next((n for n, existing in enumerate(after["actions"]) if existing["name"] == action["name"]), None)
            if place is None:
                after["actions"].append(action)
            else:
                _check_grown(after["actions"][place], action)
                after["actions"][place] = action
        actions = {action["name"] for action in after["actions"]}

        for refusal in self.refusals:
            if refusal.get("action") not in actions:
                raise TicketError(f"Refusal '{refusal.get('name')}' is of '{refusal.get('action')}', which is no action of the app.")
        after["refusals"] = list(after.get("refusals") or []) + self.refusals
        after["situations"] = list(after.get("situations") or []) + self.situations
        after["read_out"] = list(after.get("read_out") or []) + self.read_out

        for rule in self.rules:
            if any(existing["title"] == rule.get("title") for existing in after["rules"]):
                raise TicketError(f"The app already has a rule '{rule.get('title')}'.")
            if rule.get("action") and rule["action"] not in actions:
                raise TicketError(f"Rule '{rule.get('title')}' is about '{rule['action']}', which is no action of the app.")
            after["rules"].append(rule)

        try:
            result = ProductContract.from_dict(after)
        except ContractError as err:
            raise TicketError(f"The contract after the ticket is no contract: {err}") from err
        for spec in result.specs()[len(contract.rules):]:
            if not spec.situation:
                raise TicketError(f"Rule '{spec.title}' starts from no situation the app has: its Given must name one.")
        return result
