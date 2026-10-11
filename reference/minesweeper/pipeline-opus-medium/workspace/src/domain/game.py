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
import uuid


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
    "expert": (30, 16, 99),
}


class CellNotFoundError(Exception):
    """Raised when a row/column pair lies outside the game grid."""


class InvalidConfigurationError(Exception):
    """Raised when a difficulty choice is unknown or out of range."""


def _now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string.

    Returns:
        The current timestamp.
    """
    return datetime.now(timezone.utc).isoformat()


def _resolve_configuration(
    difficulty_id: str,
    width: Optional[int],
    height: Optional[int],
    mine_count: Optional[int],
) -> Tuple[int, int, int]:
    """Resolve a difficulty choice into board dimensions and mine count.

    Args:
        difficulty_id: The chosen difficulty identifier.
        width: Custom width, used only for the custom difficulty.
        height: Custom height, used only for the custom difficulty.
        mine_count: Custom mine count, used only for the custom difficulty.

    Returns:
        A tuple of width, height and mine count.

    Raises:
        InvalidConfigurationError: If the choice is unknown or out of range.
    """
    if difficulty_id in DIFFICULTY_PRESETS:
        return DIFFICULTY_PRESETS[difficulty_id]
    if difficulty_id != "custom":
        raise InvalidConfigurationError(
            f"Unknown difficulty '{difficulty_id}'; choose beginner, "
            f"intermediate, expert or custom"
        )
    if not isinstance(width, int) or isinstance(width, bool) \
            or not 9 <= width <= 30:
        raise InvalidConfigurationError(
            f"Width must be between 9 and 30, got {width}"
        )
    if not isinstance(height, int) or isinstance(height, bool) \
            or not 9 <= height <= 24:
        raise InvalidConfigurationError(
            f"Height must be between 9 and 24, got {height}"
        )
    max_mines = (width - 1) * (height - 1)
    if not isinstance(mine_count, int) or isinstance(mine_count, bool) \
            or not 10 <= mine_count <= max_mines:
        raise InvalidConfigurationError(
            f"Mine count must be between 10 and {max_mines}, got {mine_count}"
        )
    return width, height, mine_count
ALLOWED_STATUS_TRANSITIONS = frozenset(
    {
        ("Ready", "Playing"),
        ("Playing", "Won"),
        ("Playing", "Lost"),
        ("Ready", "Abandoned"),
        ("Playing", "Abandoned"),
    }
)


class InvalidTransitionError(Exception):
    """Raised when a requested game status transition is not allowed."""


@dataclass
class Game:
    """Game.

    cells: the Cell records this Game owns, one dict each with the keys id (str), row (int), column (int), has_mine (bool), adjacent_mine_count (int), state (str).
    """
    id: str
    difficulty_id: str
    width: int
    height: int
    mine_count: int
    remaining_mines: int
    created_at: str
    status: str = "Ready"
    mines_laid: bool = False
    flags_placed: int = 0
    elapsed_seconds: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    struck_cell_id: Optional[str] = None
    cells: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

    def __post_init__(self) -> None:
        """Build the hidden, mine-free grid when no cells are supplied."""
        if not self.cells:
            self.cells = [
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": False,
                    "adjacent_mine_count": 0,
                    "state": "Hidden",
                }
                for r in range(self.height)
                for c in range(self.width)
            ]

    def _is_active(self) -> bool:
        return self.status in ("Ready", "Playing")

    def _cell_at(self, row: int, column: int) -> Dict[str, Any]:
        valid = (
            isinstance(row, int)
            and isinstance(column, int)
            and 0 <= row < self.height
            and 0 <= column < self.width
        )
        if not valid:
            raise CellNotFoundError(
                f"Cell ({row}, {column}) is outside the "
                f"{self.width}x{self.height} grid"
            )
        return self.cells[row * self.width + column]

    def _neighbours(self, target: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = target["row"] + dr
                nc = target["column"] + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    result.append(self.cells[nr * self.width + nc])
        return result

    def _lay_mines(self, safe: Dict[str, Any]) -> None:
        candidates = [cl for cl in self.cells if cl is not safe]
        amount = min(self.mine_count, len(candidates))
        for cl in self.cells:
            cl["has_mine"] = False
        for cl in random.sample(candidates, amount):
            cl["has_mine"] = True
        for cl in self.cells:
            cl["adjacent_mine_count"] = sum(
                1 for n in self._neighbours(cl) if n["has_mine"]
            )
        self.mines_laid = True

    def _reveal(self, target: Dict[str, Any]) -> None:
        if target["has_mine"]:
            target["state"] = "Detonated"
            self.struck_cell_id = target["id"]
            self.transition_to("Lost")
            return
        stack = [target]
        target["state"] = "Opened"
        while stack:
            current = stack.pop()
            if current["adjacent_mine_count"] != 0:
                continue
            for n in self._neighbours(current):
                if n["state"] == "Hidden" and not n["has_mine"]:
                    n["state"] = "Opened"
                    stack.append(n)
        self._check_win()

    def _check_win(self) -> None:
        if any(
            not cl["has_mine"] and cl["state"] != "Opened" for cl in self.cells
        ):
            return
        self.transition_to("Won")
        for cl in self.cells:
            if cl["has_mine"]:
                cl["state"] = "Flagged"
        self.flags_placed = self.mine_count
        self.remaining_mines = 0

    def open_cell(self, row: int, column: int) -> None:
        """Open the cell at the given zero-based position.

        Args:
            row: Zero-based row index.
            column: Zero-based column index.

        Raises:
            CellNotFoundError: If the position lies outside the grid.
        """
        target = self._cell_at(row, column)
        if not self._is_active() or target["state"] != "Hidden":
            return
        if not self.mines_laid:
            self._lay_mines(target)
        if self.status == "Ready":
            self.transition_to("Playing")
        self._reveal(target)

    def toggle_flag(self, row: int, column: int) -> None:
        """Toggle a flag on the cell at the given zero-based position.

        Args:
            row: Zero-based row index.
            column: Zero-based column index.

        Raises:
            CellNotFoundError: If the position lies outside the grid.
        """
        target = self._cell_at(row, column)
        if not self._is_active():
            return
        if target["state"] == "Hidden":
            target["state"] = "Flagged"
            self.flags_placed += 1
        elif target["state"] == "Flagged":
            target["state"] = "Hidden"
            self.flags_placed -= 1
        else:
            return
        self.remaining_mines = self.mine_count - self.flags_placed

    def chord_cell(self, row: int, column: int) -> None:
        """Open all hidden neighbours of a satisfied numbered cell.

        Args:
            row: Zero-based row index.
            column: Zero-based column index.

        Raises:
            CellNotFoundError: If the position lies outside the grid.
        """
        target = self._cell_at(row, column)
        if self.status != "Playing":
            return
        count = target["adjacent_mine_count"]
        if target["state"] != "Opened" or count < 1:
            return
        neighbours = self._neighbours(target)
        flagged = sum(1 for n in neighbours if n["state"] == "Flagged")
        if flagged != count:
            return
        for n in neighbours:
            if self.status != "Playing":
                break
            if n["state"] == "Hidden":
                self._reveal(n)

    def tick(self) -> None:
        """Advance the clock by one second while playing, capped at 999."""
        if self.status == "Playing":
            self.elapsed_seconds = min(999, self.elapsed_seconds + 1)

    def abandon_game(self) -> None:
        """Abandon an active game; finished games are left unchanged."""
        if self._is_active():
            self.transition_to("Abandoned")

    def _new_game(
        self, difficulty_id: str, width: int, height: int, mine_count: int
    ) -> "Game":
        return Game(
            id=str(uuid.uuid4()),
            difficulty_id=difficulty_id,
            width=width,
            height=height,
            mine_count=mine_count,
            remaining_mines=mine_count,
            created_at=_now_iso(),
        )

    def restart_game(self) -> "Game":
        """Abandon this game if active and return a fresh one.

        Returns:
            A new Game with the same configuration in its starting state.
        """
        self.abandon_game()
        return self._new_game(
            self.difficulty_id, self.width, self.height, self.mine_count
        )

    def change_difficulty(
        self,
        difficulty_id: str,
        width: Optional[int],
        height: Optional[int],
        mine_count: Optional[int],
    ) -> "Game":
        """Choose a difficulty and return a new game for it.

        Args:
            difficulty_id: beginner, intermediate, expert or custom.
            width: Custom width (9-30).
            height: Custom height (9-24).
            mine_count: Custom mine count (10 to (width-1)*(height-1)).

        Returns:
            A new Game with the chosen configuration in its starting state.

        Raises:
            InvalidConfigurationError: If the choice is unknown or out of range.
        """
        new_width, new_height, new_mines = _resolve_configuration(
            difficulty_id, width, height, mine_count
        )
        self.abandon_game()
        return self._new_game(difficulty_id, new_width, new_height, new_mines)

    def transition_to(self, status: str) -> None:
        """Move the game to a new status if the transition is allowed.

        Allowed transitions are Ready to Playing, Playing to Won,
        Playing to Lost and Ready or Playing to Abandoned. Entering
        Playing records the start time; entering an end status records
        the end time.

        Args:
            status: The requested new status.

        Raises:
            InvalidTransitionError: If the transition is not allowed.
        """
        if (self.status, status) not in ALLOWED_STATUS_TRANSITIONS:
            raise InvalidTransitionError(
                f"Cannot change game status from {self.status} to {status}"
            )
        self.status = status
        if status == "Playing":
            self.started_at = _now_iso()
        else:
            self.ended_at = _now_iso()
