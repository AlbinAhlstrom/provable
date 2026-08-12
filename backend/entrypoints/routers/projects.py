"""
Projects API Router — Manages local project workspaces, workspace switches, settings, and resets via DDD Service Layer & Unit of Work.
"""

from fastapi import APIRouter, BackgroundTasks
from entrypoints.schemas import ProjectSwitchPayload, ProjectAddPayload
from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services

router = APIRouter()


@router.get("/api/projects")
def list_projects():
    """Return all registered projects and which one is currently active."""
    uow = SqliteUnitOfWork()
    return services.list_projects(uow=uow)


@router.get("/api/project/settings")
def get_active_project_settings():
    """Return configuration for the currently active project."""
    uow = SqliteUnitOfWork()
    return services.get_active_project_settings(uow=uow)


@router.post("/api/projects/switch")
def switch_project(payload: ProjectSwitchPayload, background_tasks: BackgroundTasks):
    """Switch the active project workspace, re-initialise the DB, and re-sync requirements."""
    uow = SqliteUnitOfWork()
    return services.switch_project(path=payload.path, uow=uow, background_tasks=background_tasks)


@router.post("/api/projects/add")
def add_project_endpoint(payload: ProjectAddPayload, background_tasks: BackgroundTasks):
    """Onboard a new local project folder (runs the full onboarding pipeline in background)."""
    uow = SqliteUnitOfWork()
    return services.add_project(path=payload.path, run_synthesis=payload.run_synthesis, uow=uow, background_tasks=background_tasks)


@router.post("/api/projects/reset-all")
def reset_all_projects():
    """Reset / clear requirements, test cases, and generated code in active project."""
    uow = SqliteUnitOfWork()
    return services.reset_all_projects(uow=uow)
