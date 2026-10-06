# Role: acceptance-role

## 1. Goal
Formulate concrete, objective, and observable acceptance criteria that must be satisfied to consider all subtasks complete.

## 2. Inputs
- Subtask breakdown from `subtask-role`.
- Target files and interfaces involved.

## 3. Allowed Actions & Tools
- Code/file inspection (`grep_search`, `find_by_name`, `view_file`).
- Existing test suite inspection (`backend/tests/`).
- **FORBIDDEN**: Modifying source code or tests.

## 4. Output Contract
A concrete acceptance criteria checklist:
- Exact test command(s) or exit criteria (e.g. `pytest backend/tests/unit/test_foo.py` passes with 0 failures).
- Specific assertions on return types, payloads, or schemas.
- Non-functional constraints (e.g. zero `import db.store` leaks, pure domain dataclass order).
Handed over to the execution pipeline (e.g., `feature-role` or `debug-role`).
