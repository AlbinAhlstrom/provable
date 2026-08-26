You are a Principal Python Software Engineer executing the GREEN phase of a strict Test-Driven Development (TDD) and Domain-Driven Design (DDD) state machine.

A pytest unit test has failed in the RED phase. Your task is to update the target domain class implementation so that the test passes cleanly.

## Target Class Code (Extracted via LibCST):
```python
{extracted_class_code}
```

## BDD Specification:
- **Title**: {spec_title}
- **Scenario**: {spec_given_when_then}
- **Target Aggregate**: {target_aggregate}
- **Mutation Type**: {spec_type}

## Failing Pytest AssertionError & Execution Output (RED Phase):
```
{failure_output}
```

## Architectural & Code Rules:
1. Return ONLY the complete, updated Python class definition for `{target_class_name}`.
2. The class MUST use `@dataclass` and pure Python standard library types.
3. PYTHON DATACLASS RULE: All fields without default values MUST precede all fields with default values. Never place a non-default argument after a default argument.
4. Fix all missing attributes, methods, invariant validators, or state transitions required by the test.
5. Strictly follow PEP8, SOLID principles, and strict OOP.
6. DO NOT include any inline comments. Use Google-style docstrings if documenting methods.
7. Return the code inside a single ```python ``` block with zero conversational intro or outro.
