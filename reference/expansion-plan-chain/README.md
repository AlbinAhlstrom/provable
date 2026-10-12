# Reference: the pitch expansion and the UX plan as a chain, 2026-10-11

Two steps run one after the other, the way the pipeline runs them: the expansion's answer is decomposed by the
engine and handed to the plan. Made with `.claude/skills/step-analysis/scripts/chain_bench.py`. Nothing here is run
by the engine or its tests.

Why a chain: both steps had been tuned alone (`reference/expansion-models/`, `reference/ux-plan-models/`), the
plan on one fixed expansion. A kickstart then built a game that was far from the one Opus builds, and no isolated
benchmark could say why.

Pitches (`pitches.json`): "A minesweeper game", "A kanban board for a small team", "A booking page for a hair
salon". Chains: Opus then Opus as the reference, Sonnet then Haiku as the pipeline runs. Effort `low`. The
decomposition between the two ran on Haiku in every chain.

## What separated the chains
Read side by side, the plans differed where the **expansions** differed. On the prompts as they stood:

| The game | Opus then Opus | Sonnet then Haiku (2 runs) |
| --- | --- | --- |
| Behind the window | Teal desktop | Grey, the window's own colour (2 of 2) |
| Choosing a size | "Game" menu in a menu bar | A row of text buttons in the window (2 of 2) |
| The tool's backdrop | Deep blue, as the known tool | Pale blue-grey (2 of 2) |

Sonnet described a page made after the game; Opus described the game. The plan could not repair it: its prompt
says that what the specification states stands, and Opus given Sonnet's expansion kept the grey page as well
(`reference/ux-plan-models/prompt-after-opus/`).

Two more defects showed only on the built page (`logs/runs/20261011-010053_kickstart_a-minesweeper-game`):
- The window was wider than its grid. The expansion put a row of four buttons in the window, the plan chose 16 px
  cells, and no step said which part sets the width.
- The window sat against the top edge. The plan said "centred" and the page centred it sideways only.

## What changed
Expansion (`prompt_expansion.md`), one paragraph:
- A product known by sight is described as the thing itself, not as a page made after it. It keeps what it is
  seen in and against, and offers each choice where the thing itself offers it.
- It runs as a page in a browser: choices that act on the machine around it are left out. (Without this sentence
  Sonnet kept "Exit" and "Help" in 2 of 3 runs.)

UX plan (`ux_planning.md`), two sentences in the visual direction:
- First screen: where the main thing sits, across and down, and what the rest of the screen shows.
- Form of the main view: the main view sets the unit's width, given as a sum the planner works out; every other
  part is fitted to it, and where they need more room the repeated parts are made larger. (A worked example with
  numbers was copied into a plan as the window's width, so the sentence has none.)

## Result, Sonnet then Haiku, three runs per pitch (`after/`)

| The game, read by eye | Before (2 runs) | After (3 runs) |
| --- | --- | --- |
| Teal desktop behind the window | 0 of 2 | 3 of 3 |
| Title bar and "Game" menu | 0 of 2 | 3 of 3 |
| A choice that does nothing on a page ("Exit") | 0 of 2 | 0 of 3 |
| Placement stated across and down | 0 of 2 | 3 of 3 (2 in the middle, 1 top centre) |
| Window width given as a sum that adds up | 0 of 2 | 2 of 3 (one adds a minimum 12 px wider than its grid) |

The other two pitches: the tool's backdrop is the known blue in 2 of 3 runs (pale grey in 2 of 2 before); the
booking page is unchanged in kind, and all three state where the column sits.

| Average per chain | Opus then Opus | Sonnet then Haiku, before | Sonnet then Haiku, after |
| --- | --- | --- | --- |
| Expansion | 33.0 s, 0.72 SEK, 1515 words | 15.2 s, 0.21 SEK, 875 words | 16.1 s, 0.23 SEK, 926 words |
| Plan | 31.6 s, 0.99 SEK, 1248 words | 19.9 s, 0.028 SEK, 1068 words | 22.5 s, 0.031 SEK, 1129 words |
| Both | 64.6 s, 1.71 SEK | 35.1 s, 0.24 SEK | 38.6 s, 0.26 SEK |

Prices: Anthropic list price, 10 SEK per USD. The decomposition's call is not counted.

## What is left
- Not measured here: the built page. The width and the placement are proved only by a kickstart.
- Haiku plans 16 px cells in 1 of 3 runs and 24 px in 2 of 3; Opus plans 24 px.
- Sonnet leaves the custom size out of the game in some runs (2 of 3 here, and before the change as well). The
  classified intent says custom rules are not required.
- An earlier round counted a title bar on the game as unwanted and tuned the plan against it
  (`reference/ux-plan-models/`). That was a wrong reading: the known game has one. The checklist there no longer
  counts it.

## Folders
- `before-opus/`, `before/`, `after/`: for each run the expansion (`.expansion.md`), what filled the plan's
  prompt (`.inputs.json`), the plan (`.md`), both prompts and `runs.json`.
