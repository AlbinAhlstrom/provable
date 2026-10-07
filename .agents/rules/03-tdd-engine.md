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
**Do the coding, testing, and debugging for a change directly in the main conversation context so the RED/GREEN evidence stays visible. Subagents are fine for read-only work (searching, review), not for writing the implementation.**

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

## 4. Retry Policy Invariant (retries mask errors)
- **At most one retry, ever**, and only when a *verifying step rejects what a generating step produced*: the verdict (and the failing evidence) is fed back to the generator for exactly one more attempt. The TDD loop's GREEN phase is the model case (`TddExecutionState.max_attempts = 2`: first attempt + one feedback retry, then `REQUIRES_HUMAN_INTERVENTION`).
- **Never retry** provider/network/quota errors, parse failures, test tampering, or any error that is not a gate verdict. They must fail loudly with the real reason (`agent_orchestrator.LAST_LLM_ERROR`).
- **No hidden retries:** do not add retry loops, fallbacks-on-error, or SDK auto-retries (the OpenAI client is built with `max_retries=0`). Every attempt must be visible in the result (`attempts`) and the trace.
- Changing this policy needs an explicit decision from the user.

---

## 5. Pre-Commit & Mandatory Pre-Flight Invariants
1. **Pre-Commit Full Test Suite Invariant**:
   **Every commit MUST pass the full test suite (`python -m pytest backend/tests/`, including tests marked `slow`).** `.claude/hooks/guard.py` runs it on `git commit` and blocks the commit on failure, so that run is the evidence; do not run the same suite by hand just before committing. While iterating use the fast tier: `python -m pytest backend/tests/ -m "not slow"` (~10s).
2. **Mandatory Pre-Flight Check**:
   **Before concluding ANY task or communicating back to the user that you are done, you MUST execute `python scripts/agent_preflight_check.py`.** If it fails, fix the errors and re-run, then report what failed and what you did. You are strictly forbidden from presenting broken code as done; if you cannot get it green, say so with the failing output. Phase 6 (screenshot) is skipped when the stack is not running; see `02-frontend-and-ui.md`.

---

## 6. Hermetic Test Suite & Boss Fight Testing Policy
1. **Hermetic Standard Tests**:
   - Standard unit, integration, and E2E tests (`backend/tests/unit/`, `backend/tests/integration/`, etc.) MUST be **100% hermetic and offline**, using mock test doubles (such as `backend/tests/conftest.py`'s `mock_llm_for_unit_tests` fixture).
   - Standard test runs skip live LLM generation to ensure fast (<5s), deterministic, and zero-cost local CI execution.
2. **Boss Fight Execution**:
   - Live LLM calls and unmocked synthesis are **explicitly permitted and expected** for tests decorated with `@pytest.mark.boss_fight` and executed with `RUN_BOSS_FIGHTS=1` (or `pytest -m boss_fight`).
