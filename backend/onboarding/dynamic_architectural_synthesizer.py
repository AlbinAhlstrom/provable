"""
Dynamic Architectural Synthesizer — First-Principles Architecture Generator.
Synthesizes bespoke DDD contracts and anti-monolith component hierarchies
from raw natural language prompts and induced domain structures.
Strictly category-free and domain-agnostic: zero hardcoded domain keywords.
"""

import re
from typing import List, Optional
from onboarding.router_engine import DomainStructureSchema, BusinessSpec


def _to_snake_case(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _sanitize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", name)


def synthesize_backend_domain_contract(
    pitch: str,
    structure: DomainStructureSchema,
    inbox_specs: List[BusinessSpec],
    rel_workspace: str
) -> str:
    """
    Phase 1 Task DAG: Synthesizes the execution contract for the Pure Python DDD Domain Engine & REST Endpoints.
    """
    clean_pitch = pitch.strip()
    domain_name = _sanitize_name(structure.domain_name or "Application")
    domain_slug = _to_snake_case(domain_name)
    ws = rel_workspace.replace("\\", "/").rstrip("/")

    master_entity = None
    for ent in structure.entities:
        if ent.is_aggregate_root and master_entity is None:
            master_entity = ent
            break

    master_name = _sanitize_name(master_entity.name) if master_entity else domain_name
    master_slug = _to_snake_case(master_name)

    entity_summaries = []
    for ent in structure.entities:
        attr_desc = ", ".join(f"{a.name}: {a.type}" for a in ent.attributes)
        entity_summaries.append(f"- **{ent.name}** ({'Aggregate Root' if ent.is_aggregate_root else 'Entity'}): [{attr_desc}]")
    entities_block = "\n".join(entity_summaries) if entity_summaries else f"- **{master_name}**: Primary Aggregate Root"

    bdd_lines = []
    for idx, spec in enumerate(inbox_specs, 1):
        bdd_lines.append(f"- **Invariant {idx} [{spec.title}]** ({spec.target_aggregate}):\n  - {spec.given_when_then}")
    bdd_section = "\n".join(bdd_lines) if bdd_lines else "- Enforce domain validation invariants and valid state progression."

    return f"""# Phase 1: Pure Python DDD & Invariant Engine Execution Contract

You are Provable's Backend Execution Engine. Build the **core business logic, state machines, and REST endpoints** for:

## Domain Specification
- **Product Pitch**: "{clean_pitch}"
- **Domain Identity**: `{domain_name}`
- **Entities & Value Objects**:
{entities_block}

---

## 1. Backend Invariants & Architecture Rules
1. **Pure Domain Isolation**: Code in `{ws}/src/domain/` must consist strictly of pure Python dataclasses, methods, and exceptions. Zero framework, database, or HTTP imports in `{ws}/src/domain/`.
2. **Single Source of Truth**: The domain model owns 100% of state transitions and invariant guards. Invalid operations must be rejected with zero state mutation.
3. **Pluggable Architecture**:
   - `{ws}/src/domain/state.py`: Explicit serializable state dataclass representing current snapshot of facts.
   - `{ws}/src/domain/rules.py`: Invariant validation strategies and rules.
   - `{ws}/src/domain/{master_slug}.py`: Aggregate Root coordinating state transitions.
   - `{ws}/src/entrypoints/routers/{master_slug}.py`: FastAPI router with:
     - `GET /api/{master_slug}s` or `GET /api/{master_slug}/state`: Current state snapshot.
     - `POST /api/{master_slug}/action` or `POST /api/{master_slug}s/{{id}}/action`: Command validation & execution (rejects invalid commands with HTTP 400).
     - `POST /api/{master_slug}/reset` or `POST /api/{master_slug}s/{{id}}/reset`: Reinitializes default state.

## 2. Dynamic Acceptance Invariants (BDD Grounding)
All tests in `{ws}/tests/unit/` MUST pass hermetically:
{bdd_section}

## 3. Required Deliverable
Implement the Python modules above and run `pytest tests/unit` to verify 100% test pass rate. Do not touch frontend files in this phase.
"""


def synthesize_frontend_projection_contract(
    pitch: str,
    structure: DomainStructureSchema,
    inbox_specs: List[BusinessSpec],
    rel_workspace: str
) -> str:
    """
    Phase 2 Task DAG: Synthesizes the execution contract for the Interactive Frontend Presentation Projection.
    """
    clean_pitch = pitch.strip()
    domain_name = _sanitize_name(structure.domain_name or "Application")
    domain_slug = _to_snake_case(domain_name)
    ws = rel_workspace.replace("\\", "/").rstrip("/")

    master_entity = None
    child_entities = []
    for ent in structure.entities:
        if ent.is_aggregate_root and master_entity is None:
            master_entity = ent
        else:
            child_entities.append(ent)

    master_name = _sanitize_name(master_entity.name) if master_entity else domain_name
    master_slug = _to_snake_case(master_name)

    child_components = []
    for child in child_entities[:3]:
        c_name = _sanitize_name(child.name)
        child_components.append(f"  - `{ws}/src/components/{c_name}/{c_name}Card.tsx` (Atomic item/unit display)")
    child_components_str = "\n" + "\n".join(child_components) if child_components else ""

    return f"""# Phase 2: Interactive Frontend Presentation Projection Execution Contract

The backend domain model and FastAPI REST endpoints are now fully implemented and verified on `:8001`.
Your mission is to build the **interactive, responsive React frontend** in `{ws}/src/` (and `{ws}/frontend/src/`):

## Domain Specification
- **Product Pitch**: "{clean_pitch}"
- **Domain Identity**: `{domain_name}`
- **Master Aggregate Root**: `{master_name}`

---

## 1. Presentation Invariants (Zero Tolerance for Violations)
1. **Single Source of Truth**: The React frontend is a **pure presentation projection**. It queries state and dispatches actions to REST endpoints on `:8001` (via `/api/`). Zero duplicate client-side business logic.
2. **Interactive Canvas (Anti-Monolith Invariant)**:
   - **FORBIDDEN**: Reducing interactive applications to boring administrative database CRUD tables (e.g. textboxes and generic SQL tables)!
   - **MANDATORY**: Render the intuitive human interactive canvas described in the pitch (e.g. interactive playable grid/board canvas with element selection and interaction highlights; or timeline/calendar slot canvas; or workflow cards).
   - **MANDATORY**: Decompose into single-responsibility components (strictly < 150 lines per file):
     - `{ws}/src/views/{master_name}View.tsx` (Primary interactive canvas & workspace view){child_components_str}
     - `{ws}/src/components/Controls/{master_name}Controls.tsx` (Actions, reset, triggers, status indicators)
     - `{ws}/src/components/History/{master_name}History.tsx` (Transition log, event history, audit trail)
     - `{ws}/src/api/{master_slug}Client.ts` (Strongly typed API client calling backend endpoints)
     - `{ws}/src/App.tsx` (Pure layout orchestrator, STRICTLY under 100 lines)

## 2. Required Deliverable
Build the modular frontend component tree above. Ensure seamless integration with the backend REST endpoints.
"""


def synthesize_dynamic_architecture_contract(
    pitch: str,
    structure: DomainStructureSchema,
    inbox_specs: List[BusinessSpec],
    rel_workspace: str
) -> str:
    """
    Combined architectural execution contract (retained for backward compatibility and monolithic runs).
    """
    clean_pitch = pitch.strip()
    domain_name = _sanitize_name(structure.domain_name or "Application")
    domain_slug = _to_snake_case(domain_name)
    ws = rel_workspace.replace("\\", "/").rstrip("/")

    master_entity = None
    child_entities = []
    for ent in structure.entities:
        if ent.is_aggregate_root and master_entity is None:
            master_entity = ent
        else:
            child_entities.append(ent)

    master_name = _sanitize_name(master_entity.name) if master_entity else domain_name
    master_slug = _to_snake_case(master_name)

    entity_summaries = []
    for ent in structure.entities:
        attr_desc = ", ".join(f"{a.name}: {a.type}" for a in ent.attributes)
        entity_summaries.append(f"- **{ent.name}** ({'Aggregate Root' if ent.is_aggregate_root else 'Entity'}): [{attr_desc}]")
    entities_block = "\n".join(entity_summaries) if entity_summaries else f"- **{master_name}**: Primary Aggregate Root"

    bdd_lines = []
    for idx, spec in enumerate(inbox_specs, 1):
        bdd_lines.append(f"- **Invariant {idx} [{spec.title}]** ({spec.target_aggregate}):\n  - {spec.given_when_then}")
    bdd_section = "\n".join(bdd_lines) if bdd_lines else "- Enforce domain validation invariants and valid state progression."

    child_components = []
    for child in child_entities[:3]:
        c_name = _sanitize_name(child.name)
        child_components.append(f"  - `{ws}/frontend/src/components/{c_name}/{c_name}Card.tsx` (Atomic item/unit display)")

    child_components_str = "\n" + "\n".join(child_components) if child_components else ""

    return f"""# Provable Dynamic Architectural Contract

You are Provable's Execution Engine. Build an **extensible, production-grade architectural foundation** for the following domain:

## Domain Specification
- **User Pitch**: "{clean_pitch}"
- **Domain Identity**: `{domain_name}`
- **Entities & Value Objects**:
{entities_block}

---

## 1. Universal Architectural Invariants (Zero Tolerance for Violations)

### Invariant 1: Single Source of Truth (Pure DDD)
- The backend domain model owns **100% of business logic, invariant enforcement, and state transitions**.
- The React frontend is a **pure presentation projection**: it queries state and dispatches actions to REST endpoints.
- **FORBIDDEN**: The frontend must NEVER implement duplicate client-side business validation, coordinate collision checks, or invariant rules.

### Invariant 2: Pure Domain Isolation
- Code in `{ws}/src/domain/` must consist strictly of pure Python dataclasses, methods, and exceptions.
- **FORBIDDEN**: Zero framework, database, or HTTP imports in `{ws}/src/domain/`.

### Invariant 3: Component Modularity & Interactive Canvas (Anti-Monolith Invariant)
- **FORBIDDEN**: Monolithic single-file applications.
- **FORBIDDEN**: Reducing interactive applications to boring administrative database CRUD tables (e.g. tables of textboxes for entity attributes)!
- **MANDATORY**: Render the intuitive, domain-faithful human interactive canvas (e.g. for games/spatial: interactive playable 2D grid/board canvas with element selection and interaction highlights; for scheduling: interactive calendar/slot canvas; for workflows: multi-stage draggable cards).
- **MANDATORY**: Decompose into single-responsibility components (strictly < 150 lines per file):
  - `{ws}/frontend/src/views/{master_name}View.tsx` (Primary interactive canvas & workspace view){child_components_str}
  - `{ws}/frontend/src/components/Controls/{master_name}Controls.tsx` (Actions, reset, triggers, status indicators)
  - `{ws}/frontend/src/components/History/{master_name}History.tsx` (Transition log, event history, audit trail)
  - `{ws}/frontend/src/api/{master_slug}Client.ts` (Strongly typed API client calling backend endpoints)
  - `{ws}/frontend/src/App.tsx` (Pure layout orchestrator, STRICTLY under 100 lines)

### Invariant 4: Pluggable Rule & State Architecture
- Encapsulate distinct concerns into cohesive modules:
  - `{ws}/src/domain/state.py`: Explicit serializable state dataclass representing the current snapshot of facts.
  - `{ws}/src/domain/rules.py`: Rule validation strategies and domain invariants.
  - `{ws}/src/domain/{master_slug}.py`: Aggregate Root coordinating state transitions via rules.
  - `{ws}/src/entrypoints/routers/{master_slug}.py`: FastAPI router exposing state queries and command actions.

---

## 2. Dynamic Acceptance Criteria (BDD Grounding)
The implementation MUST satisfy every one of the following concrete behavioral invariants:
{bdd_section}

---

## 3. Required Deliverables
1. **Domain Model**: Pure Python state, rules, and aggregate root in `{ws}/src/domain/`.
2. **FastAPI Endpoints**:
   - `GET /api/{master_slug}/state`: Returns current state snapshot and available actions.
   - `POST /api/{master_slug}/action`: Validates and executes requested command. Rejects invalid operations with HTTP 400.
   - `POST /api/{master_slug}/reset`: Reinitializes a clean default state.
3. **Modular React Frontend**: Interactive, responsive UI built from the modular component tree above.
4. **Hermetic Test Verification**: Execute `pytest tests/unit` and verify all acceptance tests pass.
"""
