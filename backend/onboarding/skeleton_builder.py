"""
Skeleton Builder — Instant Full-Stack Domain & OpenAPI Skeleton Generator.
Scaffolds pure DDD Domain Models, Repositories, Unit of Work, Pydantic DTOs,
and FastAPI Routers to make OpenAPI /openapi.json available from second zero.
"""

from pipeline_trace import traced
import os
import re
from typing import Dict, List, Any, Optional
from onboarding.router_engine import DomainStructureSchema, EntitySpec, AttributeSpec


_IRREGULAR_PLURALS = {"child": "children", "person": "people", "man": "men", "woman": "women",
                      "foot": "feet", "tooth": "teeth", "mouse": "mice", "goose": "geese"}


def _pluralize(slug: str) -> str:
    """Pluralize the last word of a snake_case slug ("client_family" -> "client_families")."""
    head, sep, last = slug.rpartition("_")
    if last in _IRREGULAR_PLURALS:
        plural = _IRREGULAR_PLURALS[last]
    elif last.endswith(("s", "x", "z", "ch", "sh")):
        plural = last + "es"
    elif last.endswith("y") and len(last) > 1 and last[-2] not in "aeiou":
        plural = last[:-1] + "ies"
    else:
        plural = last + "s"
    return f"{head}{sep}{plural}"


