"""
Router Engine — Structured DDD Intake & Domain Decomposition.
Separates initial natural language pitch into Domain Structure and Behavior Inbox specs.
"""

from pipeline_trace import traced
import os
import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import agent_orchestrator



from enum import Enum


class SpecMutationType(str, Enum):
    ATTRIBUTE_EXPANSION = "ATTRIBUTE_EXPANSION"
    DOMAIN_INVARIANT = "DOMAIN_INVARIANT"
    STATE_TRANSITION = "STATE_TRANSITION"
    API_CONTRACT = "API_CONTRACT"


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
    is_mathematical_boundary: bool = False
    priority: str = "High"
    status: str = "PENDING"


class DomainBehaviorInboxSchema(BaseModel):
    domain_name: str
    specs: List[BusinessSpec] = Field(default_factory=list)


class RouterDecompositionResult(BaseModel):
    structure: DomainStructureSchema
    inbox: DomainBehaviorInboxSchema


@traced("router.decompose")
def decompose_pitch_into_structure_and_inbox(pitch: str) -> RouterDecompositionResult:
    """
    Analyzes business pitch using Router-LLM to strictly decouple Domain Structure from Behavior Inbox.
    """
    clean_pitch = pitch.strip()
    prompt = agent_orchestrator.load_prompt("router_decomposition.md", {"business_pitch": clean_pitch})
    
    raw_response = agent_orchestrator.call_gemini(prompt, stage="router_decomposition")
    if not raw_response:
        api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("LLM synthesis failed: No API key found. Please set LLM_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY in your environment or root .env file.")
        raise RuntimeError("LLM synthesis failed. Refusing to fallback to generic 'Item'.")

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
        
        inbox = DomainBehaviorInboxSchema(
            domain_name=inbox_data.get("domain_name", "ApplicationDomain"),
            specs=[BusinessSpec(**s) for s in inbox_data.get("specs", [])]
        )
        
        return RouterDecompositionResult(structure=structure, inbox=inbox)
    except Exception as e:
        raise RuntimeError("LLM synthesis failed. Refusing to fallback to generic 'Item'.") from e


