# Reference: the pitch expansion alone, on three models, 2026-10-10

The expansion step run by itself: three pitches, three models, effort `low`, before and after the prompt was
rewritten. Each pitch was classified once (`intents.json`) and every model was given the same intent. One sample per
cell. Nothing here is run by the engine or its tests.

Pitches: "A minesweeper game" (known by sight), "A kanban board for a small team" (known by sight, a tool),
"A booking page for a hair salon" (no look of its own).

## What "stated" counts
A fixed list of things a builder needs and would otherwise guess, checked by pattern and then by reading: 16 parts
of the look and 10 rules for the game, 10 parts of the look and use for each of the other two (46 in all). The
patterns miss some synonyms, so read a difference of one or two as noise.

## Average of the three pitches

| | Prompt before | | | Prompt after | | |
| --- | --- | --- | --- | --- | --- | --- |
| | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 |
| Stated, of 46 | 21 | 36 | 36 | 42 | 45 | 42 |
| Game, of 26 | 8 | 20 | 21 | 22 | 25 | 24 |
| Colours named in the look | 2.7 | 2.3 | 4.3 | 6.3 | 9.3 | 9.7 |
| Time | 5.9 s | 9.2 s | 12.4 s | 16.3 s | 16.3 s | 26.3 s |
| Cost per call | 0.007 SEK | 0.15 SEK | 0.31 SEK | 0.017 SEK | 0.23 SEK | 0.58 SEK |
| Words written | 524 | 564 | 578 | 1199 | 981 | 1302 |

Prices: Anthropic list price per million tokens (Haiku 0.10 / 0.50 USD, Sonnet 2 / 10, Opus 4 / 20), 10 SEK per USD.

## What it showed
1. **The prompt mattered more than the model.** Before, Haiku left the look to phrases ("the traditional palette",
   "and so on") and dropped a rule every player expects. After, it states what Opus stated before, at a twentieth
   of the price.
2. **Why the old prompt lost detail.** It capped the specification at 350 words and asked for the look in one
   bullet. The larger models spent the words on the look anyway; the small one obeyed the cap.
3. **What the rewrite changed.** It says who reads the specification (builders who see nothing else, so what is
   left to a phrase is guessed), asks for one line per part a person sees and one per thing a person can do, and
   lifts the cap for those lists.
4. **Two things found on the way.** Asked for parts, states, controls and wording as four lists, the small model
   invented extras (a keyboard layout, a line of text under the game) and the large one wrote 2400 words. A limit
   of 30 words a line, and "describe the product as it is, not as it could be extended", ended both. With the look
   and the use under one heading, the small model once left the use out; they now have a heading each.
5. **Sonnet is the steadiest writer**, shortest and most complete, at the same speed as Haiku on the new prompt.

## Folders
- `prompt-before/`: the old prompt, three models.
- `prompt-draft/`: the rewrite as first committed, three models (the table above, "Prompt after").
- `prompt-after-run1..3/`: the prompt as it now stands, Haiku and Sonnet, three runs each.

## The draft cut a feature, and the checklist did not see it
On the draft, Sonnet wrote the game with one size only and listed the choice of difficulty as left out, twice out
of twice; on the old prompt it had kept the three sizes. The draft said "describe the product as it is, and not as
it could be extended", and Sonnet read that as "cut what the intent does not name". The checklist passed it, because
its pattern matched the word in the list of things left out. The sentence now says a product known by sight is
described whole, that the intent rules out only what it lists, and that what the product never had is not added.
The checklist gained items for scope (51 in all).

## Three runs of the prompt as it stands (Haiku and Sonnet)

| | Haiku 5.5 | Sonnet 5.5 |
| --- | --- | --- |
| Stated, average | 88 % | 97 % |
| Stated, worst run | 63 % | 83 % |
| The game keeps its three sizes | 3 of 3 | 3 of 3 |
| Runs of the game with parts it never had | 3 of 3 (a title bar, keyboard control) | 0 of 3 |
| Time | 20.5 s | 14.5 s |
| Cost per call | 0.021 SEK | 0.20 SEK |
| Words written | 1212 | 822 |

Haiku's worst runs are partly the patterns missing its wording (read by eye, its look sections were complete), but
it does add parts the product never had and writes half as much again. Sonnet is steadier, shorter and faster.

Not measured here: whether the richer specification makes the page better. That needs a kickstart.
