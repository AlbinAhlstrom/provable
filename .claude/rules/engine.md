---
paths:
  - "backend/**"
  - "scripts/**"
---

# Engine rules: layering and test-first

## Layers (dependencies point inward)

Domain model (pure) -> repository -> service layer / unit of work -> routers.

- `backend/domain/`: dataclasses only. No `fastapi`, `pydantic`, `sqlalchemy` or DB imports. Fields without defaults come before fields with defaults.
- `backend/adapters/`: persistence behind `AbstractRepository` (`Sqlite...`, `Fake...`).
- `backend/service_layer/`: orchestrates use cases through a unit of work. Routers and `services.py` never import `db.store`.
- `backend/entrypoints/routers/`: thin HTTP controllers that parse DTOs and call `services.<use_case>(uow=SqliteUnitOfWork())`.

Layer-leak check (must print nothing):
`grep -rn "import db.store" backend/entrypoints/routers/ backend/service_layer/services.py`

Where new code goes: `services.py` is already about 2,400 lines and mixes use cases with file I/O, subprocesses and pipeline orchestration. Do not grow it. New pipeline logic lives in a module under `backend/onboarding/` with its collaborators injected (the pattern of `qa_gate.py`), and `services.py` only calls it. When you touch an existing function there, prefer extracting it.

## Test-first loop

1. RED: write `backend/tests/unit/test_<target>.py` using `FakeUnitOfWork` and in-memory doubles. Run only that file and watch it fail for the right reason.
2. GREEN: implement the domain logic and service function. The targeted run passes, fast.
3. WIRE: add concrete adapters and the router handler.
4. VERIFY: the layer-leak check above prints nothing. The full suite runs for you on `git commit`.

Do this directly in the main context so the RED/GREEN evidence stays visible. Subagents are for read-only research and review. Never weaken an assertion to get green.

## Failing tests

A failing test is either stale or a regression. Decide with evidence before deleting anything:
- Check `git log -S"<symbol>"` and `vault/HANDOVER-archive.md` for the behaviour the test pins.
- Behaviour deliberately removed (the architecture moved on): rewrite or delete the test. Never revert architectural progress to satisfy a legacy test.
- Behaviour still documented: the code regressed. Fix the code. If the fix has to wait, keep the test as `@pytest.mark.xfail(strict=True, reason=...)` so the regression stays visible.

## Hermetic by default

Unit, integration and e2e tests run offline with the LLM mocked (`backend/tests/conftest.py`, including `isolate_test_workspace`). Live-LLM "boss fight" tests (`@pytest.mark.boss_fight`) run only with `RUN_BOSS_FIGHTS=1` or `-m boss_fight`, and only when the user asks.
