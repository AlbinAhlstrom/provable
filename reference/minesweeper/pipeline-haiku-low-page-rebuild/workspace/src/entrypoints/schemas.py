"""
Pydantic DTO Schemas for FastAPI OpenAPI Contract Generation.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any

class GameSchema(BaseModel):
    id: str
    difficulty: str = "Beginner"
    status: str = "ready"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    elapsed_seconds: int = 0
    mine_count: int = 10
    flag_count: int = 0
    cells: List[Dict[str, Any]] = Field(default_factory=list)

class GameCreateSchema(BaseModel):
    difficulty: str = "Beginner"
    status: str = "ready"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    elapsed_seconds: int = 0
    mine_count: int = 10
    flag_count: int = 0
    cells: List[Dict[str, Any]] = Field(default_factory=list)
    id: Optional[str] = None

class GameResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    id: str
    difficulty: str = "Beginner"
    status: str = "ready"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    elapsed_seconds: int = 0
    mine_count: int = 10
    flag_count: int = 0
    cells: List[Dict[str, Any]] = Field(default_factory=list)


class DifficultySettingSchema(BaseModel):
    id: str
    name: str
    rows: int
    columns: int
    mine_count: int

class DifficultySettingCreateSchema(BaseModel):
    name: str
    rows: int
    columns: int
    mine_count: int
    id: Optional[str] = None

class DifficultySettingResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    id: str
    name: str
    rows: int
    columns: int
    mine_count: int


class PositionSchema(BaseModel):
    row: int
    column: int

class PositionCreateSchema(BaseModel):
    row: int
    column: int
    id: Optional[str] = None

class PositionResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    row: int
    column: int

