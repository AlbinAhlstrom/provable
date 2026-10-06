"""
Pydantic Request & Response Payload DTOs for Provable Backend API Endpoints.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# ── Project Management Payload DTOs ──────────────────────────────────────────

class ProjectSwitchPayload(BaseModel):
    path: str

class ProjectAddPayload(BaseModel):
    path: str
    run_synthesis: bool = True

# ── Requirements Payload DTOs ────────────────────────────────────────────────

class Requirement(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    tests: List[Dict[str, Any]]
    assignedAgents: List[str]
    proposedCode: Optional[str] = None
    feedback: Optional[str] = None
    type: Optional[str] = None
    parentId: Optional[str] = None
    dependencies: Optional[List[str]] = []

class CreateRequirementPayload(BaseModel):
    title: str
    description: str
    parentId: Optional[str] = None

class CreateFolderPayload(BaseModel):
    title: str
    description: Optional[str] = ""
    parentId: Optional[str] = None

class EditRequirementPayload(BaseModel):
    id: str
    title: str
    description: str
    priority: str

class ParamUpdateRequest(BaseModel):
    param_key: str
    value: str

class FeatureToggleRequest(BaseModel):
    feature_id: str
    enabled: bool

# ── Code Review & Diff Payload DTOs ───────────────────────────────────────────

class ApprovePayload(BaseModel):
    id: str
    code: Optional[str] = None

class RejectPayload(BaseModel):
    id: str
    feedback: str

class FeedbackPayload(BaseModel):
    id: str
    feedback: str

class ReportBugPayload(BaseModel):
    title: str
    parentId: str
    steps: str
    expected: str
    actual: str

class CheckoutPreviewPayload(BaseModel):
    branch: str

# ── Domain Modeling & Kickstart Payload DTOs ──────────────────────────────────

class DomainDiscoveryRequest(BaseModel):
    business_pitch: str

class DomainRefinementRequest(BaseModel):
    current_schema: Dict[str, Any]
    feedback: str

class DomainSynthesisRequest(BaseModel):
    domain_schema: Dict[str, Any]

class KickstartAnalyzeRequest(BaseModel):
    business_pitch: str

class KickstartSynthesisRequest(BaseModel):
    business_pitch: Optional[str] = None
    pitch: Optional[str] = None
    mode: Optional[str] = "fast"
    selected_blocks: Optional[List[str]] = None
    selected_block_ids: Optional[List[str]] = None
    requirements: Optional[List[Dict[str, Any]]] = None
    extracted_requirements: Optional[List[Dict[str, Any]]] = None

# ── Component & Sub-requirement Payload DTOs ──────────────────────────────────

class ComponentAddRequest(BaseModel):
    prompt: str
    component_type: str = "custom"

class ComponentDeleteRequest(BaseModel):
    canonical_key: str

class SubRequirementAddRequest(BaseModel):
    parent_canonical_key: str
    prompt: str

class SubRequirementDeleteRequest(BaseModel):
    parent_canonical_key: str
    sub_id: str

class ComponentFixturesUpdateRequest(BaseModel):
    canonical_key: str
    fixtures: List[Dict[str, Any]]

class EntityAttributeSchema(BaseModel):
    name: str
    type: str = "string"
    required: bool = False
    default_value: Optional[Any] = None

class EntitySchemaUpdateRequest(BaseModel):
    canonical_key: str
    entity_name: str
    attributes: List[EntityAttributeSchema]


# ── Generator Scaffolding Test Models (Benchmark Domain) ─────────────────────

class BatchIn(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: Optional[Any] = None

class OrderLineIn(BaseModel):
    orderid: str
    sku: str
    qty: int

class OrderIn(BaseModel):
    order_number: str
    customer_name: str
    item_name: str = "Standard Item"
    pizza_name: Optional[str] = None
    size: str = "Standard"
    quantity: int = 1
    price: float

    def get_item_name(self) -> str:
        return self.pizza_name or self.item_name


class BulkStatusUpdateRequest(BaseModel):
    req_ids: List[str]
    target_status: str



