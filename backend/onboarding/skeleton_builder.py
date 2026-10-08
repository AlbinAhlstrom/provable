"""
Skeleton Builder — Instant Full-Stack Domain & OpenAPI Skeleton Generator.
Scaffolds pure DDD Domain Models, Repositories, Unit of Work, Pydantic DTOs,
and FastAPI Routers to make OpenAPI /openapi.json available from second zero.
"""

from pipeline_trace import traced
import os
import re
import shutil
from typing import Dict, List, Any, Optional
from onboarding.draft_theme import DraftTheme, theme_css
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


def to_snake_case(name: str) -> str:
    """Module/file name for an aggregate (ClientInquiry -> client_inquiry). Shared with the TDD loop so both
    write the SAME module that the generated routers and repositories import."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


_to_snake_case = to_snake_case


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


PART_LIST = "List[Dict[str, Any]]"


def _py_type(attr: Any) -> str:
    """The Python type of an attribute: a list of an owned part is a list of plain records."""
    return PART_LIST if getattr(attr, "item_attributes", None) else _map_type(attr.type)


def _ts_type(py_type: str) -> str:
    return {"int": "number", "float": "number", "bool": "boolean", "List[str]": "string[]",
            "Dict[str, Any]": "Record<string, any>"}.get(py_type, "string")


def _parts_doc(entity: EntitySpec) -> str:
    """Docstring lines saying what one item of each part list holds (the class API shown to test and code writers)."""
    lines = []
    for attr in entity.attributes:
        if getattr(attr, "item_attributes", None):
            keys = ", ".join(f"{a.name} ({_map_type(a.type)})" for a in attr.item_attributes)
            lines.append(f"    {attr.name}: the {attr.item_name} records this {entity.name} owns, one dict each with the keys {keys}.")
    return ("\n\n" + "\n".join(lines) + "\n    ") if lines else ""


def _format_default(default_val: Any, py_type: str) -> str:
    if default_val is None:
        return "None"
    if py_type == "str":
        return f'"{default_val}"'
    if py_type == "bool":
        return "True" if default_val else "False"
    if py_type in ("float", "int"):
        return str(default_val)
    if py_type in ("List[str]", PART_LIST):
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
        py_type = _py_type(attr)
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


    has_events = any(a.name == "events" for a in entity.attributes)
    if entity.is_aggregate_root and not has_events:
        field_lines.append("    events: List[Any] = field(default_factory=list)")


    fields_code = "\n".join(field_lines) if field_lines else "    id: str"

    return f'''"""
Domain Model: {entity.name} (Aggregate Root)
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
class {entity.name}:
    """{entity.name}.{_parts_doc(entity)}"""
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


DATA_DIR = ".data"  # where the running app saves its records, beside `src/`

_RECORD_STORE = r'''"""
Record store: the records of the running app, kept in one JSON file per collection.

The API holds its records in memory and restarts whenever its code changes. Each router saves its collection here
after every change and reads it back on its first request, so a restart loses nothing. `APP_DATA_DIR` names the
folder; set to an empty string (as the tests do) nothing is read or saved.
"""

import json
import os
from typing import Any, Dict, List, Optional

_DEFAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "__DATA_DIR__")


def _path(collection: str) -> Optional[str]:
    folder = os.environ.get("APP_DATA_DIR", _DEFAULT_DIR)
    return os.path.join(folder, f"{collection}.json") if folder else None


def load(collection: str) -> Dict[str, Any]:
    """The saved records and the modification time of the seed file they already include."""
    path = _path(collection)
    if not path or not os.path.exists(path):
        return {"seed_mtime": None, "records": []}
    with open(path, encoding="utf-8") as saved:
        return json.load(saved)


def save(collection: str, records: List[Dict[str, Any]], seed_mtime: Optional[float]) -> None:
    path = _path(collection)
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as out:
        json.dump({"seed_mtime": seed_mtime, "records": records}, out, default=str)
    os.replace(path + ".tmp", path)
'''

TESTS_CONFTEST = '''"""Tests run on records of their own: nothing the running app saved is read, and nothing a test creates is saved."""
import os

os.environ["APP_DATA_DIR"] = ""
'''


