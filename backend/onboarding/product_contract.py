"""The product contract: one answer that says what is built, which every later stage is derived from (ADR-011).

A kickstart used to open with five model calls in a row (intent, expansion, decomposition, action protocol, UX
plan). Each re-read the one before and was free to name things its own way, and nothing fixed the fields a class
holds before the page was written against them. The contract is one call that names the records and their fields,
the actions, the refusals, the rules, the look and the names the page is read out by. What the later stages need
(the domain structure, the rule deck, the action manifest, the intent, the page's blueprint) is read out of it here
by code, so the builders that start from it side by side cannot disagree.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import agent_orchestrator
from onboarding.intent import PRODUCT_TYPES, ProductIntent
from onboarding.router_engine import (AttributeSpec, AudienceRole, BusinessSpec, DomainStructureSchema, EntitySpec,
                                      SpecKind)
from pipeline_trace import traced

STAGE = "product_contract"
# Seconds the call may take: some 4,000 to 6,000 tokens, half a minute on the model it runs on and well past the
# 60 s of an ordinary call on a slower one.
CONTRACT_TIMEOUT_S = 180.0

# The contract's field types, and the type each is to the skeleton
FIELD_TYPES = {"text": "string", "whole_number": "int", "decimal_number": "float", "boolean": "boolean",
               "date": "string", "time": "string", "moment": "string", "one_of": "string", "list_of_text": "list"}
PARTS = "list_of_parts"
# The one way a point in time is written as text. Three writers meet in such a field (tests, code, page), and a
# moment written with its offset by one and without by another cannot be compared.
FORMS = {"date": 'a date as text, like "2030-01-31"', "time": 'a time of day as text, like "09:30"',
         "moment": 'a moment as text with its UTC offset, like "2030-01-31T09:30:00+00:00"'}
NOTHING = ("", "none", "empty", "null")   # a `starts_as` that names no starting value
# Who makes a record: a person, with the page (an order, a booking); the page by itself when it opens and finds
# none (a round of a game, a draft); or nobody, it is there from the start (a menu, a price list)
CREATED, OPENED, FROM_START = "created_by_person", "created_on_opening", "exists_from_start"
ORIGINS = {CREATED: "a person creates it with the page", OPENED: "the page creates one when it opens and none exists",
           FROM_START: "exists from the start"}
API_RULE, PAGE_RULE = "api", "page"
AUDIENCE, AUTOMATIC, OTHER = "audience", "automatic", "other"
# What an action is sent to: one record of its kind, or the kind (it makes a record, or goes through them all)
ONE_RECORD, THE_KIND = "one_record", "the_kind"
LEFT_OUT = "(left out"

_TEXT = {"type": "string"}
_TEXTS = {"type": "array", "items": _TEXT}


def _object(**properties: Any) -> Dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(properties)}


def _list(item: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "array", "items": item}


def _one_of(*values: str) -> Dict[str, Any]:
    return {"type": "string", "enum": list(values)}


# The provider compiles the schema into a grammar and refuses one that is too large, before a token is written. Measured
# on shapes of this contract: a schema is accepted while its properties and its lists together count no more than this.
# So what code reads as structure is held by the schema, what is read as words is a text or a list of texts, and what
# one part of a list holds is a field of the same list (`part_of`) rather than an object nested inside it.
# The count is a guide and not the provider's own measure: a shape counting 66 was accepted, and another counting 66
# (one more list of texts, two integers fewer) was refused until any one property was taken out. 65 is the largest
# count no shape was refused at; a new shape is still tried against the provider before it is relied on.
SCHEMA_WEIGHT_LIMIT = 65

_FIELD = _object(name=_TEXT, part_of=_TEXT, type=_one_of(*FIELD_TYPES, PARTS), starts_as=_TEXT, holds=_TEXT,
                 values=_TEXTS, part_name=_TEXT)
CONTRACT_SCHEMA: Dict[str, Any] = _object(
    product=_object(name=_TEXT, product_type=_TEXT, audience=_TEXT, loop=_TEXT, has=_TEXTS),
    look=_object(summary=_TEXT, tokens=_TEXT, palette=_TEXT, parts=_TEXTS, narrow=_TEXT, grid=_TEXT),
    opening=_TEXT,
    records=_list(_object(name=_TEXT, origin=_one_of(CREATED, OPENED, FROM_START), fields=_list(_FIELD), shown=_TEXTS,
                          starting_records=_TEXT)),
    fixed=_TEXT,
    actions=_list(_object(name=_TEXT, record=_TEXT, sent_to=_one_of(ONE_RECORD, THE_KIND),
                          performed_by=_one_of(AUDIENCE, AUTOMATIC, OTHER), params=_TEXT, trigger=_TEXT, does=_TEXT,
                          works_with=_TEXT)),
    read_out=_TEXTS,
    situations=_TEXTS,
    refusals=_list(_object(name=_TEXT, action=_TEXT, raised_when=_TEXT, sentence=_TEXT, appears=_TEXT)),
    rules=_list(_object(kind=_one_of(API_RULE, PAGE_RULE), title=_TEXT, action=_TEXT, given=_TEXT, when=_TEXT,
                        then=_TEXT, sees=_TEXT, plain=_TEXT)),
)


class ContractError(RuntimeError):
    """The contract was not delivered (provider error, an answer that is no contract). Nothing is built on a guess."""


@dataclass
class Field:
    name: str
    type: str = "text"
    starts_as: str = ""                    # for a list of parts: how many there are from the moment the record exists
    holds: str = ""
    values: List[str] = field(default_factory=list)   # each as `value: meaning; shown as "wording"`
    part_name: str = ""
    part_of: str = ""                      # the list of parts this field is one part's field of
    part_fields: List["Field"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Field":
        return cls(name=str(data["name"]), type=str(data.get("type") or "text"), starts_as=str(data.get("starts_as") or ""),
                   holds=str(data.get("holds") or ""), values=[str(v) for v in data.get("values") or []],
                   part_name=str(data.get("part_name") or ""), part_of=str(data.get("part_of") or ""))

    @classmethod
    def of_record(cls, entries: List[Dict[str, Any]]) -> List["Field"]:
        """A record's fields, with what one part of a list holds placed inside that list."""
        fields = [cls.from_dict(entry) for entry in entries]
        lists = {f.name: f for f in fields if f.type == PARTS}
        for f in fields:
            if f.part_of:
                if f.part_of not in lists:
                    raise KeyError(f"field '{f.name}' is part of '{f.part_of}', which is no list of parts of its record")
                lists[f.part_of].part_fields.append(f)
        return [f for f in fields if not f.part_of]

    def vocabulary(self) -> List[Dict[str, str]]:
        """The values of a fixed set, each with what it means (the words after its name)."""
        return [{"value": name.strip(), "meaning": meaning.strip()}
                for name, _, meaning in (entry.partition(":") for entry in self.values)]

    def starting_value(self) -> Any:
        """What a new record holds in this field, in the field's own type; None when the contract names nothing."""
        text = self.starts_as.strip()
        if text.lower() in NOTHING:
            return None
        try:
            if self.type == "whole_number":
                return int(text)
            if self.type == "decimal_number":
                return float(text)
        except ValueError:
            return None  # "9 columns": said in words, so the class starts it empty and the action sets it
        if self.type == "boolean":
            return {"true": True, "false": False}.get(text.lower())
        return text if self.type in ("text", "one_of", "date", "time", "moment") else None

    def attribute(self) -> AttributeSpec:
        if self.type == PARTS:
            return AttributeSpec(name=self.name, type="list", required=False, item_name=self.part_name or self.name,
                                 item_attributes=[part.attribute() for part in self.part_fields])
        start = self.starting_value()
        return AttributeSpec(name=self.name, type=FIELD_TYPES.get(self.type, "string"), required=False, default_value=start,
                             description="; ".join(words for words in (self.holds, FORMS.get(self.type, "")) if words))

    def starts_by_default(self) -> bool:
        """Whether the class's default is all a new record needs here: nothing is named, or a plain value the
        skeleton wrote into the class. A list that holds parts from the start, or a start said in words, is the
        class's own to build."""
        if self.starts_as.strip().lower() in NOTHING:
            return True
        return self.type != PARTS and self.starting_value() is not None

    def describe(self, indent: str = "- ") -> List[str]:
        start = f" = {self.starts_as}" if self.starts_as else ""
        lines = [f"{indent}{self.name}: {self.type}{start}; {self.holds}".rstrip("; ")]
        lines.extend(f"{indent}  {entry}" for entry in self.values)
        if self.type == PARTS:
            lines[0] = f"{indent}{self.name}: a list of {self.part_name}, {self.starts_as}; {self.holds}".rstrip("; ")
            for part in self.part_fields:
                lines.extend(part.describe("  " + indent))
        return lines


