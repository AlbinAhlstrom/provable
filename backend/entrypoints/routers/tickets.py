"""Change tickets (ADR-014): a change to the built app, asked for in a person's words."""

from fastapi import APIRouter
from pydantic import BaseModel

from service_layer import change_tickets
from service_layer.unit_of_work import SqliteUnitOfWork

router = APIRouter(prefix="/api/tickets", tags=["Change tickets"])


class ChangeRequest(BaseModel):
    request: str


@router.post("/plan")
def plan_change(req: ChangeRequest):
    """Plans a change and answers with its card: what was understood and the rules it would add. Changes nothing."""
    return change_tickets.plan_change(req.request, uow=SqliteUnitOfWork())