def generate_record_store_module() -> str:
    """Generates the file store that keeps the app's records across restarts of its API."""
    return _RECORD_STORE.replace("__DATA_DIR__", DATA_DIR)


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
            py_type = _py_type(attr)
            if attr.default_value is not None:
                default_str = _format_default(attr.default_value, py_type).replace("field(", "Field(")
                fields.append(f"    {attr.name}: {py_type} = {default_str}")
            elif not attr.required:
                fields.append(f"    {attr.name}: Optional[{py_type}] = None")
            else:
                fields.append(f"    {attr.name}: {py_type}")
        
        fields_code = "\n".join(fields) if fields else "    id: str"
        # Whoever creates a record does not know its id: the create endpoint assigns one when none is sent
        create_fields = [f for f in fields if f != "    id: str"] + ["    id: Optional[str] = None"]
        create_fields_code = "\n".join(create_fields)

        schemas_blocks.append(f'''class {ent.name}Schema(BaseModel):
{fields_code}

class {ent.name}CreateSchema(BaseModel):
{create_fields_code}

class {ent.name}ResponseSchema(BaseModel):
    model_config = ConfigDict(extra="allow")  # fields the domain class grows later are served too
{fields_code}
''')

    blocks_code = "\n\n".join(schemas_blocks)

    return f'''"""
Pydantic DTO Schemas for FastAPI OpenAPI Contract Generation.
"""

from pydantic import BaseModel, ConfigDict, Field
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

import inspect
import json
import os
import re
import uuid
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from src.entrypoints.schemas import {entity.name}CreateSchema, {entity.name}ResponseSchema
from src.domain.{slug} import {entity.name}
from src.service_layer.unit_of_work import FakeUnitOfWork
from src.adapters import record_store

router = APIRouter(prefix="/api/{plural_slug}", tags=["{entity.name}"])

# Active in-memory UoW store for fast runtime execution
_uow = FakeUnitOfWork()

# Records live in memory and are saved after every change (src/adapters/record_store.py), so a restart of this
# server loses nothing. Starting content (src/seed_data.json, written at generation time for entities shown to the
# audience) is read on the first request after the file appears or changes, because the file is written after this
# server has started; a seed file that was already applied is not applied again, so a removed record stays removed.
# The domain decides: a record it rejects is reported loudly and left out, the API stays up.
_SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "seed_data.json")
_seed_state = {{"mtime": None, "loaded": False}}


def _add_records(records: List[Dict[str, Any]], source: str) -> None:
    repo = getattr(_uow, "{plural_slug}")
    known = {{getattr(i, 'id', None) for i in repo.list()}}
    for record in records:
        if record.get("id") in known:
            continue
        try:
            repo.add({entity.name}(**record))
        except Exception as exc:
            print(f"[{{source}}] {entity.name} record {{record.get('id')!r}} was rejected by the domain: {{exc}}", flush=True)


def _save() -> None:
    record_store.save("{plural_slug}", [i.to_dict() for i in getattr(_uow, "{plural_slug}").list()], _seed_state["mtime"])


def _ensure_seeded() -> None:
    if not _seed_state["loaded"]:
        _seed_state["loaded"] = True
        saved = record_store.load("{plural_slug}")
        _seed_state["mtime"] = saved["seed_mtime"]
        with _uow:
            _add_records(saved["records"], "saved")
            _uow.commit()
    try:
        mtime = os.path.getmtime(_SEED_PATH)
    except OSError:
        return
    if _seed_state["mtime"] == mtime:
        return
    _seed_state["mtime"] = mtime
    with open(_SEED_PATH, encoding="utf-8") as seed_file:
        records = json.load(seed_file).get("{entity.name}", [])
    with _uow:
        _add_records(records, "seed")
        _uow.commit()
    _save()


@router.get("", response_model=List[{entity.name}ResponseSchema])
def list_{plural_slug}():
    _ensure_seeded()
    with _uow:
        items = getattr(_uow, "{plural_slug}").list()
        return [i.to_dict() for i in items]

@router.post("", response_model={entity.name}ResponseSchema, status_code=status.HTTP_201_CREATED)
def create_{slug}(payload: {entity.name}CreateSchema):
    _ensure_seeded()
    data = payload.dict()
    if "id" in data and not data["id"]:
        data["id"] = uuid.uuid4().hex
    item = {entity.name}(**data)
    with _uow:
        getattr(_uow, "{plural_slug}").add(item)
        _uow.commit()
    _save()
    return item.to_dict()

@router.get("/{{item_id}}", response_model={entity.name}ResponseSchema)
def get_{slug}(item_id: str):
    _ensure_seeded()
    with _uow:
        item = getattr(_uow, "{plural_slug}").get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="{entity.name} not found")
        return item.to_dict()

@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{slug}(item_id: str):
    _ensure_seeded()
    with _uow:
        repo = getattr(_uow, "{plural_slug}")
        if not repo.get(item_id):
            raise HTTPException(status_code=404, detail="{entity.name} not found")
        repo.delete(item_id)
        _uow.commit()
    _save()


class ActionRequest(BaseModel):
    action_type: str = Field(..., description="Name of a public domain method on {entity.name}")
    params: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments for that method")


def _public_actions(item) -> Dict[str, Any]:
    return {{
        name: member for name, member in inspect.getmembers(item, inspect.ismethod)
        if not name.startswith("_") and name != "to_dict"
    }}


@router.post("/{{item_id}}/action")
def run_{slug}_action(item_id: str, request: ActionRequest):
    """Runs one of the aggregate's own domain methods; the domain decides whether the action is allowed."""
    _ensure_seeded()
    name = re.sub(r"[^a-z0-9]+", "_", request.action_type.strip().lower()).strip("_")
    with _uow:
        item = getattr(_uow, "{plural_slug}").get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="{entity.name} not found")
        actions = _public_actions(item)
        if name not in actions:
            raise HTTPException(status_code=404, detail=f"Unknown action '{{request.action_type}}'. Available: {{sorted(actions)}}")
        method = actions[name]
        try:
            inspect.signature(method).bind(**request.params)
        except TypeError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid parameters for '{{name}}': {{exc}}")
        try:
            result = method(**request.params)
        except Exception as exc:  # the domain rejected the action; its state is left as the domain left it
            raise HTTPException(status_code=400, detail=str(exc) or type(exc).__name__)
        _uow.commit()
        _save()
        return {{
            "success": True,
            "state": item.to_dict(),
            "message": result if isinstance(result, str) else f"{{request.action_type}} completed",
        }}
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


def generate_frontend_package_json(app_title: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', app_title.lower()).strip('-') or 'workspace-frontend'
    return f'''{{
  "name": "{slug}",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite --port 5174",
    "build": "tsc && vite build",
    "preview": "vite preview --port 5174"
  }},
  "dependencies": {{
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.344.0"
  }},
  "devDependencies": {{
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.2.2",
    "vite": "^5.3.1"
  }}
}}
'''


def generate_frontend_vite_config() -> str:
    return '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
});
'''


