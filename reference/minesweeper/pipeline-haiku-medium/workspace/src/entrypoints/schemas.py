"""
Pydantic DTO Schemas for FastAPI OpenAPI Contract Generation.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any

class DifficultySchema(BaseModel):
    id: str
    name: str
    rows: int
    columns: int
    mine_count: int

class DifficultyCreateSchema(BaseModel):
    name: str
    rows: int
    columns: int
    mine_count: int
    id: Optional[str] = None

class DifficultyResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    id: str
    name: str
    rows: int
    columns: int
    mine_count: int


class GameSessionSchema(BaseModel):
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
    cells: List[Dict[str, Any]] = Field(default_factory=list)

class GameSessionCreateSchema(BaseModel):
    difficulty_id: str
    rows: int
    columns: int
    mine_count: int
    status: str = "ready"
    flag_count: int = 0
    elapsed_seconds: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    cells: List[Dict[str, Any]] = Field(default_factory=list)
    id: Optional[str] = None

class GameSessionResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
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
    cells: List[Dict[str, Any]] = Field(default_factory=list)

