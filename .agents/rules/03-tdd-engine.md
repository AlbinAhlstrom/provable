# 03 - TDD Engine & Layered Architecture Rules

## 1. DDD Architecture Boundaries & Layer Rules
Every component in the system adheres strictly to Domain-Driven Design (DDD) layering:

$$\text{Domain Model (Pure)} \longrightarrow \text{Repository Pattern} \longrightarrow \text{Service Layer / Unit of Work} \longrightarrow \text{Presentation Routers}$$

### Layer Rules:
1. **Pure Domain Model (`backend/domain/model.py` / `workspace/src/domain/`)**:
   - Domain dataclasses MUST have **ZERO** FastAPI, Pydantic, SQLAlchemy, or DB dependencies.
   - Domain models encapsulate pure business logic, invariants, and state transitions.
   - **Python Dataclass Field Ordering Rule**: All fields without default values MUST precede all fields with default values. Never place a non-default argument after a default argument in `@dataclass` domain definitions.
2. **Repository Layer (`backend/adapters/`)**:
   - Manages persistence abstraction (`AbstractRepository` and `SqliteRepository` / `FakeRepository`).
3. **Service Layer & Unit of Work (`backend/service_layer/`)**:
   - Orchestrates transactions and domain operations.
   - Routers MUST NEVER import `db.store` directly; all route handlers delegate to `services.<use_case>(uow=SqliteUnitOfWork())`.
4. **Entrypoints / Routers (`backend/entrypoints/routers/`)**:
   - Pure HTTP controllers parsing request DTOs and delegating to the service layer.

---

## 2. Mandatory 4-Step TDD Execution Workflow (No Subagents)
**DO NOT invoke developer subagents for code edits. Perform all coding, testing, and debugging directly in the main conversation context.**

Follow the strict 4-step TDD loop:
1. **RED**: Write a unit test in `backend/tests/unit/test_<target>.py` using `FakeUnitOfWork` and in-memory test doubles. Run ONLY `python -m pytest backend/tests/unit/test_<target>.py` and verify failure.
2. **GREEN**: Implement domain logic, service layer functions, and messagebus handlers. Run targeted unit pytest and verify pass in `<0.5s`.
3. **WIRE**: Implement concrete repository adapters and wire the FastAPI route handlers in `backend/entrypoints/routers/`.
4. **VERIFY**: Run full test suite `python -m pytest backend/tests/` and verify ZERO `import db.store` leaks across routers and service layer:
   ```bash
   grep -rn "import db.store" backend/entrypoints/routers/ backend/service_layer/services.py
   ```

---

## 3. 5-Line Hash Lock Anti-Cheat Verification
- Test integrity during TDD GREEN phase is enforced via SHA-256 cryptographic hashing (`compute_test_file_hash` / `verify_test_file_integrity`).
- Never modify or weaken test assertions during the GREEN phase.

---

## 4. Pre-Commit & Mandatory Pre-Flight Invariants
1. **Pre-Commit Full Test Suite Invariant**:
   **NEVER execute `git commit` or `git commit --amend` without running the full test suite (`python -m pytest backend/tests/`) first.** Every commit MUST be preceded by empirical runtime verification showing 100% PASS across unit, integration, and E2E test suites.
2. **Mandatory Pre-Flight Check**:
   **Before concluding ANY task or communicating back to the user that you are done, you MUST execute `python scripts/agent_preflight_check.py`.** If it fails, you must fix the errors silently before responding. You are strictly forbidden from presenting broken code.
