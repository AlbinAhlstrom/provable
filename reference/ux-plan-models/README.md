# Reference: the UX plan alone, on three models, 2026-10-11

The UX-plan step run by itself: three pitches, three models, effort `low`, before and after its prompt was rewritten.
Made with the `step-analysis` skill. Nothing here is run by the engine or its tests.

Inputs (`cases.json`): for each pitch, Sonnet's expansion from `reference/expansion-models/prompt-after-run1`, the
intent classified there, and one decomposition of it (entities and rules). Every model got the same input.

Pitches: "A minesweeper game" (known by sight), "A kanban board for a small team" (a tool), "A booking page for a
hair salon" (a form with steps).

## Result

| | Prompt before | | | Prompt after | | |
| --- | --- | --- | --- | --- | --- | --- |
| | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
| Wanted items stated | 71 % | 98 % | 100 % | 96 % | 100 % | 98 % |
| Game plans that add text the game never had | 1 of 1 | 1 of 1 | 0 of 1 | 0 of 2 | 0 of 2 | 0 of 1 |
| Layout line right | 1 of 3 | 3 of 3 | 3 of 3 | 6 of 6 | 6 of 6 | 3 of 3 |
| Time | 8.6 s | 11.8 s | 17.4 s | 11.3 s | 16.1 s | 30.3 s |
| Cost per call | 0.014 SEK | 0.29 SEK | 0.61 SEK | 0.018 SEK | 0.36 SEK | 0.92 SEK |
| Words written | 708 | 699 | 740 | 1021 | 961 | 1100 |

"Wanted" is `checklist.json` (41 items over the three pitches), checked by pattern and then by reading. The rows about
added text and the layout line are from reading. Before: one call per cell. After: two calls per pitch for Haiku and
Sonnet, one for Opus. Prices: Anthropic list price, 10 SEK per USD.

## What separated the models before
1. **The prompt ordered words onto every page.** It asked for a welcoming card wherever something was empty and
   mandated a sentence of guidance for every action that could not be done yet. Opus judged that a game needs
   neither. Haiku planned a hint line, a result line and hover hints; Sonnet a status line after the round ends.
2. **A 500-word cap that nobody kept** (all wrote about 700). Haiku made room by leaving values to phrases ("flat
   mid-grey", "the classic blue") and skipping two of the six entries of the visual direction.
3. **The layout line had no stated moment.** Haiku gave the game's largest size and wrote `columns=auto`, which the
   app cannot read.
4. **Published records were described in a business's words only**, so Haiku took a game's levels to be built in.

## What the rewrite changed
1. It says who reads the plan: the page's writer, who reads the specification as well. What the specification
   states stands; the plan decides what it left open, as exact values.
2. Guidance is asked for where a step is shown before it can be used. A signal without words is not said again in
   a sentence.
3. Wording is listed in two groups, what a person reads and what only a screen reader speaks.
4. The cap became a limit per line, and the visual direction's entries are named in order.
5. The layout line counts the view's repeated parts as the page first opens.
6. Published records are a business's offerings, a tool's presets or a game's levels alike.

## One more fix, and five Haiku runs per pitch
Haiku called the game's levels "fixed in the page" in every run. The specification names the three levels with their
sizes, and the rewrite says what the specification states stands, so Haiku took them as given. The prompt now says
what happens where the two meet: the specification's content is what the records hold at first, and the page still
reads it from them. Fifteen Haiku runs on that prompt (`prompt-final-haiku-x5/`), read by eye:

| | Before the fix | After |
| --- | --- | --- |
| Game plans that load the levels from records | 0 of 2 (one said both) | 4 of 5 |
| Game plans adding text or a title | 0 of 2 | 0 of 5 |
| Layout line right, all pitches | 6 of 6 | 14 of 15 (one tool plan gave one column for columns side by side) |
| Wanted items stated | 96 % | 97 % |
| Time, cost per call | 11.3 s, 0.018 SEK | 13.4 s, 0.021 SEK |

## What is left
- Haiku still takes the game's levels as fixed in about one run in five.
- The plans are about 40 % longer than before the rewrite, so the call costs about a quarter more and the page's
  writer reads more.
- Not measured here: the page that is built from the plan.

## Folders
- `prompt-before/`, `prompt-after/`, `prompt-after-opus/`, `prompt-final-haiku-x5/`: the prompt (`prompt.md`), every answer and `runs.json`.
- Score them again: `python .claude/skills/step-analysis/scripts/step_bench.py score --checklist
  reference/ux-plan-models/checklist.json --out reference/ux-plan-models prompt-before prompt-after prompt-after-opus`
