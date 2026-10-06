---
paths:
  - "backend/**"
  - "scripts/**"
---

# Engine rules: layering and test-first

## Layers (dependencies point inward)

Domain model (pure) -> repository -> service layer / unit of work -> routers.

- `backend/domain/`: dataclasses only. No `fastapi`, `pydantic`, `sqlalchemy` or DB imports. Fields without defaults come before fields with defaults.
- `backend/adapters/`: persistence behind `AbstractRepository` (`SqliteRepository`, `FakeRepository`).
- `backend/service_layer/`: orchestrates use cases through a unit of work. Routers and `services.py` never import `db.store`.
- `backend/entrypoints/routers/`: thin HTTP controllers that parse DTOs and call `services.<use_case>(uow=SqliteUnitOfWork())`.

## Test-first loop

1. RED: write `backend/tests/unit/test_<target>.py` using `FakeUnitOfWork` and in-memory doubles. Run only that file and watch it fail for the right reason.
2. GREEN: implement the domain logic and service function. Targeted run passes, fast.
3. WIRE: add concrete adapters and the router handler.
4. VERIFY: `python -m pytest backend/tests/` and the layer-leak check from CLAUDE.md prints nothing.

Never weaken an assertion to get green. The pipeline applies the same discipline to generated code (hash-locked tests in `service_layer/tdd_machine.py`), so the engine must model it.

## Failing tests

A failing test is either stale or a regression. Decide with evidence before deleting anything:
- Check `git log -S"<symbol>"` and `vault/HANDOVER*.md` for the behaviour the test pins.
- Behaviour deliberately removed (architecture moved on): rewrite or delete the test.
- Behaviour still documented: the code regressed. Fix the code. If the fix has to wait, keep the test as `@pytest.mark.xfail(strict=True, reason=...)` so the regression stays visible.

## Hermetic by default

Unit, integration and e2e tests run offline with the LLM mocked (`backend/tests/conftest.py`, including `isolate_test_workspace`). Live-LLM "boss fight" tests run only with `RUN_BOSS_FIGHTS=1` or `-m boss_fight`, and only when the user asks.
