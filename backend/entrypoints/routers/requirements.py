"""
Requirements API Router — Handles requirements CRUD, folders, parameters, toggles, and synthesis via DDD Service Layer & Unit of Work.
"""

from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from entrypoints.schemas import (
    Requirement, CreateRequirementPayload, CreateFolderPayload,
    EditRequirementPayload, ParamUpdateRequest, FeatureToggleRequest,
    BulkStatusUpdateRequest
)
from config_loader import get_workspace_base
from agent_orchestrator import run_openhands_loop
from service_layer.unit_of_work import AbstractUnitOfWork, SqliteUnitOfWork
from service_layer import services

def get_uow() -> AbstractUnitOfWork:
    return SqliteUnitOfWork()

router = APIRouter()




@router.get("/api/requirements")
def get_requirements():
    uow = SqliteUnitOfWork()
    return services.get_requirements_for_frontend(uow=uow)


@router.post("/api/requirements")
def update_requirements(reqs: List[Requirement]):
    uow = SqliteUnitOfWork()
    services.update_requirements(reqs, uow=uow)
    return {"status": "ok"}


@router.delete("/api/requirements/{req_id}")
def delete_requirement(req_id: str):
    uow = SqliteUnitOfWork()
    services.delete_requirement(req_id, uow=uow)
    return {"status": "deleted"}


@router.post("/api/requirements/synthesize-from-tests")
def synthesize_requirements(background_tasks: BackgroundTasks):
    """Run the reverse-TDD synthesizer on the active project's test suite."""
    workspace = get_workspace_base()

    def _run_synthesis():
        services.synthesize_requirements_task(workspace)

    background_tasks.add_task(_run_synthesis)
    return {"success": True, "message": "Requirement synthesis started in background."}


@router.post("/api/create-folder")
def create_folder(payload: CreateFolderPayload):
    uow = SqliteUnitOfWork()
    folder = services.create_folder(
        title=payload.title,
        description=payload.description,
        parent_id=payload.parentId,
        uow=uow
    )
    return {"success": True, "id": folder.id}


@router.post("/api/requirements/{req_id}/move")
def move_requirement(req_id: str, payload: dict):
    uow = SqliteUnitOfWork()
    parent_id = payload.get("parentId")
    services.move_requirement(req_id=req_id, parent_id=parent_id, uow=uow)
    return {"success": True}


@router.post("/api/create-requirement")
def create_requirement(payload: CreateRequirementPayload, background_tasks: BackgroundTasks):
    uow = SqliteUnitOfWork()
    req = services.create_requirement_entry(
        title=payload.title,
        description=payload.description,
        parent_id=payload.parentId,
        uow=uow
    )
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "id": req.id, "message": f"Created requirement {req.id} and triggered development loop."}


@router.post("/api/edit-requirement")
def edit_requirement(payload: EditRequirementPayload, background_tasks: BackgroundTasks):
    uow = SqliteUnitOfWork()
    services.edit_requirement(
        req_id=payload.id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        uow=uow
    )
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "message": f"Updated requirement {payload.id}."}


@router.post("/api/requirements/update-param")
def update_requirement_param(req: ParamUpdateRequest):
    """Updates a dynamic domain requirement parameter (like brand title or delivery SLA) and reflects changes in App.tsx and provable.db with a 1-to-1 linked test case."""
    try:
        ws_base = get_workspace_base()
        uow = SqliteUnitOfWork()
        return services.update_requirement_param(
            param_key=req.param_key,
            value=req.value,
            ws_base=ws_base,
            generate_files=True,
            uow=uow
        )
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/requirements/toggle-feature")
def toggle_requirement_feature(req: FeatureToggleRequest):
    """Toggles a pre-baked feature capability requirement on or off and updates App.tsx live with a 1-to-1 linked test case."""
    try:
        ws_base = get_workspace_base()
        uow = SqliteUnitOfWork()
        return services.toggle_requirement_feature(
            feature_id=req.feature_id,
            enabled=req.enabled,
            ws_base=ws_base,
            generate_files=True,
            uow=uow
        )
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/api/requirements/{req_id}/events")
def get_requirement_events(req_id: str, uow: AbstractUnitOfWork = Depends(get_uow)):
    """Fetches domain event audit log for a specific aggregate root."""
    try:
        events_list = services.get_requirement_events_service(req_id=req_id, uow=uow)
        return {"req_id": req_id, "events": events_list}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/requirements/bulk-status-update")
def bulk_status_update(payload: BulkStatusUpdateRequest, uow: AbstractUnitOfWork = Depends(get_uow)):
    """Atomically updates statuses for multiple requirements via Unit of Work."""
    try:
        updated = services.update_requirements_bulk_status_service(
            req_ids=payload.req_ids,
            target_status=payload.target_status,
            uow=uow
        )
        return {"success": True, "updated_count": len(updated), "status": payload.target_status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




