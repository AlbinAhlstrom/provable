"""
Wayfinder API Router — Interactive BDD Architecture Canvas & Frontier Navigation.
Exposes endpoints to generate, inspect, lock, and synthesize domain graphs.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services
from onboarding.wayfinder import (
    BddClause,
    WayfinderGraphState,
    generate_wayfinder_graph,
    lock_wayfinder_ticket,
    sync_locked_tickets_to_rule_deck
)

router = APIRouter(prefix="/api/wayfinder", tags=["Wayfinder Architectural Canvas"])

# In-memory session state for active Wayfinder navigation
_active_graph: Optional[WayfinderGraphState] = None


class GenerateGraphRequest(BaseModel):
    pitch: str = Field(..., description="Natural language business pitch")


class LockTicketRequest(BaseModel):
    ticket_id: str
    bdd: Dict[str, Any]


@router.post("/generate")
def generate_graph_endpoint(req: GenerateGraphRequest):
    """Generates initial 3-zone Wayfinder Graph with prefilled BDD templates."""
    global _active_graph
    if not req.pitch.strip():
        raise HTTPException(status_code=400, detail="Business pitch cannot be empty.")

    graph = generate_wayfinder_graph(req.pitch.strip())
    _active_graph = graph
    return graph.to_dict()


@router.get("/state")
def get_graph_state_endpoint():
    """Returns the current active Wayfinder graph state."""
    global _active_graph
    if _active_graph is None:
        # Check if kickstart has an existing pitch to hydrate
        uow = SqliteUnitOfWork()
        with uow:
            state = uow.kickstart.get()
            if state and state.business_pitch:
                _active_graph = generate_wayfinder_graph(state.business_pitch)

    if _active_graph is None:
        # Default starter graph
        _active_graph = generate_wayfinder_graph("Boutique Hotel Booking & Housekeeping Engine")

    return _active_graph.to_dict()


@router.post("/lock")
def lock_ticket_endpoint(req: LockTicketRequest):
    """Locks a ticket on the active frontier, un-fogs dependent nodes, and syncs to Living Deck."""
    global _active_graph
    if _active_graph is None:
        raise HTTPException(status_code=400, detail="No active Wayfinder graph session found. Please call /generate first.")

    try:
        resolved_bdd = BddClause.from_dict(req.bdd)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid BDD clause format: {str(e)}")

    try:
        updated_graph = lock_wayfinder_ticket(_active_graph, req.ticket_id, resolved_bdd)
        _active_graph = updated_graph

        # Synchronize locked BDD rules to the Living Deck
        uow = SqliteUnitOfWork()
        sync_locked_tickets_to_rule_deck(updated_graph, uow)

        return updated_graph.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to lock ticket: {str(e)}")


@router.post("/synthesize")
def synthesize_wayfinder_endpoint():
    """Compiles the charted Wayfinder architecture directly into the verified application stack."""
    global _active_graph
    if _active_graph is None:
        raise HTTPException(status_code=400, detail="No active Wayfinder graph session found.")

    uow = SqliteUnitOfWork()
    # 1. Sync any remaining locked tickets
    sync_locked_tickets_to_rule_deck(_active_graph, uow)

    # 2. Extract locked architectural & behavioral decisions
    answers = {}
    for t in _active_graph.get_locked_tickets():
        bdd = t.resolved_bdd or t.bdd_template
        if bdd:
            answers[t.title] = f"GIVEN {bdd.given} | WHEN {bdd.when} | THEN {bdd.then}" + (f" | UNLESS {bdd.unless}" if bdd.unless else "")
        else:
            answers[t.title] = "Locked by user"

    # 3. Trigger kickstart synthesis with domain parameters
    try:
        from service_layer.execution_router import ExecutionRouter, TaskIntent
        router_engine = ExecutionRouter()
        routing_decision = router_engine.route_task(
            intent=TaskIntent.GREENFIELD_ONE_SHOT,
            prompt=_active_graph.pitch
        )

        result = services.kickstart_domain_and_scaffold(
            pitch=_active_graph.pitch,
            uow=uow,
            mode="guided",
            answers=answers
        )
        return {
            "success": True,
            "message": "Domain architecture successfully synthesized from Wayfinder decision map!",
            "engine_used": routing_decision.get("engine", "NATIVE_SCAFFOLD"),
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "detail": str(e)
        }


class ExecuteTicketRequest(BaseModel):
    ticket_id: str
    workspace_path: Optional[str] = None


@router.post("/execute-ticket")
def execute_ticket_endpoint(req: ExecuteTicketRequest):
    """
    Executes a locked Wayfinder BDD invariant ticket using Aider precision editing
    (or native rule mutation fallback) with automated verification and git rollback.
    """
    global _active_graph
    if _active_graph is None:
        raise HTTPException(status_code=400, detail="No active Wayfinder graph session found.")

    ticket = next((t for t in _active_graph.tickets if t.id == req.ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket '{req.ticket_id}' not found.")

    bdd = ticket.resolved_bdd or ticket.bdd_template
    if not bdd:
        raise HTTPException(status_code=400, detail="Ticket has no BDD contract to execute.")

    from config_loader import get_workspace_base
    ws_base = req.workspace_path or get_workspace_base()

    from service_layer.execution_router import ExecutionRouter, TaskIntent
    router_engine = ExecutionRouter()

    result = router_engine.route_task(
        intent=TaskIntent.PRECISION_EDIT,
        prompt=f"Implement invariant for {ticket.title}",
        target_files=["domain/model.py"],
        bdd_clause=bdd,
        workspace_path=ws_base
    )

    return {
        "success": True,
        "ticket_id": ticket.id,
        "execution_result": result
    }
