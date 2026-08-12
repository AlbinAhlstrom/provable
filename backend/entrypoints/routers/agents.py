"""
Agents & Task Execution API Router — Handles triggering agent runs, checking agent status, logs, and ticket control.
"""

from fastapi import APIRouter, BackgroundTasks
from service_layer import services
from service_layer.unit_of_work import SqliteUnitOfWork

router = APIRouter()


@router.get("/api/logs/{ticket_id}")
def get_logs(ticket_id: str):
    uow = SqliteUnitOfWork()
    return services.get_agent_logs(ticket_id=ticket_id, uow=uow)


@router.get("/api/agent-status")
def get_agent_status():
    uow = SqliteUnitOfWork()
    return services.get_agent_status(uow=uow)


@router.post("/api/trigger-agents")
def trigger_agents(background_tasks: BackgroundTasks):
    uow = SqliteUnitOfWork()
    return services.trigger_agents(uow=uow, background_tasks=background_tasks)


@router.post("/api/trigger-ticket/{ticket_id}")
def trigger_ticket(ticket_id: str, background_tasks: BackgroundTasks):
    uow = SqliteUnitOfWork()
    return services.trigger_ticket(ticket_id=ticket_id, uow=uow, background_tasks=background_tasks)


@router.post("/api/abandon-ticket/{ticket_id}")
def abandon_ticket(ticket_id: str):
    uow = SqliteUnitOfWork()
    return services.abandon_ticket(ticket_id=ticket_id, uow=uow)

