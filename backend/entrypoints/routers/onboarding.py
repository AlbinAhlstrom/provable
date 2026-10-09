"""
Onboarding & Kickstart API Router — Handles domain decomposition, skeleton scaffolding, and aggregate discovery.
Delegates 100% of business logic to DDD Service Layer & Unit of Work.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services

router = APIRouter(prefix="/api/onboarding", tags=["Onboarding Kickstart"])


class KickstartRequest(BaseModel):
    pitch: Optional[str] = None
    business_pitch: Optional[str] = None
    mode: Optional[str] = "fast"


@router.post("/kickstart")
def kickstart_endpoint(req: KickstartRequest):
    """Synchronously decomposes pitch, builds DDD skeleton, and returns domain aggregates."""
    uow = SqliteUnitOfWork()
    pitch = req.pitch or req.business_pitch or "An industrial warehouse management system tracking Pallets, storage Zones, and forklift Operators."
    try:
        return services.kickstart_domain_and_scaffold(
            pitch=pitch,
            uow=uow,
            mode=req.mode or "fast"
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "detail": str(e)
        }



@router.post("/page")
def rebuild_page_endpoint():
    """Writes the current app's page again against the domain it already has (no decomposition, no TDD loop)."""
    try:
        return services.rebuild_page(uow=SqliteUnitOfWork())
    except Exception as e:
        return {"success": False, "error": str(e), "detail": str(e)}


@router.get("/progress")
def build_progress_endpoint():
    """What the running kickstart has delivered so far (answered while the kickstart request is still open)."""
    from onboarding.build_progress import current_progress
    return current_progress().to_dict()


@router.get("/aggregates")
def get_aggregates_endpoint():
    """Returns the active domain aggregates discovered for the current bounded context."""
    uow = SqliteUnitOfWork()
    return services.get_active_domain_aggregates(uow=uow)


@router.post("/reset")
def reset_onboarding_workspace_endpoint():
    """Physically nukes all workspace files and purges database tables."""
    uow = SqliteUnitOfWork()
    return services.reset_all_projects(uow=uow)

