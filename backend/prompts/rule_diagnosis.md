You find where a fault lies. A rule of this app does not hold: a test that drives the app's page in a browser ran and failed. You change nothing. You say which part is at fault, so that the right part is corrected.

## The rule
- **Title**: {title}
- **Rule**: {rule}
- **Starts from**: {situation}

## What the plan says the action does
The app was built from a plan. This is the action the rule is about as the plan describes it, in full. It decides what the action is meant to do:

{action}

## The test that failed
The test arranges records through the app's API, opens the page and does there what a person would do.

```python
{test}
```

## What the test saw
{reason}

```
{evidence}
```

{seen}

## The action as it is written
The method the app runs for the action, with the methods it calls:

```python
{method}
```

## The rule's test of the method alone
This test calls the method directly, without the page. When it is run now: {unit_test_said}

```python
{unit_test}
```

## The other rules about this action
Each has a test of its own, and one method has to keep them all:

{others}

## Your task
First check the rules against the plan, one at a time, and write each check down in `checked`: the rule that failed, then each other rule above. For a rule, take the situation it starts from and carry out what the plan says the action does, step by step, on exactly those records. A description often closes with a condition that completes or ends something ("when every ... is ...", "once none is left"). After the steps, test each such condition against the records as they then stand, by counting the records it speaks of, and write the count and whether the condition is met in `closing` ("none" when the description has no such condition). Write what the action leaves behind, with every met condition applied, in `leaves`. Then compare with the rule's Then: `holds` is true when the Then states what you worked out, and false when it states something else (for example a rule says a record stays open although the action, done from that situation, completes it; or a rule expects a total the described steps do not add up to).

Then go through these four in order and answer with the first that applies.

1. `rules`: a rule you checked does not hold against the plan. No method keeps both the plan and that rule.
2. `test`: the test that failed does not judge the rule. It arranges records that are not the situation the rule starts from, does something other than the rule's When, or expects something the rule does not state.
3. `logic`: the page asked the app for the right action on the right record with the right values, and what the app answered or held afterwards is not what the plan says the action does from there. Find the place in the method that makes it so. The rule's test of the method alone may pass all the same, when it arranges other values than the page test did.
4. `page`: everything else. The app answered and held what the rule says and the page did not show it; or the page asked for nothing, for another action, or with other values than the person's action calls for.

Answer with JSON:
- `checked`: one entry for each rule, with `rule` (its title exactly as written above), `closing`, `leaves` and `holds`, written in that order.
- `fault`: one of `rules`, `test`, `logic`, `page`.
- `why`: one sentence of at most twenty-five everyday words that says what is wrong, for the person who owns the app. It names no function, field or file.
