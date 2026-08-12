"""
Event Handlers — Service-layer handlers for reacting to Domain Events.
"""

import domain.events as events
from service_layer.unit_of_work import AbstractUnitOfWork
from adapters.workspace import AbstractWorkspaceAdapter

def sync_sdoc_handler(
    event: events.Event,
    uow: AbstractUnitOfWork,
    workspace: AbstractWorkspaceAdapter
) -> None:
    workspace.sync_sdoc(uow)

def sync_app_shell_handler(
    event: events.Event,
    uow: AbstractUnitOfWork,
    workspace: AbstractWorkspaceAdapter
) -> None:
    workspace.sync_app_shell(uow)

def trigger_agent_loop_handler(
    event: events.Event,
    uow: AbstractUnitOfWork,
    workspace: AbstractWorkspaceAdapter
) -> None:
    ticket_id = getattr(event, 'req_id', None)
    workspace.trigger_agent_loop(ticket_id=ticket_id)

def run_test_suite_handler(
    event: events.Event,
    uow: AbstractUnitOfWork,
    workspace: AbstractWorkspaceAdapter
) -> None:
    ticket_id = getattr(event, 'req_id', None)
    workspace.run_test_suite(test_id=ticket_id)
