"""
Domain Model: Game (Aggregate Root)
Single Responsibility Principle (SRP) compliant domain model.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any, Union, Set, Tuple, Callable
import random


try:
    from src.domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
    from src.domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
except ImportError:
    try:
        from domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
        from domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
    except ImportError:
        pass

DIFFICULTY_SETTINGS: Dict[str, Tuple[int, int, int]] = {
    "Beginner": (9, 9, 10),
    "Intermediate": (16, 16, 40),
    "Expert": (16, 30, 99),
}
class InvalidActionError(Exception):
    """Raised when an action is refused because the game has ended."""


@dataclass
class Game:
    """Game.

    cells: the Cell records this Game owns, one dict each with the keys id (str), row (int), column (int), has_mine (bool), adjacent_mine_count (int), state (str).
    """
    id: str
    difficulty: str = "Beginner"
    status: str = "ready"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    elapsed_seconds: int = 0
    mine_count: int = 10
    flag_count: int = 0
    cells: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

    def start_game(self, difficulty: str) -> None:
        """Discard the current session and set up a fresh board.

        Args:
            difficulty: One of Beginner, Intermediate or Expert.
        """
        rows, columns, mines = self._settings_for(difficulty)
        self.difficulty = difficulty
        self.status = "ready"
        self.started_at = None
        self.ended_at = None
        self.elapsed_seconds = 0
        self.mine_count = mines
        self.flag_count = 0
        self.cells = [
            self._make_cell(row, column)
            for row in range(rows)
            for column in range(columns)
        ]

    def reveal_cell(
        self, row: int, column: int, now: Optional[str] = None
    ) -> None:
        """Reveal a hidden cell, laying out mines on the first reveal.

        Args:
            row: Row index of the target cell.
            column: Column index of the target cell.
            now: Optional ISO timestamp used as the current moment.

        Raises:
            InvalidActionError: If the game has already ended.
        """
        if self.status in ("won", "lost"):
            raise InvalidActionError(
                f"Cannot reveal a cell when the game is {self.status}."
            )
        moment = now if now is not None else self._now()
        rows, columns, _ = self._board_settings()
        if not self._in_bounds(row, column, rows, columns):
            return
        if self.status == "ready":
            self._lay_out_board(row, column)
            self.status = "in_progress"
            self.started_at = moment
        target = self._cell_at(row, column)
        if target is None or target["state"] != "hidden":
            return
        if target["has_mine"]:
            target["state"] = "revealed"
            self._expose_mines_on_loss()
            self._finish("lost", moment)
            return
        self._open_region(row, column, rows, columns)
        if all(
            cell["state"] == "revealed"
            for cell in self.cells
            if not cell["has_mine"]
        ):
            self._flag_remaining_mines()
            self._finish("won", moment)

    def toggle_flag(
        self, row: int, column: int, now: Optional[str] = None
    ) -> None:
        """Cycle a hidden cell to flagged or a flagged cell to hidden.

        Args:
            row: Row index of the target cell.
            column: Column index of the target cell.
            now: Optional ISO timestamp, accepted for interface symmetry.

        Raises:
            InvalidActionError: If the game has already ended.
        """
        if self.status not in ("ready", "in_progress"):
            raise InvalidActionError(
                f"Cannot flag a cell when the game is {self.status}."
            )
        cell = self._cell_at(row, column)
        if cell is None:
            return
        if cell["state"] == "hidden":
            cell["state"] = "flagged"
            self.flag_count += 1
        elif cell["state"] == "flagged":
            cell["state"] = "hidden"
            self.flag_count -= 1

    @staticmethod
    def _settings_for(difficulty: str) -> Tuple[int, int, int]:
        if difficulty not in DIFFICULTY_SETTINGS:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        return DIFFICULTY_SETTINGS[difficulty]

    def _board_settings(self) -> Tuple[int, int, int]:
        return self._settings_for(self.difficulty)

    @staticmethod
    def _in_bounds(row: int, column: int, rows: int, columns: int) -> bool:
        return 0 <= row < rows and 0 <= column < columns

    @staticmethod
    def _make_cell(
        row: int,
        column: int,
        state: str = "hidden",
        has_mine: bool = False,
        adjacent_mine_count: int = 0,
    ) -> Dict[str, Any]:
        return {
            "id": f"{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": has_mine,
            "adjacent_mine_count": adjacent_mine_count,
            "state": state,
        }

    @staticmethod
    def _neighbours(
        row: int, column: int, rows: int, columns: int
    ) -> List[Tuple[int, int]]:
        return [
            (r, c)
            for r in range(row - 1, row + 2)
            for c in range(column - 1, column + 2)
            if (r, c) != (row, column) and 0 <= r < rows and 0 <= c < columns
        ]

    def _cell_at(self, row: int, column: int) -> Optional[Dict[str, Any]]:
        for cell in self.cells:
            if cell["row"] == row and cell["column"] == column:
                return cell
        return None

    def _lay_out_board(self, row: int, column: int) -> None:
        rows, columns, mines = self._board_settings()
        self.mine_count = mines
        safe = {(row, column)} | set(
            self._neighbours(row, column, rows, columns)
        )
        candidates = [
            (r, c)
            for r in range(rows)
            for c in range(columns)
            if (r, c) not in safe
        ]
        mine_positions = set(random.sample(candidates, mines))
        self.cells = [
            self._make_cell(
                r,
                c,
                has_mine=(r, c) in mine_positions,
                adjacent_mine_count=sum(
                    1
                    for n in self._neighbours(r, c, rows, columns)
                    if n in mine_positions
                ),
            )
            for r in range(rows)
            for c in range(columns)
        ]

    def _open_region(self, row: int, column: int, rows: int, columns: int) -> None:
        pending = [(row, column)]
        while pending:
            r, c = pending.pop()
            cell = self._cell_at(r, c)
            if cell is None or cell["state"] != "hidden" or cell["has_mine"]:
                continue
            cell["state"] = "revealed"
            if cell["adjacent_mine_count"] == 0:
                pending.extend(self._neighbours(r, c, rows, columns))

    def _finish(self, outcome: str, ended: str) -> None:
        self.status = outcome
        self.ended_at = ended
        if self.started_at is not None:
            started = datetime.fromisoformat(self.started_at)
            finished = datetime.fromisoformat(ended)
            self.elapsed_seconds = int((finished - started).total_seconds())

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def mine_counter(self) -> int:
        """Return the mine counter, which may be negative.

        Returns:
            The mine count minus the flag count.
        """
        return self.mine_count - self.flag_count

    def timer_display(self) -> int:
        """Return the elapsed seconds capped for display.

        Returns:
            The elapsed seconds, never more than 999.
        """
        return min(self.elapsed_seconds, 999)

    def _expose_mines_on_loss(self) -> None:
        for cell in self.cells:
            if cell["has_mine"]:
                cell["state"] = "revealed"
            elif cell["state"] == "flagged":
                cell["state"] = "wrong"

    def _flag_remaining_mines(self) -> None:
        for cell in self.cells:
            if cell["has_mine"] and cell["state"] == "hidden":
                cell["state"] = "flagged"
                self.flag_count += 1
