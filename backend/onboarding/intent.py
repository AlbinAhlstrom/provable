"""Product-intent step: decide what KIND of product a pitch asks for before the domain model is designed.

Without it the decomposition prompt defaults to a back-office DDD model for every pitch (a "personal website"
became a booking management console). The intent scopes the model: what to cover and what NOT to model.
"""

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import agent_orchestrator
from pipeline_trace import traced

PRODUCT_TYPES = (
    "public_website", "customer_app", "internal_tool", "api_service", "marketplace", "game", "data_pipeline", "other",
)


class IntentError(RuntimeError):
    """The pitch could not be classified (provider error, unusable answer). Never papered over with a default."""


@dataclass
class ProductIntent:
    product_type: str
    audience: str
    primary_goal: str
    scope_summary: str
    model_focus: List[str]
    out_of_scope: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductIntent":
        for key in ("product_type", "audience", "primary_goal", "scope_summary", "model_focus"):
            if not data.get(key):
                raise IntentError(f"Intent is missing a usable '{key}'.")
        if data["product_type"] not in PRODUCT_TYPES:
            raise IntentError(f"Intent product_type '{data['product_type']}' is not one of {', '.join(PRODUCT_TYPES)}.")
        return cls(
            product_type=data["product_type"],
            audience=str(data["audience"]),
            primary_goal=str(data["primary_goal"]),
            scope_summary=str(data["scope_summary"]),
            model_focus=[str(x) for x in data["model_focus"]],
            out_of_scope=[str(x) for x in data.get("out_of_scope", [])],
            assumptions=[str(x) for x in data.get("assumptions", [])],
        )


def intent_block(intent: Optional[ProductIntent]) -> str:
    """Text injected into the decomposition prompt (empty-intent callers get an explicit 'not specified')."""
    if intent is None:
        return "(Product intent not specified: infer the scope from the pitch alone.)"
    lines = [
        f"- Product type: {intent.product_type}",
        f"- Audience: {intent.audience}",
        f"- Goal: {intent.primary_goal}",
        f"- Scope: {intent.scope_summary}",
        f"- The model must cover: {'; '.join(intent.model_focus)}",
    ]
    if intent.out_of_scope:
        lines.append(f"- Do NOT model: {'; '.join(intent.out_of_scope)}")
    return "\n".join(lines)


@traced("intent.classify")
def classify_pitch_intent(pitch: str) -> ProductIntent:
    """Classifies the pitch with one LLM call. Raises IntentError on any failure: there is no default intent."""
    prompt = agent_orchestrator.load_prompt("intent_classification.md", {"business_pitch": pitch.strip()})
    raw = agent_orchestrator.call_gemini(prompt, stage="intent_classification", json_mode=True)
    if not raw or not raw.strip():
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        raise IntentError(f"Intent classification failed: {reason}")
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise IntentError(f"Intent classification did not return valid JSON: {e}") from e
    return ProductIntent.from_dict(data)