@dataclass
class Record:
    name: str
    origin: str = CREATED
    fields: List[Field] = field(default_factory=list)
    shown: List[str] = field(default_factory=list)
    starting_records: str = ""


@dataclass
class Action:
    name: str
    record: str
    performed_by: str = AUDIENCE
    params: List[str] = field(default_factory=list)   # each as `name: type`; the contract gives them as one text
    sent_to: str = ONE_RECORD
    trigger: str = ""    # of the audience: the part, the gesture and the label; automatic: when the page sends it
    does: str = ""
    works_with: str = ""  # the kinds of stored record it is handed, by record name, separated by commas

    def __post_init__(self) -> None:
        if isinstance(self.params, str):
            self.params = [entry.strip() for entry in self.params.split(",") if entry.strip()]


@dataclass
class Refusal:
    name: str
    action: str = ""
    raised_when: str = ""
    sentence: str = ""
    appears: str = ""


@dataclass
class Rule:
    kind: str
    title: str
    action: str = ""
    given: str = ""      # opens with the name of one of the contract's situations
    when: str = ""
    then: str = ""
    sees: str = ""       # which parts then read what, in the names of `read_out`
    plain: str = ""      # the rule as a person who uses the product says it: what a card shows


@dataclass
class Product:
    name: str
    product_type: str = "other"
    audience: str = ""
    loop: str = ""
    has: List[str] = field(default_factory=list)   # each ends in "(kept)" or "(left out: the reason)"


