"""Use case: bring the current app's routers and API clients up to today's generator (`onboarding/wiring.py`)."""

from typing import Any, Dict, Optional

from onboarding.router_engine import DomainStructureSchema
from onboarding.wiring import refresh_wiring
from service_layer.unit_of_work import AbstractUnitOfWork


def refresh_app_wiring(uow: AbstractUnitOfWork, workspace_dir: Optional[str] = None) -> Dict[str, Any]:
    """Writes the current app's routers and clients again from the decomposition and the actions its kickstart
    kept (a client carries one function per action, which the page calls)."""
    if workspace_dir is None:
        from config_loader import get_workspace_base
        workspace_dir = get_workspace_base()
    with uow:
        state = uow.kickstart.get()
        kept, actions = state.structure, (state.action_manifest or {}).get("actions")
    if not kept:
        return {"success": False, "error": "there is no decomposition to write the wiring from: run a kickstart first"}
    return {"success": True,
            "rewritten": refresh_wiring(DomainStructureSchema.model_validate(kept), workspace_dir, actions=actions)}