def generate_frontend_tsconfig() -> str:
    return '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
'''


def generate_frontend_tailwind_config() -> str:
    return '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        }
      }
    },
  },
  plugins: [],
}
'''


def generate_frontend_postcss_config() -> str:
    return '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''


def generate_frontend_index_html(app_title: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{app_title}</title>
  </head>
  <body class="bg-slate-950 text-slate-100 antialiased min-h-screen">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''


def generate_frontend_index_css() -> str:
    return '''@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #090d16;
  color: #f1f5f9;
}
'''


def generate_frontend_main_tsx() -> str:
    return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import * as AppModule from './App';
import './index.css';
import './theme.css';

const App = (AppModule as any).default || (AppModule as any).App;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {App ? <App /> : <div style={{ color: 'red', padding: 20 }}>Failed to load App component</div>}
  </React.StrictMode>,
);
'''


def _ts_interface_fields(entity: EntitySpec) -> List[str]:
    """TypeScript interface field lines for an entity's attributes."""
    lines = []
    for attr in entity.attributes:
        if getattr(attr, "item_attributes", None):
            item = "; ".join(f"{a.name}: {_ts_type(_map_type(a.type))}" for a in attr.item_attributes)
            ts_t = f"Array<{{ {item} }}>"
        else:
            ts_t = _ts_type(_map_type(attr.type))
        optional_marker = "?" if (not attr.required or attr.default_value is not None) else ""
        lines.append(f"  {attr.name}{optional_marker}: {ts_t};")
    return lines


def generate_master_client(master: EntitySpec) -> str:
    """The master aggregate's API client (`src/api/<slug>Client.ts`), written deterministically from the entity so it can
    never drift from the router: list/get/create plus the action endpoint. Errors are thrown with the server's message;
    nothing is fabricated when a request fails."""
    name, plural = master.name, _pluralize(_to_snake_case(master.name))
    fields = "\n".join(_ts_interface_fields(master)) or "  id: string;"
    return f'''/** Generated from the {name} aggregate; calls the domain API (:8001) through the Vite proxy. */

