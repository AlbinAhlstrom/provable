"""Games stored in SQLite: one row per game, the game's storage form as JSON."""
from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional, Union

from src.domain.game import Game


class SqliteGameRepository:
    def __init__(self, path: Union[str, Path]):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS games ("
                " id TEXT PRIMARY KEY,"
                " created_at REAL NOT NULL,"
                " body TEXT NOT NULL)"
            )
            db.execute("CREATE INDEX IF NOT EXISTS games_created ON games (created_at DESC)")

    def add(self, game: Game) -> None:
        with closing(self._connect()) as db, db:
            db.execute(
                "INSERT INTO games (id, created_at, body) VALUES (?, ?, ?)",
                (game.id, game.created_at, json.dumps(game.to_dict())),
            )

    def save(self, game: Game) -> None:
        with closing(self._connect()) as db, db:
            cursor = db.execute(
                "UPDATE games SET body = ? WHERE id = ?", (json.dumps(game.to_dict()), game.id)
            )
            if cursor.rowcount != 1:
                raise KeyError(f"No stored game with id {game.id!r}")

    def get(self, game_id: str) -> Optional[Game]:
        with closing(self._connect()) as db:
            row = db.execute("SELECT body FROM games WHERE id = ?", (game_id,)).fetchone()
        return None if row is None else Game.from_dict(json.loads(row[0]))

    def list(self, limit: Optional[int] = None) -> list[Game]:
        query = "SELECT body FROM games ORDER BY created_at DESC, rowid DESC"
        params: tuple = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        with closing(self._connect()) as db:
            rows = db.execute(query, params).fetchall()
        return [Game.from_dict(json.loads(body)) for (body,) in rows]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path, timeout=10)
