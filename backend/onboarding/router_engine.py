"""
Router Engine — Structured DDD Intake & Domain Decomposition.
Separates initial natural language pitch into Domain Structure and Behavior Inbox specs.
"""

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


def decompose_pitch_into_structure_and_inbox(pitch: str) -> RouterDecompositionResult:
    """
    Analyzes business pitch using Router-LLM to strictly decouple Domain Structure from Behavior Inbox.
    """
    clean_pitch = pitch.strip()
    prompt = agent_orchestrator.load_prompt("router_decomposition.md", {"business_pitch": clean_pitch})
    if not prompt:
        prompt = f'Decompose into structure and behavior inbox: "{clean_pitch}"'
    
    raw_response = agent_orchestrator.call_gemini(prompt, stage="router_decomposition")
    
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
        # Fallback to minimal safe domain structure
        default_entity = EntitySpec(
            name="Item",
            is_aggregate_root=True,
            attributes=[AttributeSpec(name="id", type="str"), AttributeSpec(name="name", type="str")]
        )
        default_spec = BusinessSpec(
            spec_id="SPEC-001",
            title="Enforce Item Creation",
            description="Item should be initialized with valid parameters.",
            given_when_then="Given item params When instantiating Then item is created",
            target_aggregate="Item",
            is_mathematical_boundary=False,
            priority="High",
            status="PENDING"
        )
        return RouterDecompositionResult(
            structure=DomainStructureSchema(domain_name="DefaultDomain", entities=[default_entity]),
            inbox=DomainBehaviorInboxSchema(domain_name="DefaultDomain", specs=[default_spec])
        )