export interface {name}State {{
{fields}
  [key: string]: any;
}}

export interface ActionResponse {{
  success: boolean;
  state: {name}State;
  message?: string;
}}

const BASE_URL = '/api/{plural}';

async function failure(res: Response, what: string): Promise<Error> {{
  const body = await res.json().catch(() => ({{}}));
  return new Error(typeof body.detail === 'string' ? body.detail : `${{what}} failed (${{res.status}})`);
}}

export async function list{name}(): Promise<{name}State[]> {{
  const res = await fetch(BASE_URL);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}}

export async function get{name}(id: string): Promise<{name}State> {{
  const res = await fetch(`${{BASE_URL}}/${{encodeURIComponent(id)}}`);
  if (!res.ok) throw await failure(res, 'Loading');
  return res.json();
}}

export async function create{name}(data: Partial<{name}State>): Promise<{name}State> {{
  const res = await fetch(BASE_URL, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data),
  }});
  if (!res.ok) throw await failure(res, 'Saving');
  return res.json();
}}

export async function sendAction(
  id: string,
  actionType: string,
  params: Record<string, unknown> = {{}}
): Promise<ActionResponse> {{
  const res = await fetch(`${{BASE_URL}}/${{encodeURIComponent(id)}}/action`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ action_type: actionType, params }}),
  }});
  if (!res.ok) throw await failure(res, 'The action');
  return res.json();
}}
'''


def generate_frontend_api_client(entities: List[EntitySpec]) -> str:
    ts_interfaces = []
    ts_functions = []

    for ent in entities:
        slug = _to_snake_case(ent.name)
        type_fields = _ts_interface_fields(ent)
        type_body = "\n".join(type_fields) if type_fields else "  id: string;"

        ts_interfaces.append(f'''export interface {ent.name} {{
{type_body}
  [key: string]: any;
}}''')

        ts_functions.append(f'''export async function fetch{ent.name}List(): Promise<{ent.name}[]> {{
  const res = await fetch(`/api/{_pluralize(slug)}`);
  if (!res.ok) throw new Error(`Failed to fetch {ent.name} list: ${{res.statusText}}`);
  return res.json();
}}

export async function get{ent.name}(id: string): Promise<{ent.name}> {{
  const res = await fetch(`/api/{_pluralize(slug)}/${{encodeURIComponent(id)}}`);
  if (!res.ok) throw new Error(`Failed to fetch {ent.name} ${{id}}: ${{res.statusText}}`);
  return res.json();
}}

export async function create{ent.name}(data: Partial<{ent.name}>): Promise<{ent.name}> {{
  const res = await fetch(`/api/{_pluralize(slug)}`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data),
  }});
  if (!res.ok) {{
    const err = await res.json().catch(() => ({{ detail: res.statusText }}));
    throw new Error(err.detail || `Failed to create {ent.name}`);
  }}
  return res.json();
}}''')

    interfaces_code = "\n\n".join(ts_interfaces)
    functions_code = "\n\n".join(ts_functions)

    return f'''/**
 * Auto-Generated Type-Safe API Client for Workspace Domain API (:8001).
 * Generated deterministically from domain aggregates and Pydantic schemas.
 */

