"""
Domain Model: BestTime (Aggregate Root)
Single Responsibility Principle (SRP) compliant domain model.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import Optional, List, Dict, Any, Union, Set, Tuple, Callable


try:
    from src.domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
    from src.domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
except ImportError:
    try:
        from domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
        from domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
    except ImportError:
        pass
STANDARD_DIFFICULTIES: Tuple[str, ...] = ("beginner", "intermediate", "expert")


@dataclass
class BestTime:
    """BestTime."""
    id: str
    difficulty_id: str
    game_id: str
    best_seconds: int
    achieved_at: str
    events: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

    def record_win(
        self,
        game_id: str,
        difficulty_id: str,
        elapsed_seconds: int,
        achieved_at: str,
    ) -> bool:
        """Record a won game and keep the fastest time for this difficulty.

        When no best time is stored yet, the first win on this record's
        standard difficulty sets the best time.

        Args:
            game_id: Identifier of the won game.
            difficulty_id: Difficulty the game was played on.
            elapsed_seconds: Seconds taken to win the game.
            achieved_at: Timestamp when the win was achieved.

        Returns:
            True if the stored best time was set or replaced, otherwise False.
        """
        if difficulty_id not in STANDARD_DIFFICULTIES:
            return False
        if difficulty_id != self.difficulty_id:
            return False
        if self.best_seconds is not None and not elapsed_seconds < self.best_seconds:
            return False
        self.best_seconds = elapsed_seconds
        self.game_id = game_id
        self.achieved_at = achieved_at
        return True

    def record_game_end(
        self,
        game_id: str,
        difficulty_id: str,
        outcome: str,
        elapsed_seconds: int,
        ended_at: str,
    ) -> bool:
        """Record the end of a game; only won games can affect the best time.

        Args:
            game_id: Identifier of the ended game.
            difficulty_id: Difficulty the game was played on.
            outcome: How the game ended, such as won, lost or abandoned.
            elapsed_seconds: Seconds the game lasted.
            ended_at: Timestamp when the game ended.

        Returns:
            True if the stored best time was set or replaced, otherwise False.
        """
        if str(outcome).strip().lower() != "won":
            return False
        return self.record_win(
            game_id=game_id,
            difficulty_id=difficulty_id,
            elapsed_seconds=elapsed_seconds,
            achieved_at=ended_at,
        )
