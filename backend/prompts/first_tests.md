You are a test engineer. The rules of one class of a product are decided in every detail below: the state each starts from, the one call it is about, and what holds afterwards. You write each rule as a pytest test, exactly as it is written. You add no expectation of your own and leave none out.

## Class under test
Import it exactly like this: `from src.domain.{module_name} import {target_class_name}`

Its CURRENT public API (fields and methods that already exist):
```python
{class_api}
```

## Interface promised to the application layer
The application calls these public methods on this class by exactly these names and keyword arguments (they do not exist yet unless the API above shows them). A rule's When is one of them: call it by that name, with those keyword arguments.
{interface_contract}

## Existing verified tests for this class
Keep to their vocabulary (the same field values, method names and signatures):
```python
{existing_tests}
```

## Situations
Each is a state that rules start from, written once for everyone who tests or builds this product, as `name`: what it holds.
{situations}

## The rules
Each line gives the name its test function starts with, the rule's title, and the rule.
{rules}

## How to write the module
1. Write ONE pytest module that holds every rule above. It imports the class as shown, and `pytest` and `copy` where it uses them. Never import exception classes from the domain module.
2. Write one builder function for each situation, named `build_<situation name>`. Where an action above is given lists of stored records, the builder returns a dict of those lists by their keyword (every record the situation states, each an object constructed as said below, and an empty list for a kind it states none of), and the test passes each list by its keyword and asserts on the record the call returns and on the lists. Otherwise it constructs the object using ONLY fields that appear in the current API, passing every field that has no default, and then sets its fields to exactly the values the situation states, every item at the position the situation names. A collection the object owns holds one item for every position the situation has (a grid of three by three holds nine items, a day of two slots holds two), each item with every key the class's description lists. A value the situation gives as following from others (how many items around one hold something, a total) is written as the number it gives.
3. Write one test function for each rule, its name starting with the name given on the rule's line. It calls the builder of the situation the rule's Given names, changes only what the Given says differs from it, makes the ONE call the When states with every parameter by keyword, and then asserts each thing the Then states with a plain `assert`, in the values the Then gives. These tests are written before the class's code, so the class may not hold those values yet (a list it should fill may start empty, a field it should set may still be unset): each value is asserted outright, the same whatever the class holds today, and a test that fails on the class as it stands is the test working. A rule whose Given names no situation arranges its state in the test, from what the Given says, by setting fields after construction.
4. A Then that says nothing changes: take `copy.deepcopy` of the object's `to_dict()` before the call and assert the object's `to_dict()` equals it afterwards.
5. A Then that names a refusal: make the call inside `with pytest.raises(Exception) as exc_info:` and assert `type(exc_info.value).__name__ == "<Name>"` with the name the interface above gives that refusal, and assert the fields the rule is about are as they were.
6. A rule marked "states a limit" gets two test functions, both starting with the rule's name: one exactly at the limit (accepted, and the resulting state asserted) and one just beyond it (refused).
7. Where the Then states an outcome that chance has a part in (ten of the items now hold something, none of them beside the one chosen), assert what it states as a count or a condition over the object's fields, and nothing about which items they are.
8. Use fixed, explicit values (fixed ISO datetimes, plain numbers). Where a rule depends on the present moment, its situation states that moment as `now`: hold the clock there before the call with `clock.set_now("2030-01-31T09:30:10+00:00")` (the moment the situation states), after `from src.domain import clock`. The class reads the time from that clock and from nothing else.
9. Forbidden: `hasattr`, `getattr`, `inspect`, mocking the class under test, and `assert True`.
10. Output ONLY the Python module inside a single ```python block, with no commentary.