{interfaces_code}

{functions_code}
'''


def plain_plural(name: str) -> str:
    """An entity's name as a visitor would say it: `SalonService` -> `Salon services`."""
    return _pluralize(to_snake_case(name)).replace("_", " ").capitalize()


_ENTITY_VIEW = r"""import React, { useEffect, useState } from 'react';
import { __E__, fetch__E__List, create__E__ } from '../api/client';

// A first draft of the app: the records as they are, until the page is written.
const TITLE_FIELD = '__TITLE__';
const FORM_FIELDS: { name: string; numeric: boolean }[] = __FORM_FIELDS__;

const label = (key: string) => key.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
const shown = (value: unknown): string =>
  Array.isArray(value) ? String(value.length)
    : typeof value === 'boolean' ? (value ? 'Yes' : 'No')
    : value === null || value === undefined || value === '' ? '–' : String(value);
const listed = (key: string) => key !== 'id' && key !== 'events' && key !== TITLE_FIELD && !key.endsWith('_id');

const surface = { background: 'var(--draft-surface)', borderColor: 'color-mix(in srgb, var(--draft-text) 14%, transparent)' };
const muted = { color: 'color-mix(in srgb, var(--draft-text) 62%, transparent)' };
const accent = { background: 'var(--draft-accent)', color: 'var(--draft-on-accent)' };
const heading = { fontFamily: 'var(--draft-heading-font)' };

export const __E__View: React.FC = () => {
  const [items, setItems] = useState<__E__[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const [formData, setFormData] = useState<Record<string, any>>({});

  const load = async () => {
    try {
      setItems(await fetch__E__List());
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Could not load __PLURAL_LOWER__');
    }
  };

  // The starting content is written a little after the app starts: ask again while there is nothing to show
  const empty = items.length === 0;
  useEffect(() => {
    load();
    if (!empty) return;
    const timer = setInterval(load, 3000);
    return () => clearInterval(timer);
  }, [empty]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await create__E__(formData);
      setAdding(false);
      setFormData({});
      await load();
    } catch (err: any) {
      setError(err.message || 'Could not save');
    }
  };

  return (
    <section className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold" style={heading}>__PLURAL__</h2>
        {FORM_FIELDS.length > 0 && (
          <button onClick={() => setAdding(!adding)} className="px-4 py-2 rounded-lg text-sm font-medium" style={accent}>
            {adding ? 'Close' : 'Add'}
          </button>
        )}
      </div>

      {error && <p className="rounded-lg border px-4 py-3 text-sm" style={surface} role="alert">{error}</p>}

      {adding && (
        <form onSubmit={handleCreate} className="rounded-xl border p-5 space-y-4" style={surface}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {FORM_FIELDS.map(field => (
              <label key={field.name} className="block text-sm">
                <span className="block mb-1" style={muted}>{label(field.name)}</span>
                <input
                  type={field.numeric ? 'number' : 'text'}
                  value={formData[field.name] ?? ''}
                  onChange={e => setFormData({ ...formData, [field.name]: field.numeric && e.target.value !== '' ? Number(e.target.value) : e.target.value })}
                  className="w-full rounded-lg border px-3 py-2 text-sm bg-transparent"
                  style={{ borderColor: surface.borderColor }}
                />
              </label>
            ))}
          </div>
          <button type="submit" className="px-4 py-2 rounded-lg text-sm font-medium" style={accent}>Save</button>
        </form>
      )}

      {empty ? (
        <p className="rounded-xl border border-dashed px-6 py-10 text-center text-sm" style={{ ...surface, ...muted }}>Nothing here yet.</p>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item, index) => (
            <li key={item.id || index} className="rounded-xl border p-5" style={surface}>
              <h3 className="text-lg font-semibold mb-3" style={heading}>{shown(item[TITLE_FIELD])}</h3>
              <dl className="space-y-1.5 text-sm">
                {Object.keys(item).filter(listed).map(key => (
                  <div key={key} className="flex justify-between gap-4">
                    <dt style={muted}>{label(key)}</dt>
                    <dd className="text-right break-words min-w-0">{shown(item[key])}</dd>
                  </div>
                ))}
              </dl>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
};
"""


def generate_frontend_entity_view(entity: EntitySpec) -> str:
    """The stand-in view of one entity: its records as cards under a plain name, coloured by `src/theme.css`."""
    scalars = [a for a in entity.attributes if a.name != "id" and not getattr(a, "item_attributes", None)]
    described = [a for a in scalars if not a.name.endswith("_id")]
    title = (described or scalars or [None])[0]
    form_fields = ", ".join(
        f"{{ name: '{a.name}', numeric: {'true' if _map_type(a.type) in ('int', 'float') else 'false'} }}" for a in scalars)
    plural = plain_plural(entity.name)
    return (_ENTITY_VIEW.replace("__E__", entity.name).replace("__TITLE__", title.name if title else "id")
            .replace("__FORM_FIELDS__", f"[{form_fields}]").replace("__PLURAL_LOWER__", plural.lower())
            .replace("__PLURAL__", plural))


_APP_COMPONENT = r"""import React, { useState } from 'react';
__IMPORTS__

// A first draft of the app: what it keeps track of, shown plainly until the page is written.
const TABS: { name: string; label: string; view: React.FC }[] = [
__TABS__
];

export const App: React.FC = () => {
  const [active, setActive] = useState<string>(TABS[0]?.name ?? '');
  const View = TABS.find(tab => tab.name === active)?.view;

  return (
    <div className="min-h-screen" style={{ background: 'var(--draft-bg)', color: 'var(--draft-text)' }}>
      <header className="max-w-5xl mx-auto px-4 sm:px-6 pt-10 pb-2">
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight" style={{ fontFamily: 'var(--draft-heading-font)' }}>__TITLE__</h1>
        {TABS.length > 1 && (
          <nav className="mt-6 flex flex-wrap gap-2">
            {TABS.map(tab => (
              <button
                key={tab.name}
                onClick={() => setActive(tab.name)}
                className="px-4 py-2 rounded-full text-sm font-medium border"
                style={tab.name === active
                  ? { background: 'var(--draft-accent)', color: 'var(--draft-on-accent)', borderColor: 'var(--draft-accent)' }
                  : { borderColor: 'color-mix(in srgb, var(--draft-text) 20%, transparent)' }}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        )}
      </header>
      <main>{View && <View />}</main>
    </div>
  );
};

export default App;
"""


def generate_frontend_app_component(entities: List[EntitySpec], app_title: str) -> str:
    """The stand-in app: the product's name and one tab per entity it is given."""
    imports = "\n".join(f"import {{ {e.name}View }} from './views/{e.name}View';" for e in entities)
    tabs = "\n".join(f"  {{ name: '{e.name}', label: '{plain_plural(e.name)}', view: {e.name}View }}," for e in entities)
    title = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", app_title).replace("{", "").replace("}", "")
    return _APP_COMPONENT.replace("__IMPORTS__", imports).replace("__TABS__", tabs).replace("__TITLE__", title)


def _draft_entities(structure: DomainStructureSchema) -> List[EntitySpec]:
    """The entities the stand-in app lists: the ones the audience works with, or all of them when the structure
    says nothing about its audience."""
    if any(getattr(e.audience_role, "value", "internal") != "internal" for e in structure.entities):
        return structure.presented_entities()
    return list(structure.entities)


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
    files[os.path.join(base_path, "src", "domain", "exceptions.py")] = '''"""
Domain Layer Exceptions.
Pure domain exceptions representing business rule violations and concurrency conflicts.
"""

