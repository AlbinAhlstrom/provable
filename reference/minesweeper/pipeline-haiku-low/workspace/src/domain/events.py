"""
Domain Layer Events.
Pure events recorded on aggregate roots for post-commit dispatch.
"""

import time
from typing import Dict, Any

class DomainEvent:
    """Base domain event accepting flexible keyword attributes."""
    def __init__(self, *args, **kwargs):
        self.timestamp = kwargs.get("timestamp", time.time())
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

class MaintenanceRequiredEvent(DomainEvent):
    """Event fired when maintenance is required."""
    pass

class MaintenanceLockedEvent(DomainEvent):
    """Event fired when asset is locked for maintenance."""
    pass

class GameCreatedEvent(DomainEvent):
    pass

class GameUpdatedEvent(DomainEvent):
    pass

class DifficultySettingCreatedEvent(DomainEvent):
    pass

class DifficultySettingUpdatedEvent(DomainEvent):
    pass
