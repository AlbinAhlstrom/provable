You are a senior test engineer writing the RED test of a strict TDD loop for a pure-Python domain model (dataclasses).

## Specification (BDD)
- **Title**: {spec_title}
- **Description**: {spec_description}
- **Scenario**: {spec_given_when_then}{limit_note}

## Class under test
Import it exactly like this: `from src.domain.{module_name} import {target_class_name}`

Its CURRENT public API (fields and methods that already exist):
```python
{class_api}
```

## Interface promised to the application layer
The application calls these public methods on this class by exactly these names and keyword arguments (they do not exist yet unless the API above shows them):
{interface_contract}
If the scenario describes what one of these methods does, your test MUST call that method with those parameter names; do not invent a different name for it. If the scenario is not about any of them, name the method you need as the scenario implies.

## Existing verified tests for this class
Your test must be consistent with these (same meaning of states, same method names and signatures, same behavior); never contradict them. If the scenario seems to conflict with one, test the part of the scenario that does not conflict and keep the same vocabulary.
```python
{existing_tests}
```

## The other rules of this class
Each of these has its own test, written by someone else at the same time, and one implementation must satisfy all of them at once. They all hold in the situation you arrange, whether or not your scenario mentions them:
{other_rules}
{feedback_block}
## Arranging the Given
Put the object straight into the situation the scenario starts from by setting its fields after construction: in a collection it owns, clear what the scenario does not need and write in only the few items it does need. Keep the shape the object has when it is newly created: a collection that starts with one item for every position (each square of a board, each slot of a day) keeps one item for every position, each with every key the class's description lists, and you change only what the items hold. Reach a situation through a sequence of calls only when the scenario is about that sequence itself. Every step of a long sequence is a place where your expectation and the product's rules can part ways, and a test with a wrong expectation fails a correct implementation. For the same reason, show the rule in the simplest situation that shows it (and the situations rule 7 asks for when the scenario states a limit): each further situation is one more expectation that can be wrong, and the implementer is told to implement the rule in full whatever the examples. Simple still means a situation in which your rule decides the outcome alone: go through the other rules above and check, one by one, that none of them also applies to the state you arrange or to the state your action leaves (none of them ends, refuses or changes it). When one does, add or move what it takes for that rule to stay out of it.

Above each assertion, write a short comment that works out the expected result from the product's rules for exactly the state you arranged, item by item (what is where, what can reach what, what blocks it). If the working shows your expectation does not hold, change the arrangement until it does.

## Rules
1. Write ONE pytest test module that verifies the scenario's behavior: arrange (Given), act (When), assert (Then).
2. Construct the object using ONLY fields that appear in the current API, and pass every field that has no default. Never invent constructor arguments. If the scenario needs a field that does not exist yet, set it as an attribute after construction.
3. If the scenario needs behavior that does not exist yet, call it the way the scenario implies. A missing method (AttributeError) or a failed assertion is the expected RED outcome. Choose clear method and keyword-argument names: the implementer will be given this test and will implement exactly that interface.
4. When the scenario says an operation is rejected or raises, use `with pytest.raises(Exception) as exc_info:` and assert `type(exc_info.value).__name__ == "<Name>"`, where the name is the one the interface above gives for that kind of refusal, or, when it gives none, the name the scenario implies. Never import exception classes from the domain module. Compare a field against the values the interface above lists for it, spelled exactly so.
5. Use fixed, explicit values (fixed ISO datetimes, plain numbers). Never call `datetime.now()` and never depend on the clock: pass reference times as arguments.
6. Forbidden: `hasattr`, `getattr`, `inspect`, mocking the class under test, `assert True`, and tests that only check that something exists or returns True without the scenario's input.
7. When the scenario states a number or limit, test BOTH sides of that boundary: one case just beyond it (rejected/invalid, e.g. 119 for a 120 minimum) and one case exactly at it (accepted/valid, e.g. exactly 120). Write them as two test functions or one `pytest.mark.parametrize`. The accepted case must call the same operation and assert it succeeds (no exception, and the resulting state). For rules about ranges, intervals or overlap, also test two intervals that merely touch at an endpoint (end equals start), and state whether the scenario treats that as an overlap.
8. When the scenario's rule holds alike for each of several parties, sides or kinds the class knows (each player, each role, each direction), test it for at least two of them, as separate test functions or one `pytest.mark.parametrize`: an implementation written out once per party is only proved for the parties a test reaches.
9. When the scenario says what is allowed (which moves, transitions or values a thing may take), also test one case the rule does not allow, the kind nearest to an allowed one, and assert it is refused: a rule proved only by what it permits is also met by an implementation that permits everything.
10. Output ONLY the Python module inside a single ```python block, with no commentary.
