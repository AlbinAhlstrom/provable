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
    target_aggregate: str = "Order"
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
    """Adds a new atomic specification to the Behavior Inbox without free-text prompting."""
    uow = SqliteUnitOfWork()
    import random
    s_id = req.spec_id or f"SPEC-{random.randint(100, 999)}"
    spec_dict = {
        "spec_id": s_id,
        "title": req.title,
        "description": req.description,
        "given_when_then": req.given_when_then,
        "target_aggregate": req.target_aggregate,
        "is_mathematical_boundary": req.is_mathematical_boundary,
        "priority": req.priority,
        "status": "PENDING"
    }
    services.add_inbox_spec(spec_dict, uow=uow)
    return {"success": True, "spec": spec_dict}


@router.post("/inbox/{spec_id}/status")
def update_spec_status(spec_id: str, req: SpecStatusUpdateRequest):
    """Updates the status of a specific inbox specification."""
    uow = SqliteUnitOfWork()
    updated = services.update_spec_status(spec_id, status=req.status, uow=uow)
    return {"success": True, "data": updated}
