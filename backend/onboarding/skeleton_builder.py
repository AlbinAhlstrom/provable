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
    <script src="https://cdn.tailwindcss.com"></script>
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

const App = (AppModule as any).default || (AppModule as any).App;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {App ? <App /> : <div style={{ color: 'red', padding: 20 }}>Failed to load App component</div>}
  </React.StrictMode>,
);
'''


def generate_frontend_api_client(entities: List[EntitySpec]) -> str:
    ts_interfaces = []
    ts_functions = []

    for ent in entities:
        slug = _to_snake_case(ent.name)
        type_fields = []
        for attr in ent.attributes:
            py_t = _map_type(attr.type)
            ts_t = "string"
            if py_t in ("int", "float"):
                ts_t = "number"
            elif py_t == "bool":
                ts_t = "boolean"
            elif py_t == "List[str]":
                ts_t = "string[]"
            elif py_t == "Dict[str, Any]":
                ts_t = "Record<string, any>"
            
            optional_marker = "?" if (not attr.required or attr.default_value is not None) else ""
            type_fields.append(f"  {attr.name}{optional_marker}: {ts_t};")
        
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


def generate_frontend_entity_view(entity: EntitySpec) -> str:
    slug = _to_snake_case(entity.name)
    headers = [attr.name for attr in entity.attributes]
    if "id" not in headers:
        headers.insert(0, "id")
    
    header_th = "\n".join([f'                  <th key="{h}" className="px-4 py-3 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">{h}</th>' for h in headers[:5]])
    row_td = "\n".join([f'                  <td key="{h}" className="px-4 py-3 text-sm text-slate-300 font-mono">{{item.{h} !== undefined ? String(item.{h}) : "-"}}</td>' for h in headers[:5]])

    form_inputs = []
    for attr in entity.attributes:
        if attr.name == "id":
            continue
        form_inputs.append(f'''          <div key="{attr.name}">
            <label className="block text-xs font-semibold text-slate-400 mb-1">{attr.name}</label>
            <input
              type="{ 'number' if _map_type(attr.type) in ('int', 'float') else 'text' }"
              value={{formData.{attr.name} ?? ''}}
              onChange={{(e) => setFormData({{ ...formData, {attr.name}: e.target.value }})}}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="{attr.name}"
            />
          </div>''')
    form_inputs_code = "\n".join(form_inputs)

    return f'''import React, {{ useState, useEffect }} from 'react';
import {{ {entity.name}, fetch{entity.name}List, create{entity.name} }} from '../api/client';
import {{ Plus, RefreshCw, AlertCircle, CheckCircle }} from 'lucide-react';

