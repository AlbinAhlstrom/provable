"""
Pure Domain Model Entities & Value Objects (FastAPI & ORM Ignorant).
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from domain.exceptions import InvalidStatusTransition
import domain.events as events

def resolve_canonical_feature(feature_or_req_id: str) -> dict:
    clean = feature_or_req_id.lower().replace('-', '_').replace(' ', '_')
    clean = re.sub(r'[^a-z0-9_]', '', clean)
    clean = re.sub(r'_+', '_', clean).strip('_')
    base_key = clean.replace('req_ui_', '').replace('req_cmp_', '').replace('req_', '').replace('_001', '')
    if not base_key:
        base_key = "main"
    return {
        'canonical_key': base_key,
        'req_ids': [f"REQ-UI-{base_key.upper()}", f"REQ-{base_key.upper()}-001"],
        'aliases': [base_key]
    }


@dataclass
class Component:
    id: str
    title: str
    description: str
    canonical_key: str
    component_type: str = "custom"
    prompt: Optional[str] = None
    status: str = "Done"
    priority: str = "High"
    tests: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Component):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "canonical_key": self.canonical_key,
            "component_type": self.component_type,
            "prompt": self.prompt,
            "status": self.status,
            "priority": self.priority,
            "tests": self.tests,
        }

    @classmethod
    def create(cls, prompt: str) -> "Component":
        p_clean = prompt.strip()
        info = resolve_canonical_feature(p_clean)
        canon_key = info['canonical_key']
        req_id = f"REQ-CMP-{canon_key.upper()}-001"
        comp_type = "premade" if canon_key in ['catalog', 'cart', 'tracking', 'kds', 'reviews', 'auth', 'calendar'] else "custom"
        test_case = {
            "name": f"test_component_{canon_key}_active",
            "given": f"Given active application stack with component {canon_key}",
            "when": f"When rendering component {canon_key}",
            "then": f"Then component UI elements for {p_clean} render successfully",
            "status": "pass"
        }
        comp = cls(
            id=req_id,
            title=f"Dynamic Component: {p_clean.capitalize()}",
            description=f"The system shall provide an interactive {p_clean} component.",
            canonical_key=canon_key,
            component_type=comp_type,
            prompt=p_clean,
            status="Done",
            priority="High",
            tests=[test_case]
        )
        comp.events.append(events.ComponentAdded(canonical_key=canon_key, prompt=p_clean, req_id=req_id))
        return comp


VALID_TRANSITIONS = {
    "Backlog": ["In_Progress", "Disabled"],
    "In_Progress": ["Review", "Backlog"],
    "Review": ["Test", "In_Progress"],
    "Test": ["Done", "In_Progress", "Conflict"],
    "Conflict": ["In_Progress"],
    "Done": ["Backlog", "Disabled"],
    "Disabled": ["Backlog"]
}

@dataclass
class Requirement:
    id: str
    title: str
    description: str
    status: str = "Backlog"
    priority: str = "High"
    type: str = "Requirement"
    parent_id: Optional[str] = None
    layer: str = "LOGIC"
    tests: List[Dict[str, Any]] = field(default_factory=list)
    assigned_agents: List[str] = field(default_factory=list)
    proposed_code: Optional[str] = None
    feedback: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    component_type: Optional[str] = None
    component_meta: Optional[str] = None
    events: List[Any] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Requirement):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def transition_to(self, new_status: str):
        allowed = VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise InvalidStatusTransition(
                f"Cannot transition Requirement '{self.id}' from '{self.status}' to '{new_status}'. Allowed: {allowed}"
            )
        self.status = new_status

    def start_progress(self):
        self.transition_to("In_Progress")

    def submit_for_review(self, code: str):
        self.proposed_code = code
        self.transition_to("Review")

    def approve(self):
        self.transition_to("Test")

    def reject(self, feedback: str):
        self.feedback = feedback
        self.transition_to("In_Progress")
        self.events.append(events.RequirementRejected(req_id=self.id, feedback=feedback))

    def complete(self):
        self.transition_to("Done")

    def edit(self, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None):
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        self.events.append(events.RequirementEdited(req_id=self.id, title=title, description=description, priority=priority))

    def move(self, parent_id: Optional[str]):
        self.parent_id = parent_id
        self.events.append(events.RequirementMoved(req_id=self.id, parent_id=parent_id))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'parentId': self.parent_id,
            'dependencies': self.dependencies,
            'assignedAgents': self.assigned_agents,
            'proposedCode': self.proposed_code,
            'feedback': self.feedback or '',
            'component_type': self.component_type,
            'component_meta': self.component_meta,
            'tests': self.tests,
        }

    @classmethod
    def create_folder(cls, folder_id: str, title: str, description: str = "", parent_id: Optional[str] = None) -> "Requirement":
        return cls(
            id=folder_id,
            title=title,
            description=description or "",
            priority="High",
            status="Backlog",
            type="Folder",
            parent_id=parent_id,
            dependencies=[],
            assigned_agents=[]
        )

    @classmethod
    def create_param_requirement(cls, param_key: str, value: str) -> "Requirement":
        if param_key == 'brand_title':
            req_id = "REQ-BRAND-001"
            req_title = f"Storefront brand title set to '{value}'"
            req_desc = f"The application shall display '{value}' as the primary brand header title."
            tc_name = "test_storefront_brand_title_configured"
            tc_given = "Given the storefront application is loaded"
            tc_when = "When rendering the navigation header"
            tc_then = f"Then the brand title displays '{value}'"
        elif param_key == 'delivery_sla':
            req_id = "REQ-DELIVERY-001"
            req_title = f"Estimated Delivery SLA set to '{value}'"
            req_desc = f"The system shall display estimated delivery SLA as '{value}' across order views."
            tc_name = "test_delivery_sla_configured"
            tc_given = "Given customer checkout view"
            tc_when = "When estimated delivery SLA is rendered"
            tc_then = f"Then SLA displays '{value}'"
        else:
            raise ValueError(f"Unknown param_key '{param_key}'")

        test_case = {
            "name": tc_name,
            "given": tc_given,
            "when": tc_when,
            "then": tc_then,
            "status": "pass"
        }
        return cls(
            id=req_id,
            title=req_title,
            description=req_desc,
            type="Requirement",
            priority="High",
            status="Done",
            tests=[test_case]
        )


@dataclass
class Project:
    name: str
    path: str
    active: bool = False
    events: List[Any] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Project):
            return False
        return os.path.normcase(os.path.abspath(self.path)) == os.path.normcase(os.path.abspath(other.path))

    def __hash__(self) -> int:
        return hash(os.path.normcase(os.path.abspath(self.path)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "active": self.active
        }


@dataclass
class TestSpec:
    id: str
    requirement_id: str
    name: str = ""
    given: str = ""
    when: str = ""
    then: str = ""
    last_result: str = "pending"
    test_code: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TestSpec):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "requirement_id": self.requirement_id,
            "name": self.name,
            "given": self.given,
            "when": self.when,
            "then": self.then,
            "last_result": self.last_result,
            "test_code": self.test_code
        }

    @classmethod
    def create(
        cls,
        requirement_id: str,
        name: str = "",
        given: str = "",
        when: str = "",
        then: str = "",
        test_code: str = ""
    ) -> "TestSpec":
        tc_id = f"TC-{requirement_id}"
        return cls(
            id=tc_id,
            requirement_id=requirement_id,
            name=name or f"test_{requirement_id.lower().replace('-', '_')}",
            given=given or "Given active system state",
            when=when or f"When executing requirement {requirement_id}",
            then=then or "Then expected assertions pass",
            last_result="pending",
            test_code=test_code
        )


@dataclass
class AgentRun:
    id: str
    ticket_id: Optional[str] = None
    step: str = "Idle"
    active: bool = False
    attempt: int = 0
    max_attempts: int = 3
    last_update: str = ""
    log_content: str = ""
    events: List[Any] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AgentRun):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "active": self.active,
            "ticket_id": self.ticket_id,
            "step": self.step,
            "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "last_update": self.last_update,
            "log_content": self.log_content,
        }

    @staticmethod
    def analyze_backlog(backlog_requirements: List[Requirement]) -> Dict[str, Any]:
        if backlog_requirements:
            top_task = backlog_requirements[0]
            return {
                "ticket": top_task.id,
                "title": top_task.title,
                "reasoning": f"Prioritized ticket {top_task.id} ({top_task.title}) based on High priority backlog ordering.",
                "action": f"Dispatching autonomous developer agent to write BDD test suite and implement feature logic for {top_task.id}."
            }
        return {
            "ticket": None,
            "title": None,
            "reasoning": "No active tasks remaining in Backlog state.",
            "action": "Agent idling, waiting for new requirements or bug reports."
        }


MOCK_DOMAIN_SCHEMA = {
    "pitch": "Universal domain storefront and ordering platform",
    "entities": [
        {"name": "Order", "identity": "order_number", "fields": ["order_number", "customer_name", "status", "total_order_price"]},
        {"name": "OrderItem", "identity": "id", "fields": ["item_name", "quantity", "unit_price"]}
    ],
    "services": [
        {"name": "place_order", "parameters": ["order_number", "customer_name", "item_name", "quantity", "price"]},
        {"name": "update_status", "parameters": ["order_number", "status"]}
    ],
    "exceptions": ["DomainError", "OrderNotFound", "InvalidOrderState"],
    "invariants": [
        "Order total price must equal sum of item prices",
        "Cancelled orders cannot transition to completed"
    ]
}


@dataclass
class EntityAttribute:
    name: str
    type: str = "string"  # "string", "currency", "number", "tags", "boolean"
    required: bool = False
    default_value: Any = None
    display_mode: str = "visible"  # "visible", "tag_chips", "badge", "subtitle", "hidden"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "default_value": self.default_value,
            "display_mode": self.display_mode
        }


@dataclass
class DomainEntitySchema:
    entity_name: str
    canonical_key: str
    attributes: List[EntityAttribute] = field(default_factory=list)
    is_aggregate_root: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "canonical_key": self.canonical_key,
            "attributes": [a.to_dict() if hasattr(a, 'to_dict') else a for a in self.attributes],
            "is_aggregate_root": self.is_aggregate_root
        }


@dataclass
class KickstartState:
    business_pitch: str = "An industrial warehouse management system tracking Pallets, storage Zones, and forklift Operators."
    blocks: List[str] = field(default_factory=list)

    extracted_requirements: List[Dict[str, Any]] = field(default_factory=list)
    synthesized: bool = False
    custom_fixtures: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    entity_schemas: Dict[str, DomainEntitySchema] = field(default_factory=dict)
    inbox_specs: List[Dict[str, Any]] = field(default_factory=list)
    intent: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "business_pitch": self.business_pitch,
            "intent": self.intent,
            "blocks": self.blocks,
            "extracted_requirements": self.extracted_requirements,
            "synthesized": self.synthesized,
            "custom_fixtures": self.custom_fixtures,
            "inbox_specs": self.inbox_specs,
            "entity_schemas": {
                k: (v.to_dict() if hasattr(v, 'to_dict') else v)
                for k, v in self.entity_schemas.items()
            }
        }






