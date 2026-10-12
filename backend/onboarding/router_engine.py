"""
Router Engine — Structured DDD Intake & Domain Decomposition.
Separates initial natural language pitch into Domain Structure and Behavior Inbox specs.
"""

from pipeline_trace import traced
import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
import agent_orchestrator
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # avoid a runtime import cycle; the type is only used in a signature
    from onboarding.intent import ProductIntent



from enum import Enum


class SpecMutationType(str, Enum):
    ATTRIBUTE_EXPANSION = "ATTRIBUTE_EXPANSION"
    DOMAIN_INVARIANT = "DOMAIN_INVARIANT"
    STATE_TRANSITION = "STATE_TRANSITION"
    API_CONTRACT = "API_CONTRACT"


class SpecKind(str, Enum):
    """What a spec constrains: domain behaviour (proved by the TDD loop) or what the user sees (proved by a build)."""
    BEHAVIOR = "behavior"
    PRESENTATION = "presentation"


class AttributeSpec(BaseModel):
    name: str
    type: str = "str"
    required: bool = True
    default_value: Optional[Any] = None


class EntitySpec(BaseModel):
    name: str
    is_aggregate_root: bool = True
    attributes: List[AttributeSpec] = Field(default_factory=list)
    relationships: List[Dict[str, str]] = Field(default_factory=list)


class DomainStructureSchema(BaseModel):
    domain_name: str
    entities: List[EntitySpec] = Field(default_factory=list)
    value_objects: List[EntitySpec] = Field(default_factory=list)
    enums: List[Dict[str, Any]] = Field(default_factory=list)


class BusinessSpec(BaseModel):
    spec_id: str
    title: str
    description: str
    given_when_then: str
    target_aggregate: str
    spec_type: str = SpecMutationType.DOMAIN_INVARIANT.value
    kind: str = SpecKind.BEHAVIOR.value
    category: Optional[str] = "INVARIANT"
    is_mathematical_boundary: bool = False
    priority: str = "High"
    status: str = "PENDING"



class DomainBehaviorInboxSchema(BaseModel):
    domain_name: str
    specs: List[BusinessSpec] = Field(default_factory=list)


class RouterDecompositionResult(BaseModel):
    structure: DomainStructureSchema
    inbox: DomainBehaviorInboxSchema