export const {entity.name}View: React.FC = () => {{
  const [items, setItems] = useState<{entity.name}[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [formData, setFormData] = useState<Record<string, any>>({{}});

  const loadData = async () => {{
    setLoading(true);
    setError(null);
    try {{
      const data = await fetch{entity.name}List();
      setItems(data);
    }} catch (err: any) {{
      setError(err.message || 'Failed to load {entity.name} records');
    }} finally {{
      setLoading(false);
    }}
  }};

  useEffect(() => {{
    loadData();
  }}, []);

  const handleCreate = async (e: React.FormEvent) => {{
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {{
      await create{entity.name}(formData);
      setSuccess('{entity.name} created successfully!');
      setShowCreate(false);
      setFormData({{}});
      await loadData();
    }} catch (err: any) {{
      setError(err.message || 'Failed to create {entity.name}');
    }}
  }};

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">{entity.name} Management</h2>
          <p className="text-sm text-slate-400">View, monitor, and mutate {entity.name} domain aggregates.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={{loadData}}
            disabled={{loading}}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-sm transition"
          >
            <RefreshCw className={{`w-4 h-4 ${{loading ? 'animate-spin' : ''}}`}} /> Refresh
          </button>
          <button
            onClick={{() => setShowCreate(!showCreate)}}
            className="flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-sm font-medium transition shadow-sm"
          >
            <Plus className="w-4 h-4" /> New {entity.name}
          </button>
        </div>
      </div>

      {{error && (
        <div className="bg-rose-950/50 border border-rose-800 rounded p-4 flex items-center gap-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{{error}}</span>
        </div>
      )}}

      {{success && (
        <div className="bg-emerald-950/50 border border-emerald-800 rounded p-4 flex items-center gap-3 text-emerald-300 text-sm">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <span>{{success}}</span>
        </div>
      )}}

      {{showCreate && (
        <form onSubmit={{handleCreate}} className="bg-slate-900/80 border border-slate-800 rounded-lg p-5 space-y-4">
          <h3 className="text-base font-semibold text-slate-200">Create New {entity.name}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
{form_inputs_code}
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={{() => setShowCreate(false)}}
              className="px-3 py-1.5 text-sm text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded transition"
            >
              Save {entity.name}
            </button>
          </div>
        </form>
      )}}

      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden shadow">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-800">
            <thead className="bg-slate-950">
              <tr>
{header_th}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900">
              {{items.length === 0 ? (
                <tr>
                  <td colSpan={{{len(headers[:5])}}} className="px-4 py-8 text-center text-sm text-slate-500">
                    No {entity.name} records found. Create one above to get started.
                  </td>
                </tr>
              ) : (
                items.map((item, idx) => (
                  <tr key={{item.id || idx}} className="hover:bg-slate-800/50 transition">
{row_td}
                  </tr>
                ))
              )}}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}};
'''


def generate_frontend_app_component(entities: List[EntitySpec], app_title: str) -> str:
    imports = []
    tabs = []
    cases = []

    for ent in entities:
        imports.append(f"import {{ {ent.name}View }} from './views/{ent.name}View';")
        tabs.append(f'''          <button
            key="{ent.name}"
            onClick={{() => setActiveTab('{ent.name}')}}
            className={{`px-4 py-2 text-sm font-medium rounded-md transition ${{
              activeTab === '{ent.name}'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }}`}}
          >
            {ent.name}
          </button>''')
        cases.append(f"        {{activeTab === '{ent.name}' && <{ent.name}View />}}")

    imports_code = "\n".join(imports)
    tabs_code = "\n".join(tabs)
    cases_code = "\n".join(cases)
    default_tab = entities[0].name if entities else "Overview"

    return f'''import React, {{ useState }} from 'react';
import {{ Layers, Server }} from 'lucide-react';
{imports_code}

export const App: React.FC = () => {{
  const [activeTab, setActiveTab] = useState<string>('{default_tab}');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white">{app_title}</h1>
            <p className="text-xs text-slate-400">Generated Full-Stack Domain Application</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 bg-emerald-950/60 border border-emerald-800/80 rounded-full text-emerald-400 text-xs font-medium">
          <Server className="w-3.5 h-3.5" />
          <span>API Connected (:8001)</span>
        </div>
      </header>

      <div className="bg-slate-900/50 border-b border-slate-800 px-6 py-2 flex items-center gap-2">
{tabs_code}
      </div>

      <main className="flex-1 overflow-y-auto">
{cases_code}
      </main>
    </div>
  );
}};

export default App;

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
    files[os.path.join(frontend_dir, "src", "App.tsx")] = generate_frontend_app_component(structure.entities, app_title)
    files[os.path.join(base_path, "src", "api", "client.ts")] = generate_frontend_api_client(structure.entities)
    files[os.path.join(base_path, "src", "App.tsx")] = generate_frontend_app_component(structure.entities, app_title)

    for ent in structure.entities:
        files[os.path.join(frontend_dir, "src", "views", f"{ent.name}View.tsx")] = generate_frontend_entity_view(ent)
        files[os.path.join(base_path, "src", "views", f"{ent.name}View.tsx")] = generate_frontend_entity_view(ent)

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
