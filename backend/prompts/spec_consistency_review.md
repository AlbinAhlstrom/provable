You review a set of behaviour specifications that will each be implemented, one after the other, on the same domain classes. Find specifications that cannot all be true together.

## Product intent
{intent_block}

## Specifications
{specs_block}

Report only real contradictions: two or more specifications that demand incompatible results for the same situation (for example one says an inquiry is accepted when a field is missing and another says it is rejected). Do not report overlaps, duplicates, missing detail or style differences.

Respond STRICTLY with JSON, no commentary:
{"conflicts": [{"specs": ["<spec_id>", "<spec_id>"], "reason": "<one sentence naming the incompatible demands>"}]}
Use an empty list when there are none.
