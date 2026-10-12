"""
Domain Model: DifficultySetting (Aggregate Root)
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


@dataclass
class DifficultySetting:
    """DifficultySetting."""
    id: str
    name: str
    rows: int
    columns: int
    mine_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

    @classmethod
    def for_difficulty(cls, name: str) -> DifficultySetting:
        """Build the board setting for a named difficulty.

        Args:
            name: One of "Beginner", "Intermediate" or "Expert".

        Returns:
            The DifficultySetting holding the specified grid and mine count.

        Raises:
            ValueError: If the name is not one of the three difficulties.
        """
        grids = {
            "Beginner": (9, 9, 10),
            "Intermediate": (16, 16, 40),
            "Expert": (16, 30, 99),
        }
        if name not in grids:
            raise ValueError(f"Unknown difficulty: {name!r}")
        rows, columns, mine_count = grids[name]
        return cls(
            id=name.lower(),
            name=name,
            rows=rows,
            columns=columns,
            mine_count=mine_count,
        )
