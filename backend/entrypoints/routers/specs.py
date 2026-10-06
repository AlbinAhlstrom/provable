"""
Spec-CRUD & TDD Inbox API Router.
Enables structured specification management without natural language prompt drift.
Delegates 100% of business logic to DDD Service Layer & Unit of Work.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services

router = APIRouter(prefix="/api/specs", tags=["Behavior Inbox Specs"])


class SpecCreateRequest(BaseModel):
    spec_id: Optional[str] = None
    title: str
    description: str
    given_when_then: str
    target_aggregate: str = "Pallet"
    spec_type: str = "DOMAIN_INVARIANT"
    kind: str = "behavior"  # "behavior" (TDD loop) or "presentation" (view rewrite + build)
    is_mathematical_boundary: bool = False
    priority: str = "High"


class SpecStatusUpdateRequest(BaseModel):
    status: str


@router.get("/inbox", response_model=List[Dict[str, Any]])
def get_inbox_specs():
    """Lists all specifications currently queued in the Behavior Inbox."""
    uow = SqliteUnitOfWork()
    return services.get_inbox_specs(uow=uow)


@router.post("/inbox/add", status_code=status.HTTP_201_CREATED)
def add_inbox_spec(req: SpecCreateRequest):
    """Adds a new atomic specification to the Behavior Inbox and synchronously executes the TDD machine."""
    uow = SqliteUnitOfWork()
    import random
    s_id = req.spec_id or f"SPEC-{random.randint(100, 999)}"
    spec_dict = {
        "spec_id": s_id,
        "title": req.title,
        "description": req.description,
        "given_when_then": req.given_when_then,
        "target_aggregate": req.target_aggregate,
        "spec_type": req.spec_type,
        "kind": req.kind,
        "is_mathematical_boundary": req.is_mathematical_boundary,
        "priority": req.priority,
        "status": "PENDING"
    }
    services.add_inbox_spec(spec_dict, uow=uow)
    tdd_result = services.execute_inbox_spec_tdd(s_id, uow=uow)
    spec_dict["status"] = tdd_result.get("status", "FULFILLED" if tdd_result.get("success") else "REQUIRES_HUMAN_INTERVENTION")
    return {"success": tdd_result.get("success", False), "spec": spec_dict, "tdd_result": tdd_result}


@router.post("/inbox/{spec_id}/status")
def update_spec_status(spec_id: str, req: SpecStatusUpdateRequest):
    """Updates the status of a specific inbox specification."""
    uow = SqliteUnitOfWork()
    updated = services.update_spec_status(spec_id, status=req.status, uow=uow)
    return {"success": True, "data": updated}


@router.post("/inbox/{spec_id}/execute")
def execute_inbox_spec(spec_id: str):
    """Executes the TDD loop for an existing specification in the Behavior Inbox."""
    uow = SqliteUnitOfWork()
    tdd_result = services.execute_inbox_spec_tdd(spec_id, uow=uow)
    return {"success": tdd_result.get("success", False), "tdd_result": tdd_result}


# ============================================================================
# 🃏 THE LIVING RULE DECK ENDPOINTS (The Fluxx Paradigm)
# ============================================================================

class RuleCardCreateRequest(BaseModel):
    id: Optional[str] = None
    title: str
    chapter: Optional[str] = "General"
    card_type: str = "LOGIC"  # "LOGIC" or "VIEW"
    category: Optional[str] = "INVARIANT"
    target: str = "global"     # "global" or specific entity/component name
    description: str = ""
    given_clause: str = ""
    when_clause: str = ""
    then_clause: str = ""
    unless_clause: str = ""
    is_active: bool = True
    derived_from_id: Optional[str] = None


class RuleCardToggleRequest(BaseModel):
    is_active: bool


class RuleCardUpdateRequest(BaseModel):
    title: Optional[str] = None
    chapter: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    target: Optional[str] = None
    given_clause: Optional[str] = None
    when_clause: Optional[str] = None
    then_clause: Optional[str] = None
    unless_clause: Optional[str] = None
    status: Optional[str] = None


@router.get("/deck")
def get_living_deck():
    """Returns the Living Deck categorized into logic_cards and view_cards."""
    uow = SqliteUnitOfWork()
    return services.get_categorized_living_deck(uow=uow)


@router.post("/deck/add", status_code=status.HTTP_201_CREATED)
def add_rule_card(req: RuleCardCreateRequest):
    """Adds or updates a RuleCard in the Living Deck."""
    uow = SqliteUnitOfWork()
    import random
    card_id = req.id or f"CARD-{random.randint(100, 999)}"
    card_dict = {
        "id": card_id,
        "title": req.title,
        "chapter": req.chapter or "General",
        "card_type": req.card_type,
        "category": req.category or "INVARIANT",
        "target": req.target or "global",
        "description": req.description,
        "given_clause": req.given_clause,
        "when_clause": req.when_clause,
        "then_clause": req.then_clause,
        "unless_clause": req.unless_clause,
        "is_active": req.is_active,
        "derived_from_id": req.derived_from_id,
        "status": "PENDING"
    }
    saved = services.add_rule_card(card_dict, uow=uow)

    # Immediately drive the incremental Delta Evolution Compiler pipeline
    evolution_res = services.execute_inbox_spec_tdd(card_id, uow=uow)
    if evolution_res.get("success"):
        saved["status"] = "FULFILLED"
    else:
        saved["status"] = evolution_res.get("status", "REQUIRES_HUMAN_INTERVENTION")

    return {"success": True, "card": saved, "evolution_result": evolution_res}



@router.post("/deck/{card_id}/toggle")
def toggle_rule_card(card_id: str, req: RuleCardToggleRequest):
    """Toggles active state of a RuleCard (sets to PAUSED if inactive)."""
    uow = SqliteUnitOfWork()
    updated = services.toggle_rule_card(card_id, is_active=req.is_active, uow=uow)
    return {"success": True, "card": updated}


@router.post("/deck/{card_id}/update")
def update_rule_card(card_id: str, req: RuleCardUpdateRequest):
    """Updates fields of a specific RuleCard in the Living Deck."""
    uow = SqliteUnitOfWork()
    updates = {k: v for k, v in req.dict(exclude_unset=True).items() if v is not None}
    updated = services.update_rule_card(card_id, updates=updates, uow=uow)
    return {"success": True, "card": updated}


@router.delete("/deck/{card_id}")
def delete_rule_card(card_id: str):
    """Deletes a specific RuleCard from the Living Deck."""
    uow = SqliteUnitOfWork()
    success = services.delete_rule_card(card_id, uow=uow)
    return {"success": success, "deleted_id": card_id}



