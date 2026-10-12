"""
Pydantic DTO Schemas for FastAPI OpenAPI Contract Generation.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any

class GameSchema(BaseModel):
    id: str
    difficulty_id: str
    width: int
    height: int
    mine_count: int
    remaining_mines: int
    created_at: str
    status: str = "Ready"
    mines_laid: bool = True
    flags_placed: int = 0
    elapsed_seconds: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    struck_cell_id: Optional[str] = None
    cells: List[Dict[str, Any]] = Field(default_factory=list)

class GameCreateSchema(BaseModel):
    difficulty_id: str
    width: int
    height: int
    mine_count: int
    remaining_mines: int
    created_at: str
    status: str = "Ready"
    mines_laid: bool = True
    flags_placed: int = 0
    elapsed_seconds: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    struck_cell_id: Optional[str] = None
    cells: List[Dict[str, Any]] = Field(default_factory=list)
    id: Optional[str] = None

class GameResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    id: str
    difficulty_id: str
    width: int
    height: int
    mine_count: int
    remaining_mines: int
    created_at: str
    status: str = "Ready"
    mines_laid: bool = True
    flags_placed: int = 0
    elapsed_seconds: int = 0
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    struck_cell_id: Optional[str] = None
    cells: List[Dict[str, Any]] = Field(default_factory=list)


class DifficultySchema(BaseModel):
    id: str
    name: str
    display_order: int
    width: Optional[int] = None
    height: Optional[int] = None
    mine_count: Optional[int] = None
    is_standard: bool = True

class DifficultyCreateSchema(BaseModel):
    name: str
    display_order: int
    width: Optional[int] = None
    height: Optional[int] = None
    mine_count: Optional[int] = None
    is_standard: bool = True
    id: Optional[str] = None

class DifficultyResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    id: str
    name: str
    display_order: int
    width: Optional[int] = None
    height: Optional[int] = None
    mine_count: Optional[int] = None
    is_standard: bool = True


class BestTimeSchema(BaseModel):
    id: str
    difficulty_id: str
    game_id: str
    best_seconds: int
    achieved_at: str

class BestTimeCreateSchema(BaseModel):
    difficulty_id: str
    game_id: str
    best_seconds: int
    achieved_at: str
    id: Optional[str] = None

class BestTimeResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    id: str
    difficulty_id: str
    game_id: str
    best_seconds: int
    achieved_at: str


class BoardConfigurationSchema(BaseModel):
    width: int
    height: int
    mine_count: int

class BoardConfigurationCreateSchema(BaseModel):
    width: int
    height: int
    mine_count: int
    id: Optional[str] = None

class BoardConfigurationResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    width: int
    height: int
    mine_count: int


class GridPositionSchema(BaseModel):
    row: int
    column: int

class GridPositionCreateSchema(BaseModel):
    row: int
    column: int
    id: Optional[str] = None

class GridPositionResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
    row: int
    column: int