@dataclass
class Look:
    summary: str = ""
    tokens: str = ""     # the draft theme's line: `background=#.. surface=#.. text=#.. accent=#.. on_accent=#.. heading=..`
    palette: str = ""
    parts: List[str] = field(default_factory=list)
    narrow: str = ""
    grid: str = ""       # `columns=9 rows=9` for a main view that is a grid of equal parts; empty otherwise

    def grid_size(self) -> "tuple[int, int]":
        """The columns and rows the main view opens with; 0 where the contract names none."""
        columns, rows = (re.search(rf"{side}\s*=\s*(\d+)", self.grid or "") for side in ("columns", "rows"))
        return (int(columns.group(1)) if columns else 0, int(rows.group(1)) if rows else 0)


@dataclass
class ProductContract:
    product: Product
    look: Look
    opening: str
    records: List[Record]
    fixed: List[str]
    actions: List[Action]
    read_out: List[str]
    refusals: List[Refusal]
    rules: List[Rule]
    situations: List[str] = field(default_factory=list)   # each as `name = what it is in words: the values it holds`
    source: Dict[str, Any] = field(default_factory=dict, repr=False)  # the answer as it was given, for the record

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductContract":
        """The contract of an answer. Raises ContractError naming the first part that is missing or empty."""
        for key in ("product", "look", "opening", "records", "actions", "rules"):
            if not data.get(key):
                raise ContractError(f"The contract has no usable '{key}'.")
        try:
            return cls(
                product=Product(**data["product"]), look=Look(**data["look"]), opening=str(data["opening"]),
                records=[Record(name=str(r["name"]), origin=str(r.get("origin") or CREATED),
                                fields=Field.of_record(r.get("fields") or []), shown=list(r.get("shown") or []),
                                starting_records=str(r.get("starting_records") or ""))
                         for r in data["records"]],
                fixed=[entry.strip() for entry in str(data.get("fixed") or "").split(";") if entry.strip()], actions=[Action(**a) for a in data["actions"]],
                read_out=list(data.get("read_out") or []), refusals=[Refusal(**r) for r in data.get("refusals") or []],
                rules=[Rule(**r) for r in data["rules"]], situations=[str(s) for s in data.get("situations") or []],
                source=data)
        except (KeyError, TypeError) as exc:
            raise ContractError(f"The contract is not in the agreed form: {type(exc).__name__}: {exc}") from exc

    # --- what the later stages are given -------------------------------------------------------------------------

    def structure(self) -> DomainStructureSchema:
        """The classes the skeleton builds: one per record, holding every field the contract names."""
        return DomainStructureSchema(domain_name=self.product.name, entities=[
            EntitySpec(name=record.name, is_aggregate_root=True,
                       audience_role=AudienceRole.SHOWN if record.origin == FROM_START else AudienceRole.CREATED,
                       created_on_opening=record.origin == OPENED,
                       attributes=[f.attribute() for f in record.fields if f.name != "id"])
            for record in self.records])

    def specs(self) -> List[BusinessSpec]:
        """The rule deck: a rule the records obey is proved by the domain's test loop, a rule of the page alone is not."""
        specs = []
        for number, rule in enumerate(self.rules, start=1):
            page_only = rule.kind == PAGE_RULE
            outcome = rule.sees if page_only else rule.then
            specs.append(BusinessSpec(
                spec_id=f"SPEC-{number:03d}", title=rule.title,
                description=rule.sees if page_only else f"What the person sees: {rule.sees}",
                given_when_then=f"Given {rule.given}, When {rule.when}, Then {outcome}",
                plain=rule.plain, situation=self._situation_of(rule.given), action=rule.action,
                target_aggregate=self._record_of(rule.action) if rule.action else self._worked_on().name,
                kind=(SpecKind.PRESENTATION if page_only else SpecKind.BEHAVIOR).value))
        return specs

    def _situation_of(self, given: str) -> str:
        """The situation a Given names, as `name`: what it holds; empty when it names none. The longest name found
        is the one meant, so a situation named after another (`order_sent`, `order_sent_twice`) is not mistaken."""
        named = {name.strip(): holds.strip() for name, _, holds in (entry.partition("=") for entry in self.situations)}
        found = [name for name in named if name and re.search(rf"(?<![\w]){re.escape(name)}(?![\w])", given)]
        return f"`{max(found, key=len)}`: {named[max(found, key=len)]}" if found else ""

    def _worked_on(self) -> Record:
        """The record the page is about: the first one a person or the page makes, else the first."""
        return next((r for r in self.records if r.origin != FROM_START), self.records[0])

    def action_manifest(self) -> Dict[str, Any]:
        """The action protocol in the form its readers know (action_protocol.py, the test and code writers)."""
        def describe(action: Action) -> str:
            moment = f" The page sends it {action.trigger}." if action.performed_by == AUTOMATIC and action.trigger else ""
            return f"{action.does}{moment}".strip()

        kinds = [r.name for r in self.records]

        def handed(action: Action) -> List[str]:
            named = [name.strip() for name in action.works_with.split(",")]
            return [kind for kind in dict.fromkeys(named) if kind in kinds]

        return {
            "actions": [{"name": a.name, "aggregate": a.record, "performed_by": a.performed_by,
                         "params": [p.split(":")[0].strip() for p in a.params], "description": describe(a),
                         "given": handed(a), "on_kind": a.sent_to == THE_KIND} for a in self.actions],
            "records": [{"aggregate": r.name, "fields": ["id"] + [f.name for f in r.fields if f.name != "id"]}
                        for r in self.records],
            "starting_states": [{"aggregate": r.name, "description": self._starting_state(r),
                                 "held_by_defaults": all(f.starts_by_default() for f in r.fields)} for r in self.records],
            "vocabulary": [{"aggregate": r.name, "field": f.name, "values": f.vocabulary()}
                           for r in self.records for f in r.fields if f.values],
            "rejections": [{"aggregate": self._record_of(r.action), "error": r.name,
                            "raised_when": f'{r.raised_when}; it is raised with exactly this message: "{r.sentence}"'}
                           for r in self.refusals],
        }

    def _record_of(self, action_name: str) -> str:
        """The record an action is sent to; the first record when the contract names no such action."""
        return next((a.record for a in self.actions if a.name == action_name), self.records[0].name)

    @staticmethod
    def _starting_state(record: Record) -> str:
        held = []
        for f in record.fields:
            if f.type == PARTS:
                held.append(f"{f.name} holds {f.starts_as or 'its parts'}")
            elif f.starts_as:
                held.append(f"{f.name} {f.starts_as}")
        return "id is set; " + ", ".join(held) if held else "id is set"

    def intent(self) -> ProductIntent:
        kind = self.product.product_type if self.product.product_type in PRODUCT_TYPES else "other"
        return ProductIntent(product_type=kind, audience=self.product.audience,
                             primary_goal=self.product.loop, scope_summary=self.product.loop,
                             model_focus=[r.name for r in self.records],
                             out_of_scope=[entry for entry in self.product.has if LEFT_OUT in entry])

    def brief(self) -> str:
        """What is built, in words: the text later writers are given where they used to get the expanded pitch."""
        lines = [f"# {self.product.name}", "", "## Product", f"- Who uses it: {self.product.audience}",
                 f"- The loop: {self.product.loop}", "- It has: " + "; ".join(self.product.has), "", "## Records"]
        for record in self.records:
            lines.append(f"### {record.name}: {ORIGINS.get(record.origin, record.origin)}")
            for f in record.fields:
                lines.extend(f.describe())
            lines.extend(f"- shown: {shown}" for shown in record.shown)
            if record.starting_records:
                lines.append(f"- starting records: {record.starting_records}")
        lines += ["", "## Fixed values"] + [f"- {entry}" for entry in self.fixed]
        lines += ["", "## Situations the rules start from"] + [f"- {entry}" for entry in self.situations]
        lines += ["", "## Rules"]
        for spec, rule in zip(self.specs(), self.rules):
            sees = "" if rule.kind == PAGE_RULE else f" The person sees: {rule.sees}"
            lines.append(f"- {spec.spec_id} [{rule.kind}] {rule.title}: {spec.given_when_then}.{sees}")
        return "\n".join(lines)

    def blueprint(self) -> str:
        """The page's plan: what a person meets, where each action is done, how parts are read out, and the look."""
        columns, rows = self.look.grid_size()
        lines = ["### 1. Opening", self.opening, "", "### 2. Where each action is done"]
        for action in self.actions:
            if action.performed_by == AUDIENCE:
                lines.append(f"- `{action.name}`: {action.trigger}")
            elif action.performed_by == AUTOMATIC:
                lines.append(f"- `{action.name}`: no control; the page sends it {action.trigger}")
        lines += ["", "### 3. How each part is read out (role and name, used as written)"]
        lines += [f"- {entry}" for entry in self.read_out]
        lines += ["", "### 4. Wordings"]
        for record in self.records:
            for f in record.fields:
                lines.extend(f"- `{record.name}.{f.name}` {entry}" for entry in f.values)
            lines.extend(f"- shown value: {shown}" for shown in record.shown)
        lines += ["", "### 5. Refusals (the sentence is shown as written)"]
        lines += [f'- `{r.name}` on `{r.action}`: "{r.sentence}", {r.appears}' for r in self.refusals] or ["- (none)"]
        lines += ["", "### 6. Visual Direction", self.look.summary, f"TOKENS {self.look.tokens}"]
        if columns > 0:
            lines.append(f"LAYOUT columns={columns} rows={rows if rows > 0 else 'auto'}")
        lines += [f"Palette: {self.look.palette}", "Parts, in the order they sit on the page:"]
        lines += [f"- {part}" for part in self.look.parts]
        lines.append(f"On a narrow screen: {self.look.narrow}")
        return "\n".join(lines)


