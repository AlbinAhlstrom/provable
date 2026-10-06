"""
Domain Events — Pure dataclasses representing business events occurring within the domain.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

class Event:
    pass

@dataclass
class RequirementCreated(Event):
    req_id: str
    title: str
    description: str
    priority: str = "High"
    status: str = "Backlog"

@dataclass
class RequirementEdited(Event):
    req_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None

@dataclass
class RequirementMoved(Event):
    req_id: str
    parent_id: Optional[str] = None

@dataclass
class RequirementRejected(Event):
    req_id: str
    feedback: str

@dataclass
class ComponentAdded(Event):
    canonical_key: str
    prompt: str
    req_id: str

@dataclass
class ComponentDeleted(Event):
    canonical_key: str

@dataclass
class RequirementStatusChanged(Event):
    req_id: str
    old_status: str
    new_status: str
    timestamp: float = 0.0