class DomainError(Exception):
    """Base domain error."""
    pass

class StaleDataError(DomainError):
    """Raised when an optimistic concurrency control (OCC) version conflict occurs."""
    pass

class InvariantViolation(DomainError):
    """Raised when an entity invariant is violated."""
    pass

class MaintenanceRequiredError(DomainError):
    """Raised when equipment operating hours exceed threshold before maintenance."""
    pass

class MaintenanceLockoutError(DomainError):
    """Raised when equipment is locked for maintenance."""
    pass

class ReservationConflictError(DomainError):
    """Raised when an asset is double-booked or already reserved."""
    pass

class BusinessRuleViolation(DomainError):
    """Raised when general business rules are breached."""
    pass
'''

    events_code = '''"""
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
'''
    for ent in structure.entities:
        events_code += f'''
class {ent.name}CreatedEvent(DomainEvent):
    pass

class {ent.name}UpdatedEvent(DomainEvent):
    pass
'''
    files[os.path.join(base_path, "src", "domain", "events.py")] = events_code


    # 2. Repository and Unit of Work
    files[os.path.join(base_path, "src", "adapters", "__init__.py")] = '"""Adapters Package"""\n'
    files[os.path.join(base_path, "src", "adapters", "repository.py")] = generate_repository_module(structure.entities)
    files[os.path.join(base_path, "src", "service_layer", "__init__.py")] = '"""Service Layer Package"""\n'
    files[os.path.join(base_path, "src", "service_layer", "unit_of_work.py")] = generate_uow_module(structure.entities)
    files[os.path.join(base_path, "src", "adapters", "record_store.py")] = generate_record_store_module()
    files[os.path.join(base_path, "tests", "conftest.py")] = TESTS_CONFTEST

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

    # 6. Standalone Full-Stack Frontend Application (Vite + React 18 + Tailwind on Port 5174)
    app_title = structure.domain_name or "Domain Application"
    frontend_dir = os.path.join(base_path, "frontend")

    
    files[os.path.join(frontend_dir, "package.json")] = generate_frontend_package_json(app_title)
    files[os.path.join(frontend_dir, "vite.config.ts")] = generate_frontend_vite_config()
    files[os.path.join(base_path, "vite.config.ts")] = generate_frontend_vite_config()
    files[os.path.join(frontend_dir, "tsconfig.json")] = generate_frontend_tsconfig()
    files[os.path.join(frontend_dir, "tailwind.config.js")] = generate_frontend_tailwind_config()
    files[os.path.join(frontend_dir, "postcss.config.js")] = generate_frontend_postcss_config()
    files[os.path.join(frontend_dir, "index.html")] = generate_frontend_index_html(app_title)
    files[os.path.join(base_path, "index.html")] = generate_frontend_index_html(app_title)
    files[os.path.join(frontend_dir, "src", "index.css")] = generate_frontend_index_css()
    files[os.path.join(frontend_dir, "src", "main.tsx")] = generate_frontend_main_tsx()
    files[os.path.join(base_path, "src", "main.tsx")] = generate_frontend_main_tsx()
    files[os.path.join(frontend_dir, "src", "api", "client.ts")] = generate_frontend_api_client(structure.entities)
    draft_entities = _draft_entities(structure)
    files[os.path.join(frontend_dir, "src", "App.tsx")] = generate_frontend_app_component(draft_entities, app_title)
    for root in (frontend_dir, base_path):
        files[os.path.join(root, "src", "theme.css")] = theme_css(DraftTheme())
    files[os.path.join(base_path, "src", "api", "client.ts")] = generate_frontend_api_client(structure.entities)
    files[os.path.join(base_path, "src", "App.tsx")] = generate_frontend_app_component(draft_entities, app_title)

    for ent in structure.entities:
        files[os.path.join(frontend_dir, "src", "views", f"{ent.name}View.tsx")] = generate_frontend_entity_view(ent)
        files[os.path.join(base_path, "src", "views", f"{ent.name}View.tsx")] = generate_frontend_entity_view(ent)

    return files


@traced("skeleton.write")
def build_and_write_skeleton(structure: DomainStructureSchema, target_dir: Optional[str] = None) -> List[str]:
    """Generates all full-stack skeleton files and writes them to the specified target directory."""
    base = target_dir or os.getcwd()
    files_map = generate_fullstack_skeleton_files(structure, base_path=base)
    shutil.rmtree(os.path.join(base, DATA_DIR), ignore_errors=True)  # a new app starts without the previous one's records
    created_paths = []

    for path, code in files_map.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        created_paths.append(path)

    return created_paths
