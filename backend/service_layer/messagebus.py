"""
MessageBus Pattern — Dispatches domain events to registered event handlers.
"""

from typing import Dict, Type, List, Callable, Optional
import domain.events as events
from service_layer.unit_of_work import AbstractUnitOfWork
from adapters.workspace import AbstractWorkspaceAdapter, LocalWorkspaceAdapter
from service_layer import handlers

EVENT_HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.RequirementCreated: [handlers.sync_sdoc_handler],
    events.RequirementEdited: [handlers.sync_sdoc_handler, handlers.sync_app_shell_handler],
    events.RequirementMoved: [handlers.sync_sdoc_handler],
    events.RequirementRejected: [handlers.sync_sdoc_handler, handlers.trigger_agent_loop_handler],
    events.ComponentAdded: [handlers.sync_sdoc_handler, handlers.sync_app_shell_handler],
    events.ComponentDeleted: [handlers.sync_sdoc_handler, handlers.sync_app_shell_handler],
}

def handle(
    event: events.Event,
    uow: AbstractUnitOfWork,
    workspace: Optional[AbstractWorkspaceAdapter] = None
) -> None:
    if workspace is None:
        workspace = LocalWorkspaceAdapter()

    queue = [event]
    queue.extend(list(uow.collect_new_events()))

    while queue:
        ev = queue.pop(0)
        handlers_list = EVENT_HANDLERS.get(type(ev), [])
        for handler in handlers_list:
            handler(ev, uow=uow, workspace=workspace)
            queue.extend(list(uow.collect_new_events()))