def verify_and_clean_spec_jargon(spec_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Plain-Language Spec Verifier Gate:
    Detects and cleans low-level programming artifacts (PascalCase class names, method calls,
    screaming snake-case enums, technical framework terms) in human BDD clauses.
    Ensures that to the user, 'specs are code' written in accessible plain English.
    """
    cleaned = dict(spec_dict)
    violations: List[str] = []

    fields_to_check = [
        "title", "given_clause", "when_clause", "then_clause", "unless_clause", "given_when_then", "description"
    ]

    replacements = [
        (r"\bGameSession\b", "game session"),
        (r"\bCellState\b", "cell"),
        (r"\bTileAggregate\b", "tile"),
        (r"\bIN_PROGRESS\b", "in-progress"),
        (r"\bUNINITIALIZED\b", "unstarted"),
        (r"\bRESOLVED\b", "finished"),
        (r"\bVICTORY\b", "victory"),
        (r"\bDEFEAT\b", "defeat"),
        (r"\bDigCell\(([^)]*)\)", r"uncovering tile \1"),
        (r"\bprimary_reveal\(([^)]*)\)", r"revealing cell \1"),
        (r"\bcycle_marker\(([^)]*)\)", r"cycling marker \1"),
        (r"\bOCC\b", "concurrency check"),
        (r"\bFastAPI\b", "backend API"),
        (r"\bUoW\b", "system transaction"),
        (r"\bAggregateRoot\b", "entity"),
    ]

    for field in fields_to_check:
        val = cleaned.get(field)
        if not val or not isinstance(val, str):
            continue

        for m in re.finditer(r"\b([A-Za-z0-9_]+)\([^)]*\)", val):
            func_name = m.group(1)
            if func_name.lower() not in ["given", "when", "then", "if"]:
                violations.append(f"Method call '{m.group(0)}' in {field}")

        for m in re.finditer(r"\b([A-Z]{2,}_[A-Z0-9_]+)\b", val):
            violations.append(f"Enum constant '{m.group(1)}' in {field}")

        for m in re.finditer(r"\b([A-Z][a-z0-9]+[A-Z][a-zA-Z0-9]*)\b", val):
            class_name = m.group(1)
            if class_name not in ["JavaScript", "TypeScript", "English"]:
                violations.append(f"PascalCase class identifier '{class_name}' in {field}")

        for pattern, repl in replacements:
            val = re.sub(pattern, repl, val, flags=re.IGNORECASE)

        def _pascal_to_spaced(match):
            s = match.group(1)
            return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s).lower()

        val = re.sub(r"(?<=\s)([A-Z][a-z0-9]+[A-Z][a-zA-Z0-9]*)\b", _pascal_to_spaced, val)
        val = re.sub(r"\b([a-zA-Z0-9_]+)\(([^)]*)\)", r"\1 \2", val)
        cleaned[field] = val.strip()

    return cleaned, violations


@traced("router.decompose")
def decompose_pitch_into_structure_and_inbox(pitch: str, intent: "Optional[ProductIntent]" = None) -> RouterDecompositionResult:
    """
    Analyzes business pitch using Router-LLM to strictly decouple Domain Structure from Behavior Inbox.
    Supports top-down chapters and enforces the plain-language Spec Verifier Gate.
    """
    clean_pitch = pitch.strip()
    from onboarding.intent import intent_block
    prompt = agent_orchestrator.load_prompt("router_decomposition.md", {"business_pitch": clean_pitch, "intent_block": intent_block(intent)})
    
    raw_response = agent_orchestrator.call_gemini(prompt, stage="router_decomposition", json_mode=True)
    if not raw_response:
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        raise RuntimeError(f"LLM synthesis failed: {reason} (refusing to fall back to a generic 'Item').")

    # Parse structured response
    try:
        # Strip markdown fences if present
        clean_json = re.sub(r"^```json\s*", "", raw_response.strip(), flags=re.MULTILINE)
        clean_json = re.sub(r"^```\s*$", "", clean_json.strip(), flags=re.MULTILINE)
        data = json.loads(clean_json)
        
        structure_data = data.get("structure", {})
        inbox_data = data.get("inbox", {})
        
        structure = DomainStructureSchema(
            domain_name=structure_data.get("domain_name", "ApplicationDomain"),
            entities=[EntitySpec(**e) for e in structure_data.get("entities", [])],
            value_objects=[EntitySpec(**v) for v in structure_data.get("value_objects", [])],
            enums=structure_data.get("enums", [])
        )
        
        raw_specs = []
        if "chapters" in data and isinstance(data["chapters"], list):
            for ch in data["chapters"]:
                ch_title = ch.get("title") or ch.get("name") or "General"
                for s in ch.get("specs", []):
                    s_copy = dict(s)
                    s_copy.setdefault("chapter", ch_title)
                    raw_specs.append(s_copy)
        elif "inbox" in data:
            raw_specs = inbox_data.get("specs", [])
        
        sanitized_specs = []
        for s in raw_specs:
            clean_s, _ = verify_and_clean_spec_jargon(s)
            sanitized_specs.append(BusinessSpec(**clean_s))
        
        inbox = DomainBehaviorInboxSchema(
            domain_name=inbox_data.get("domain_name", structure.domain_name),
            specs=sanitized_specs
        )
        
        return RouterDecompositionResult(structure=structure, inbox=inbox)
    except Exception as e:
        raise RuntimeError("LLM synthesis failed. Refusing to fallback to generic 'Item'.") from e



# ============================================================================
# 🔄 THE BIDIRECTIONAL AUTO-RULE DERIVATION ENGINE (The Fluxx Paradigm)
# ============================================================================

def project_ui_affordances_from_logic_card(
    card: Any,
    existing_view_cards: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Top-Down Projection:
    Analyzes a newly added or modified LOGIC card.
    Identifies which VIEW cards require new UI affordances (buttons, inputs, status badges, timers)
    to ensure Zero Phantom Logic in the live application.
    """
    c_dict = card.to_dict() if hasattr(card, "to_dict") else dict(card)
    title = c_dict.get("title", "").lower()
    desc = c_dict.get("description", "").lower()
    when_c = c_dict.get("when_clause", "").lower()
    then_c = c_dict.get("then_clause", "").lower()
    combined = f"{title} {desc} {when_c} {then_c}"

    target_view = "Main"
    if existing_view_cards and len(existing_view_cards) > 0:
        target_view = existing_view_cards[0].get("target") or existing_view_cards[0].get("title") or "Main"

    affordance_type = "action_button"
    label = c_dict.get("title", "Action")

    if any(k in combined for k in ["timer", "clock", "klocka", "countdown", "blitz"]):
        affordance_type = "timer_display"
        label = "Live Countdown Timer"
    elif any(k in combined for k in ["promo", "discount", "code", "input", "rabatt", "enter"]):
        affordance_type = "input_field"
        label = "Apply Promo / Code"
    elif any(k in combined for k in ["badge", "status", "warning", "lock", "alert"]):
        affordance_type = "status_badge"
        label = "Status Indicator"
    elif any(k in combined for k in ["undo", "ångra"]):
        affordance_type = "action_button"
        label = "Undo Move"
    elif any(k in combined for k in ["resign", "ge upp", "cancel", "avboka"]):
        affordance_type = "action_button"
        label = "Cancel / Resign"

    return [
        {
            "target_view": target_view,
            "affordance_type": affordance_type,
            "label": label,
            "card_id": c_dict.get("id"),
            "bound_rule_title": c_dict.get("title")
        }
    ]