def _to_snake_case(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _map_type(attr_type: str) -> str:
    t = attr_type.lower().strip()
    if t in ("string", "str", "text"):
        return "str"
    if t in ("float", "currency", "number", "price", "rate", "amount"):
        return "float"
    if t in ("int", "integer", "count", "quantity"):
        return "int"
    if t in ("bool", "boolean"):
        return "bool"
    if t in ("list", "tags", "array"):
        return "List[str]"
    if t in ("dict", "map", "json"):
        return "Dict[str, Any]"
    return "str"


def _format_default(default_val: Any, py_type: str) -> str:
    if default_val is None:
        return "None"
    if py_type == "str":
        return f'"{default_val}"'
    if py_type == "bool":
        return "True" if default_val else "False"
    if py_type in ("float", "int"):
        return str(default_val)
    if py_type == "List[str]":
        return "field(default_factory=list)"
    if py_type == "Dict[str, Any]":
        return "field(default_factory=dict)"
    return "None"


def generate_domain_module(entity: EntitySpec) -> str:
    """Generates an isolated Aggregate Root or Entity module following SRP."""
    field_lines = []
    has_list_or_dict = False
    
    # Python dataclass rule: fields without defaults MUST precede fields with defaults.
    sorted_attrs = sorted(
        entity.attributes,
        key=lambda a: 1 if (a.default_value is not None or not a.required) else 0
    )

    for attr in sorted_attrs:
        py_type = _map_type(attr.type)
        if "List[" in py_type or "Dict[" in py_type:
            has_list_or_dict = True
        
        if attr.default_value is not None:
            default_str = _format_default(attr.default_value, py_type)
            if default_str.startswith("field("):
                has_list_or_dict = True
                field_lines.append(f"    {attr.name}: {py_type} = {default_str}")
            else:
                field_lines.append(f"    {attr.name}: {py_type} = {default_str}")
        elif not attr.required:
            field_lines.append(f"    {attr.name}: Optional[{py_type}] = None")
        else:
            field_lines.append(f"    {attr.name}: {py_type}")
            
    fields_code = "\n".join(field_lines) if field_lines else "    id: str"

    return f'''"""
Domain Model: {entity.name} (Aggregate Root)
Single Responsibility Principle (SRP) compliant domain model.
"""

from dataclasses import dataclass{', field' if has_list_or_dict else ''}
from typing import Optional, List, Dict, Any

@dataclass
class {entity.name}:
{fields_code}

    def to_dict(self) -> Dict[str, Any]:
        return {{
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }}
'''


def generate_repository_module(entities: List[EntitySpec]) -> str:
    """Generates AbstractRepository and in-memory FakeRepository for all entities."""
    imports = []
    abstract_classes = []
    fake_classes = []

    for ent in entities:
        slug = _to_snake_case(ent.name)
        imports.append(f"from src.domain.{slug} import {ent.name}")
        
        abstract_classes.append(f'''class Abstract{ent.name}Repository(ABC):
    @abstractmethod
    def add(self, item: {ent.name}) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Optional[{ent.name}]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[{ent.name}]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str) -> None:
        raise NotImplementedError
''')

        fake_classes.append(f'''class Fake{ent.name}Repository(Abstract{ent.name}Repository):
    def __init__(self, items: Optional[List[{ent.name}]] = None):
        self._items: Dict[str, {ent.name}] = {{getattr(i, 'id', str(idx)): i for idx, i in enumerate(items or [])}}

    def add(self, item: {ent.name}) -> None:
        self._items[str(getattr(item, 'id', ''))] = item

    def get(self, item_id: str) -> Optional[{ent.name}]:
        return self._items.get(str(item_id))

    def list(self) -> List[{ent.name}]:
        return list(self._items.values())

    def delete(self, item_id: str) -> None:
        self._items.pop(str(item_id), None)
''')

    imports_code = "\n".join(imports)
    abstract_code = "\n\n".join(abstract_classes)
    fake_code = "\n\n".join(fake_classes)

    return f'''"""
Repository Layer: Abstract and In-Memory Fake Repositories for DDD entities.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
{imports_code}

{abstract_code}

{fake_code}
'''


def generate_uow_module(entities: List[EntitySpec]) -> str:
    """Generates Unit of Work interfaces and in-memory test doubles."""
    uow_fields = []
    fake_inits = []

    for ent in entities:
        slug = _to_snake_case(ent.name)
        uow_fields.append(f"    {_pluralize(slug)}: repository.Abstract{ent.name}Repository")
        fake_inits.append(f"        self.{_pluralize(slug)} = repository.Fake{ent.name}Repository()")

    fields_code = "\n".join(uow_fields)
    inits_code = "\n".join(fake_inits)

    return f'''"""
Unit of Work Layer: Manages atomic transactional boundaries and repositories.
"""

from abc import ABC, abstractmethod
from src.adapters import repository

class AbstractUnitOfWork(ABC):
{fields_code}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
{inits_code}
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass
'''


def generate_schemas_module(entities: List[EntitySpec], value_objects: List[EntitySpec]) -> str:
    """Generates Pydantic DTOs for request/response validation and OpenAPI export."""
    schemas_blocks = []

    for ent in entities + value_objects:
        fields = []
        sorted_attrs = sorted(
            ent.attributes,
            key=lambda a: 1 if (a.default_value is not None or not a.required) else 0
        )
        for attr in sorted_attrs:
            py_type = _map_type(attr.type)
            if attr.default_value is not None:
                default_str = _format_default(attr.default_value, py_type)
                fields.append(f"    {attr.name}: {py_type} = {default_str}")
            elif not attr.required:
                fields.append(f"    {attr.name}: Optional[{py_type}] = None")
            else:
                fields.append(f"    {attr.name}: {py_type}")
        
        fields_code = "\n".join(fields) if fields else "    id: str"

        schemas_blocks.append(f'''class {ent.name}Schema(BaseModel):
{fields_code}

class {ent.name}CreateSchema(BaseModel):
{fields_code}

class {ent.name}ResponseSchema(BaseModel):
{fields_code}
''')

    blocks_code = "\n\n".join(schemas_blocks)

    return f'''"""
Pydantic DTO Schemas for FastAPI OpenAPI Contract Generation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

{blocks_code}
'''


def generate_router_module(entity: EntitySpec) -> str:
    """Generates a FastAPI CRUD router for an aggregate root."""
    slug = _to_snake_case(entity.name)
    plural_slug = _pluralize(slug)

    return f'''"""
FastAPI Router for {entity.name} (Auto-projected from domain model).
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from src.entrypoints.schemas import {entity.name}CreateSchema, {entity.name}ResponseSchema
from src.domain.{slug} import {entity.name}
from src.service_layer.unit_of_work import FakeUnitOfWork

router = APIRouter(prefix="/api/{plural_slug}", tags=["{entity.name}"])

# Active in-memory UoW store for fast runtime execution
_uow = FakeUnitOfWork()

@router.get("", response_model=List[{entity.name}ResponseSchema])
def list_{plural_slug}():
    with _uow:
        items = getattr(_uow, "{plural_slug}").list()
        return [i.to_dict() for i in items]

@router.post("", response_model={entity.name}ResponseSchema, status_code=status.HTTP_201_CREATED)
def create_{slug}(payload: {entity.name}CreateSchema):
    item = {entity.name}(**payload.dict())
    with _uow:
        getattr(_uow, "{plural_slug}").add(item)
        _uow.commit()
    return item.to_dict()

@router.get("/{{item_id}}", response_model={entity.name}ResponseSchema)
def get_{slug}(item_id: str):
    with _uow:
        item = getattr(_uow, "{plural_slug}").get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="{entity.name} not found")
        return item.to_dict()
'''


def generate_app_module(entities: List[EntitySpec]) -> str:
    """Generates the main FastAPI application mounting all aggregate routers."""
    imports = []
    mounts = []

    for ent in entities:
        slug = _to_snake_case(ent.name)
        imports.append(f"from src.entrypoints.routers.{slug} import router as {slug}_router")
        mounts.append(f"app.include_router({slug}_router)")

    imports_code = "\n".join(imports)
    mounts_code = "\n".join(mounts)

    return f'''"""
FastAPI Main Application Entrypoint — Instant OpenAPI Generator.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
{imports_code}

app = FastAPI(
    title="Generated Enterprise Domain API",
    description="Deterministic Domain-Driven API automatically projected from domain models.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

{mounts_code}

@app.get("/health")
def health_check():
    return {{"status": "healthy", "service": "domain-api"}}
'''


@traced("skeleton.generate_files")
def generate_fullstack_skeleton_files(structure: DomainStructureSchema, base_path: str = "") -> Dict[str, str]:
    """Generates a complete dictionary of workspace file paths and their full-stack source code."""
    files: Dict[str, str] = {}
    
    # 1. Domain Aggregate modules (SRP)
    for ent in structure.entities:
        slug = _to_snake_case(ent.name)
        files[os.path.join(base_path, "src", "domain", f"{slug}.py")] = generate_domain_module(ent)
        
    for vo in structure.value_objects:
        slug = _to_snake_case(vo.name)
        files[os.path.join(base_path, "src", "domain", f"{slug}.py")] = generate_domain_module(vo)

    files[os.path.join(base_path, "src", "domain", "__init__.py")] = '"""Domain Layer Package"""\n'

    # 2. Repository and Unit of Work
    files[os.path.join(base_path, "src", "adapters", "__init__.py")] = '"""Adapters Package"""\n'
    files[os.path.join(base_path, "src", "adapters", "repository.py")] = generate_repository_module(structure.entities)
    files[os.path.join(base_path, "src", "service_layer", "__init__.py")] = '"""Service Layer Package"""\n'
    files[os.path.join(base_path, "src", "service_layer", "unit_of_work.py")] = generate_uow_module(structure.entities)

    # 3. Pydantic DTO Schemas & Routers
    files[os.path.join(base_path, "src", "entrypoints", "__init__.py")] = '"""Entrypoints Package"""\n'
    files[os.path.join(base_path, "src", "entrypoints", "schemas.py")] = generate_schemas_module(structure.entities, structure.value_objects)
    
    files[os.path.join(base_path, "src", "entrypoints", "routers", "__init__.py")] = '"""Routers Package"""\n'
    for ent in structure.entities:
        slug = _to_snake_case(ent.name)
        files[os.path.join(base_path, "src", "entrypoints", "routers", f"{slug}.py")] = generate_router_module(ent)

    # 4. FastAPI App Entrypoint
    files[os.path.join(base_path, "src", "app.py")] = generate_app_module(structure.entities)

    # 5. Baseline Skeleton Tests
    first_ent = structure.entities[0] if structure.entities else EntitySpec(name="Item")
    ent_slug = _to_snake_case(first_ent.name)
    sample_kwargs = []
    for attr in first_ent.attributes:
        if attr.required and attr.default_value is None:
            py_t = _map_type(attr.type)
            if py_t == "int":
                sample_kwargs.append(f'{attr.name}=1')
            elif py_t == "float":
                sample_kwargs.append(f'{attr.name}=1.0')
            elif py_t == "bool":
                sample_kwargs.append(f'{attr.name}=True')
            elif py_t == "List[str]":
                sample_kwargs.append(f'{attr.name}=[]')
            elif py_t == "Dict[str, Any]":
                sample_kwargs.append(f'{attr.name}={{}}')
            else:
                sample_kwargs.append(f'{attr.name}="test-1"')
    args_str = ", ".join(sample_kwargs) if sample_kwargs else 'id="test-1"'

    files[os.path.join(base_path, "tests", "unit", "test_skeleton.py")] = f'''import pytest
from src.domain.{ent_slug} import {first_ent.name}
from src.adapters.repository import Fake{first_ent.name}Repository
from src.service_layer.unit_of_work import FakeUnitOfWork
from src.app import app

def test_domain_entity_instantiation():
    """Verify domain entity can be instantiated."""
    item = {first_ent.name}({args_str})
    assert item is not None

def test_fake_repository_crud():
    """Verify repository CRUD operations in memory."""
    repo = Fake{first_ent.name}Repository()
    item = {first_ent.name}({args_str})
    repo.add(item)
    assert len(repo.list()) == 1

def test_fake_uow_commit():
    """Verify Unit of Work transaction lifecycle."""
    uow = FakeUnitOfWork()
    with uow:
        getattr(uow, "{_pluralize(ent_slug)}").add({first_ent.name}({args_str}))
        uow.commit()
    assert uow.committed
'''

    return files


@traced("skeleton.write")
def build_and_write_skeleton(structure: DomainStructureSchema, target_dir: Optional[str] = None) -> List[str]:
    """Generates all full-stack skeleton files and writes them to the specified target directory."""
    base = target_dir or os.getcwd()
    files_map = generate_fullstack_skeleton_files(structure, base_path=base)
    created_paths = []

    for path, code in files_map.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        created_paths.append(path)

    return created_paths
