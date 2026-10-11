"""HTTP face of the game. Each action endpoint: load the game, call the domain, save, return.

Run from the project folder:  python -m uvicorn src.app:app --port 8101
"""
from __future__ import annotations

import os
import secrets
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Optional, Protocol

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.adapters.sqlite_repository import SqliteGameRepository
from src.domain.game import (
    FIRST_AREA,
    MAX_COLS,
    MAX_ROWS,
    MIN_SIDE,
    PRESETS,
    Game,
    GameError,
    GameOver,
)
from src.domain.stats import summarize

ROOT = Path(__file__).resolve().parent.parent


class GameRepository(Protocol):
    def add(self, game: Game) -> None: ...
    def save(self, game: Game) -> None: ...
    def get(self, game_id: str) -> Optional[Game]: ...
    def list(self, limit: Optional[int] = None) -> list[Game]: ...


class NewGame(BaseModel):
    difficulty: str = "beginner"
    rows: Optional[int] = None
    cols: Optional[int] = None
    mines: Optional[int] = None


class CellRef(BaseModel):
    row: int
    col: int


def create_app(
    repository: Optional[GameRepository] = None,
    clock: Callable[[], float] = time.time,
    new_seed: Callable[[], int] = lambda: secrets.randbits(63),
    new_id: Callable[[], str] = lambda: uuid.uuid4().hex,
) -> FastAPI:
    repo: GameRepository = repository or SqliteGameRepository(
        os.environ.get("MINESWEEPER_DB", ROOT / "data" / "minesweeper.db")
    )
    app = FastAPI(title="Minesweeper")
    # One action at a time: load-change-save must not interleave for the same game.
    turn = threading.Lock()

    @app.exception_handler(GameError)
    def rule_refused(_: Request, error: GameError) -> JSONResponse:
        status = 409 if isinstance(error, GameOver) else 422
        return JSONResponse(status_code=status, content={"detail": str(error)})

    @app.exception_handler(RequestValidationError)
    def bad_request(_: Request, error: RequestValidationError) -> JSONResponse:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in e['loc'][1:]) or 'body'}: {e['msg']}"
            for e in error.errors()
        )
        return JSONResponse(status_code=422, content={"detail": problems})

    def load(game_id: str) -> Game:
        game = repo.get(game_id)
        if game is None:
            raise HTTPException(status_code=404, detail="No such game.")
        return game

    def act(game_id: str, move: Callable[[Game, float], None]) -> dict[str, Any]:
        with turn:
            game = load(game_id)
            now = clock()
            move(game, now)
            repo.save(game)
        return game.view(now).as_dict()

    @app.get("/api/difficulties")
    def difficulties() -> dict[str, Any]:
        return {
            "presets": [
                {"key": key, "rows": rows, "cols": cols, "mines": mines}
                for key, (rows, cols, mines) in PRESETS.items()
            ],
            "custom": {
                "min_side": MIN_SIDE,
                "max_rows": MAX_ROWS,
                "max_cols": MAX_COLS,
                "first_area": FIRST_AREA,
            },
        }

    @app.post("/api/games", status_code=201)
    def create_game(body: NewGame) -> dict[str, Any]:
        now = clock()
        game = Game.new(
            id=new_id(), difficulty=body.difficulty, seed=new_seed(), now=now,
            rows=body.rows, cols=body.cols, mines=body.mines,
        )
        repo.add(game)
        return game.view(now).as_dict()

    @app.get("/api/games")
    def list_games(limit: int = 50) -> list[dict[str, Any]]:
        now = clock()
        summaries = []
        for game in repo.list(limit=max(1, min(limit, 500))):
            summary = game.view(now).as_dict()
            del summary["board"]
            summaries.append(summary)
        return summaries

    @app.get("/api/games/{game_id}")
    def get_game(game_id: str) -> dict[str, Any]:
        return load(game_id).view(clock()).as_dict()

    @app.post("/api/games/{game_id}/reveal")
    def reveal(game_id: str, cell: CellRef) -> dict[str, Any]:
        return act(game_id, lambda game, now: game.reveal(cell.row, cell.col, now))

    @app.post("/api/games/{game_id}/flag")
    def flag(game_id: str, cell: CellRef) -> dict[str, Any]:
        return act(game_id, lambda game, now: game.toggle_flag(cell.row, cell.col))

    @app.post("/api/games/{game_id}/chord")
    def chord(game_id: str, cell: CellRef) -> dict[str, Any]:
        return act(game_id, lambda game, now: game.chord(cell.row, cell.col, now))

    @app.get("/api/stats")
    def stats() -> dict[str, Any]:
        return {key: value.as_dict() for key, value in summarize(repo.list()).items()}

    # When the frontend has been built, serve it too, so one process runs the product.
    dist = ROOT / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")

    return app


def __getattr__(name: str) -> Any:
    """`uvicorn src.app:app` builds the app on first use; importing the module opens no file."""
    if name == "app":
        globals()["app"] = create_app()
        return globals()["app"]
    raise AttributeError(name)
