"""
FastAPI Router for Game (Auto-projected from domain model).
"""

import inspect
import json
import os
import re
import uuid
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from src.entrypoints.schemas import GameCreateSchema, GameResponseSchema
from src.domain.game import Game
from src.service_layer.unit_of_work import FakeUnitOfWork
from src.adapters import record_store

router = APIRouter(prefix="/api/games", tags=["Game"])

# Active in-memory UoW store for fast runtime execution
_uow = FakeUnitOfWork()

# Records live in memory and are saved after every change (src/adapters/record_store.py), so a restart of this
# server loses nothing. Starting content (src/seed_data.json, written at generation time for entities shown to the
# audience) is read on the first request after the file appears or changes, because the file is written after this
# server has started; a seed file that was already applied is not applied again, so a removed record stays removed.
# The domain decides: a record it rejects is reported loudly and left out, the API stays up.
_SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "seed_data.json")
_seed_state = {"mtime": None, "loaded": False}


def _add_records(records: List[Dict[str, Any]], source: str) -> None:
    repo = getattr(_uow, "games")
    known = {getattr(i, 'id', None) for i in repo.list()}
    for record in records:
        if record.get("id") in known:
            continue
        try:
            repo.add(Game(**record))
        except Exception as exc:
            print(f"[{source}] Game record {record.get('id')!r} was rejected by the domain: {exc}", flush=True)


def _save() -> None:
    record_store.save("games", [i.to_dict() for i in getattr(_uow, "games").list()], _seed_state["mtime"])


def _ensure_seeded() -> None:
    if not _seed_state["loaded"]:
        _seed_state["loaded"] = True
        saved = record_store.load("games")
        _seed_state["mtime"] = saved["seed_mtime"]
        with _uow:
            _add_records(saved["records"], "saved")
            _uow.commit()
    try:
        mtime = os.path.getmtime(_SEED_PATH)
    except OSError:
        return
    if _seed_state["mtime"] == mtime:
        return
    _seed_state["mtime"] = mtime
    with open(_SEED_PATH, encoding="utf-8") as seed_file:
        records = json.load(seed_file).get("Game", [])
    with _uow:
        _add_records(records, "seed")
        _uow.commit()
    _save()


@router.get("", response_model=List[GameResponseSchema])
def list_games():
    _ensure_seeded()
    with _uow:
        items = getattr(_uow, "games").list()
        return [i.to_dict() for i in items]

@router.post("", response_model=GameResponseSchema, status_code=status.HTTP_201_CREATED)
def create_game(payload: GameCreateSchema):
    _ensure_seeded()
    # Only what the client sent: every other field starts as the class itself says (its starting state)
    data = payload.model_dump(exclude_unset=True)
    if "id" in type(payload).model_fields and not data.get("id"):
        data["id"] = uuid.uuid4().hex
    item = Game(**data)
    with _uow:
        getattr(_uow, "games").add(item)
        _uow.commit()
    _save()
    return item.to_dict()

@router.get("/{item_id}", response_model=GameResponseSchema)
def get_game(item_id: str):
    _ensure_seeded()
    with _uow:
        item = getattr(_uow, "games").get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Game not found")
        return item.to_dict()

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(item_id: str):
    _ensure_seeded()
    with _uow:
        repo = getattr(_uow, "games")
        if not repo.get(item_id):
            raise HTTPException(status_code=404, detail="Game not found")
        repo.delete(item_id)
        _uow.commit()
    _save()


class ActionRequest(BaseModel):
    action_type: str = Field(..., description="Name of a public domain method on Game")
    params: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments for that method")


def _public_actions(item) -> Dict[str, Any]:
    return {
        name: member for name, member in inspect.getmembers(item, inspect.ismethod)
        if not name.startswith("_") and name != "to_dict"
    }


@router.post("/{item_id}/action")
def run_game_action(item_id: str, request: ActionRequest):
    """Runs one of the aggregate's own domain methods; the domain decides whether the action is allowed."""
    _ensure_seeded()
    name = re.sub(r"[^a-z0-9]+", "_", request.action_type.strip().lower()).strip("_")
    with _uow:
        item = getattr(_uow, "games").get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Game not found")
        actions = _public_actions(item)
        if name not in actions:
            raise HTTPException(status_code=404, detail=f"Unknown action '{request.action_type}'. Available: {sorted(actions)}")
        method = actions[name]
        try:
            inspect.signature(method).bind(**request.params)
        except TypeError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid parameters for '{name}': {exc}")
        try:
            result = method(**request.params)
        except Exception as exc:  # the domain rejected the action; its state is left as the domain left it
            raise HTTPException(status_code=400, detail=str(exc) or type(exc).__name__)
        _uow.commit()
        _save()
        return {
            "success": True,
            "state": item.to_dict(),
            "message": result if isinstance(result, str) else f"{request.action_type} completed",
        }
