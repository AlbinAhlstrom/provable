You review a set of behaviour specifications that will each be implemented, one after the other, on the same domain classes. Find specifications that cannot all be true together, and specifications that cannot be true of the app as it was planned.

## Product intent
{intent_block}

## Specifications
Where a heading gives an action, it gives it as the plan describes it, in full: that description decides what the action does. The specifications under the heading are about that action. A specification may say which situation it starts from.

{specs_block}

## Your task
First check every specification that stands under an action against the plan, one at a time, and write each check down in `checked`. For a specification, take the situation it starts from and carry out what the plan says the action does, step by step, on exactly those records. A description often closes with a condition that completes or ends something ("when every ... is ...", "once none is left"). After the steps, test each such condition against the records as they then stand, by counting the records it speaks of, and write the count and whether the condition is met in `closing` ("none" when the description has no such condition). Write what the action leaves behind, with every met condition applied, in `leaves`. Then compare with the specification's Then: `holds` is true when the Then states what you worked out or is silent about it, and false when it states something else (for example a specification says a record stays open although the action, done from that situation, completes it; or it expects a total the described steps do not add up to).

Then write the conflicts:
- one for each specification you found not to hold, naming that specification alone;
- one for each set of two or more specifications that demand incompatible results for the same situation (for example one says a request is accepted when a field is missing and another says it is rejected).

Report only real contradictions. Overlaps, duplicates, missing detail and differences of style are none.

Answer with JSON:
- `checked`: one entry for each specification under an action, with `spec` (its id), `closing`, `leaves` and `holds`, written in that order. Keep `closing` and `leaves` to a few words each.
- `conflicts`: each with `specs` (the ids) and `reason`, one sentence of at most twenty-five everyday words that says which demands cannot both be met, for the person who owns the app. It names no function, field or file. An empty list when there are none.
