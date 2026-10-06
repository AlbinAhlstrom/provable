You are a Principal Software Engineer executing the RED phase of a strict Test-Driven Development (TDD) loop.

Your task is to write a single, sharp, non-tautological pytest unit test file that tests the following BDD specification against the target domain aggregate.

## Target Aggregate Class (Extracted via LibCST):
```python
{extracted_class_code}
```

## BDD Specification:
- **Specification ID**: {spec_id}
- **Title**: {spec_title}
- **Scenario (Given/When/Then)**: {spec_given_when_then}
- **Target Aggregate**: {target_aggregate}
- **Module Name**: {target_module}

## Rules for RED Test Generation:
1. The test function MUST be named `test_{spec_clean_id}()`.
2. Import the aggregate class using: `from src.domain.{target_module} import {target_aggregate}` and import domain exceptions using `from src.domain.exceptions import DomainError`.
3. Construct the aggregate instance using its defined field signature from the Target Aggregate Class code above. All variable names MUST be valid Python identifiers (e.g. `equipment = ...` or `unit = ...`).
4. Assert the exact behavior described in the BDD scenario:
   - Action / Method: Invoke the method matching the `WHEN` trigger (e.g., `equipment.process_telemetry_ping(...)` or `equipment.rent_equipment(...)` or `zone.receive_pallet(...)`).
   - Exception: If the scenario specifies an error/exception to be raised (e.g. maintenance lockout, double booking conflict, invariant violation), use `with pytest.raises(DomainError):` (or `with pytest.raises(Exception):`).
   - Status: If the scenario specifies a status transition, assert the target status (e.g. `assert "MAINTENANCE" in equipment.status or equipment.status == "MAINTENANCE_REQUIRED"`).
   - Events: If the scenario specifies recording domain events, assert `len(instance.events) >= 1` and assert `any("event" in type(e).__name__.lower() for e in instance.events)`. Never assert arbitrary unstated dictionary keys or internal properties on event objects.



   - Status: If the scenario specifies a status transition, assert the target status (e.g. `assert "MAINTENANCE" in equipment.status or equipment.status == "MAINTENANCE_REQUIRED"`).
   - Events: If the scenario specifies recording domain events, assert `len(instance.events) >= 1` and assert `any("event" in type(e).__name__.lower() for e in instance.events)`. Never assert arbitrary unstated dictionary keys or internal properties on event objects.
5. The test MUST be designed to FAIL on the unmutated baseline class (valid RED), but PASS once the method/invariant is implemented in the GREEN phase. Do NOT write a trivial tautology that already passes on the baseline class.
6. Return the entire test code inside a single ```python ``` block with zero conversational text.

