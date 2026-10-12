"""
Domain Model: GameSession (Aggregate Root)
Single Responsibility Principle (SRP) compliant domain model.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any, Union, Set, Tuple, Callable
import random

from datetime import datetime, timezone


try:
    from src.domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
    from src.domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
except ImportError:
    try:
        from domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
        from domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
    except ImportError:
        pass

DIFFICULTY_PRESETS = {
    "beginner": (9, 9, 10),
    "intermediate": (16, 16, 40),
    "expert": (16, 30, 99),
}
ACTIVE_STATUSES = ("ready", "in_progress")


class GameSessionError(Exception):
    """GameSessionError.

    Base class for every refusal raised by a GameSession.
    """


class ActionNotAllowedError(GameSessionError):
    """ActionNotAllowedError.

    Raised when an action is not permitted in the current status or cell state.
    """


class InvalidDifficultyError(GameSessionError):
    """InvalidDifficultyError.

    Raised when a difficulty does not match its preset or cannot hold its mines.
    """


class CellOutOfBoundsError(GameSessionError):
    """CellOutOfBoundsError.

    Raised when a row or column lies outside the board.
    """


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string.

    Returns:
        The current UTC timestamp.
    """
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GameSession:
    """GameSession.

    cells: the Cell records this GameSession owns, one dict each with the keys id (str), row (int), column (int), has_mine (bool), adjacent_mine_count (int), state (str).
    """
    id: str
    difficulty_id: str
    rows: int
    columns: int
    mine_count: int
    status: str = "ready"
    flag_count: int = 0
    elapsed_seconds: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    cells: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }
    def __post_init__(self) -> None:
        """Build the hidden board when no cell records were supplied.

        Returns:
            None.
        """
        if not self.cells:
            self.cells = self._build_hidden_board()

    def start_new_game(
        self, difficulty_id: str, rows: int, columns: int, mine_count: int
    ) -> None:
        """Replace the board with a new hidden board for a difficulty preset.

        Args:
            difficulty_id: The chosen difficulty name.
            rows: The number of rows, which must match the preset.
            columns: The number of columns, which must match the preset.
            mine_count: The number of mines, which must match the preset.

        Raises:
            InvalidDifficultyError: If the difficulty is unknown or the
                dimensions do not match its preset.
        """
        preset = DIFFICULTY_PRESETS.get(difficulty_id)
        if preset is None or preset != (rows, columns, mine_count):
            raise InvalidDifficultyError(
                f"values do not match difficulty {difficulty_id!r}"
            )
        self.difficulty_id = difficulty_id
        self.rows = rows
        self.columns = columns
        self.mine_count = mine_count
        self.status = "ready"
        self.flag_count = 0
        self.elapsed_seconds = 0
        self.started_at = None
        self.ended_at = None
        self.cells = self._build_hidden_board()

    def reveal_cell(self, row: int, column: int) -> None:
        """Reveal a hidden, unflagged cell, placing mines on the first reveal.

        Args:
            row: The row of the cell.
            column: The column of the cell.

        Raises:
            ActionNotAllowedError: If the status or cell state forbids it.
            CellOutOfBoundsError: If the position is outside the board.
        """
        if self.status not in ACTIVE_STATUSES:
            raise ActionNotAllowedError(
                f"cannot reveal a cell while status is {self.status!r}"
            )
        index = self._index()
        cell = self._cell_at(index, row, column)
        if cell["state"] != "hidden":
            raise ActionNotAllowedError(
                f"cannot reveal a cell in state {cell['state']!r}"
            )
        if self.status == "ready":
            self._place_mines(row, column)
            self.status = "in_progress"
            self.started_at = _utc_now_iso()
        if cell["has_mine"]:
            cell["state"] = "revealed"
            self.status = "lost"
            self.ended_at = _utc_now_iso()
            return
        self._reveal_region(index, cell)
        if self._all_safe_cells_revealed():
            self.status = "won"
            self.ended_at = _utc_now_iso()

    def toggle_flag(self, row: int, column: int) -> None:
        """Toggle the flag on a hidden or flagged cell.

        Args:
            row: The row of the cell.
            column: The column of the cell.

        Raises:
            ActionNotAllowedError: If the status or cell state forbids it.
            CellOutOfBoundsError: If the position is outside the board.
        """
        if self.status not in ACTIVE_STATUSES:
            raise ActionNotAllowedError(
                f"cannot flag a cell while status is {self.status!r}"
            )
        cell = self._cell_at(self._index(), row, column)
        if cell["state"] == "hidden":
            cell["state"] = "flagged"
            self.flag_count += 1
        elif cell["state"] == "flagged":
            cell["state"] = "hidden"
            self.flag_count -= 1
        else:
            raise ActionNotAllowedError(
                f"cannot flag a cell in state {cell['state']!r}"
            )

    def abandon_game(self) -> None:
        """End the current game with no result.

        Raises:
            ActionNotAllowedError: If the status is not ready or in_progress.
        """
        if self.status not in ACTIVE_STATUSES:
            raise ActionNotAllowedError(
                f"cannot abandon a game while status is {self.status!r}"
            )
        self.status = "abandoned"
        self.ended_at = _utc_now_iso()

    def _build_hidden_board(self) -> List[Dict[str, Any]]:
        """Create one hidden cell record for every board position.

        Returns:
            The list of hidden cell records.
        """
        return [
            {
                "id": f"{row}-{column}",
                "row": row,
                "column": column,
                "has_mine": False,
                "adjacent_mine_count": 0,
                "state": "hidden",
            }
            for row in range(self.rows)
            for column in range(self.columns)
        ]

    def _index(self) -> Dict[Tuple[int, int], Dict[str, Any]]:
        """Index the cell records by their position.

        Returns:
            A mapping from (row, column) to the cell record.
        """
        return {(cell["row"], cell["column"]): cell for cell in self.cells}

    def _cell_at(
        self,
        index: Dict[Tuple[int, int], Dict[str, Any]],
        row: int,
        column: int,
    ) -> Dict[str, Any]:
        """Look up a cell record, refusing positions off the board.

        Args:
            index: The position index of the board.
            row: The row of the cell.
            column: The column of the cell.

        Returns:
            The cell record at the position.

        Raises:
            CellOutOfBoundsError: If no cell exists at the position.
        """
        cell = index.get((row, column))
        if cell is None:
            raise CellOutOfBoundsError(f"no cell at ({row}, {column})")
        return cell

    def _neighbour_positions(
        self, row: int, column: int
    ) -> List[Tuple[int, int]]:
        """List the on-board positions adjacent to a cell.

        Args:
            row: The row of the cell.
            column: The column of the cell.

        Returns:
            The positions of the neighbouring cells.
        """
        return [
            (row + d_row, column + d_column)
            for d_row in (-1, 0, 1)
            for d_column in (-1, 0, 1)
            if (d_row, d_column) != (0, 0)
            and 0 <= row + d_row < self.rows
            and 0 <= column + d_column < self.columns
        ]

    def _place_mines(self, first_row: int, first_column: int) -> None:
        """Place mines at random, avoiding the first revealed cell.

        Args:
            first_row: The row of the first revealed cell.
            first_column: The column of the first revealed cell.

        Raises:
            InvalidDifficultyError: If the mines cannot leave the first cell
                free.
        """
        if self.mine_count >= len(self.cells):
            raise InvalidDifficultyError(
                "mine_count leaves no room for a safe first reveal"
            )
        candidates = [
            (cell["row"], cell["column"])
            for cell in self.cells
            if (cell["row"], cell["column"]) != (first_row, first_column)
        ]
        mine_positions = set(random.sample(candidates, self.mine_count))
        for cell in self.cells:
            cell["has_mine"] = (cell["row"], cell["column"]) in mine_positions
        index = self._index()
        for cell in self.cells:
            cell["adjacent_mine_count"] = sum(
                1
                for position in self._neighbour_positions(
                    cell["row"], cell["column"]
                )
                if index[position]["has_mine"]
            )

    def _reveal_region(
        self,
        index: Dict[Tuple[int, int], Dict[str, Any]],
        start: Dict[str, Any],
    ) -> None:
        """Reveal a safe cell and expand through connected zero-count cells.

        Args:
            index: The position index of the board.
            start: The safe hidden cell to reveal.
        """
        pending = [start]
        while pending:
            cell = pending.pop()
            if cell["state"] != "hidden":
                continue
            cell["state"] = "revealed"
            if cell["adjacent_mine_count"] != 0:
                continue
            for position in self._neighbour_positions(
                cell["row"], cell["column"]
            ):
                neighbour = index[position]
                if neighbour["state"] == "hidden":
                    pending.append(neighbour)

    def _all_safe_cells_revealed(self) -> bool:
        """Report whether every safe cell has been revealed.

        Returns:
            True when no safe cell is still hidden or flagged.
        """
        return all(
            cell["state"] == "revealed"
            for cell in self.cells
            if not cell["has_mine"]
        )