@traced("contract.write")
def write_product_contract(pitch: str) -> ProductContract:
    """Writes the contract of a pitch with one LLM call. Raises ContractError on any failure; nothing is retried."""
    prompt = agent_orchestrator.load_prompt("product_contract.md", {"pitch": pitch.strip()})
    raw = agent_orchestrator.call_gemini(prompt, stage=STAGE, json_mode=True, json_schema=CONTRACT_SCHEMA,
                                         timeout_s=CONTRACT_TIMEOUT_S)
    if not raw or not raw.strip():
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        raise ContractError(f"The product contract was not written: {reason}")
    try:
        data = agent_orchestrator.extract_json_object(raw)
    except Exception as exc:
        raise ContractError(f"The product contract is not valid JSON: {exc}") from exc
    return ProductContract.from_dict(data)


def contract_protocol(contract: ProductContract) -> Any:
    """The action protocol stage, answered from the contract (the stage's signature, no model call)."""
    def protocol(**_: Any) -> Dict[str, Any]:
        master = contract.structure().master_entity()
        from onboarding.skeleton_builder import to_snake_case
        return {"success": True, "files": [], "elapsed_seconds": 0.0, "master_name": master.name,
                "master_slug": to_snake_case(master.name), "action_manifest": contract.action_manifest(),
                "router_code": None}
    return protocol


def contract_ux(contract: ProductContract) -> Any:
    """The UX plan stage, answered from the contract (the stage's signature, no model call)."""
    def ux(**_: Any) -> str:
        return contract.blueprint()
    return ux


def to_json(contract: ProductContract) -> str:
    return json.dumps(contract.source, indent=2, ensure_ascii=False)
