"""
Domain Model: Difficulty (Aggregate Root)
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
class Difficulty:
    """Difficulty."""
    id: str
    name: str
    rows: int
    columns: int
    mine_count: int
    events: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

    @classmethod
    def select_preset(cls, name: str) -> Difficulty:
        """Build the difficulty preset registered under the given name.

        Args:
            name: The preset name, one of Beginner, Intermediate or Expert.

        Returns:
            A Difficulty holding the rows, columns and mine count of the preset.

        Raises:
            ValueError: If the name does not match a known preset.
        """
        presets = {
            "Beginner": (9, 9, 10),
            "Intermediate": (16, 16, 40),
            "Expert": (16, 30, 99),
        }
        if name not in presets:
            raise ValueError(f"Unknown difficulty preset: {name}")
        rows, columns, mine_count = presets[name]
        return cls(
            id=name.lower(),
            name=name,
            rows=rows,
            columns=columns,
            mine_count=mine_count,
        )
