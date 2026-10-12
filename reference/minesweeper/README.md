# Reference: "A minesweeper game", 2026-10-10

One pitch built six ways on the same day, kept as a fixed point to compare later pipeline changes against.
Nothing here is run by the engine or its tests.

| Folder | What it is | Time | Cost | Result |
| --- | --- | --- | --- | --- |
| `opus-agent-free/` | Opus 5.5 (medium) as a free agent: only the pitch, every choice its own | 15.1 min | ~19-23 SEK | Plain HTML/JS, 21 rules, chording; self-checked (21 unit tests, 88 browser checks) |
| `opus-agent-stack/` | Opus 5.5 (medium) as a free agent, held to FastAPI domain + React page | 16.6 min | ~25-33 SEK | 23 rules, 116 tests, mines hidden from the browser; self-checked |
| `pipeline-opus-medium/` | Opus 5.5 (medium) through the pipeline, commit `cbca950` | 7.9 min | 61.07 SEK | Verdict OK, 46 rules proved. Looks like the original. New game after a loss does nothing |
| `pipeline-haiku-medium/` | Haiku 5.5 (medium) through the pipeline, commit `cce7356` | 4.3 min | 1.38 SEK | Degraded: 28 of 33 rules, no chording |
| `pipeline-haiku-low/` | Haiku 5.5 (low) through the pipeline, commit `cce7356` | 3.1 min | 0.81 SEK | Degraded: page call timed out; 18 rules, no chording |
| `pipeline-haiku-low-page-rebuild/` | The page of the run above, rebuilt at commit `010d77f` | 1.8 min | 0.14 SEK | Page OK; the board moves on the first click |

Agent costs are estimates at list price (4 USD in, 20 USD out per million tokens, 10 SEK per USD); pipeline costs are
what the run recorder priced.

## What is in each folder

- **Agent builds:** the product, and `STEPS.md`: the rule list, the definition of done, and every step with what was
  decided, checked and fixed. Dependencies are not included (`npm install` in `opus-agent-stack/frontend`).
- **Pipeline runs:** a run recorder folder as written to `logs/runs/`: `run.json`, `summary.json` (per-stage status,
  time and cost), `trace/` (every LLM call's prompt and answer) and `workspace/` (the generated `src/` and `tests/`).
  `python scripts/trace_report.py` reads only `logs/runs/`; copy a folder back there to report on it.

## Stage by stage (seconds; LLM cost in SEK)

| Stage | Opus medium | Haiku medium | Haiku low |
| --- | --- | --- | --- |
| expansion | 30 s | 16 s | 6 s |
| decomposition | 94 s, 46 rules | 54 s, 33 rules | 15 s, 18 rules |
| action protocol | 48 s, 8 actions | 23 s, 4 actions | 5 s, 3 actions |
| UX plan | 22 s | 14 s | 9 s |
| actions (tests + code) | 208 s, all pass | 94 s, all pass | 57 s, all pass |
| rule tests | 132 s | 64 s | 51 s |
| page | 195 s, 24k tokens | 117 s, 30k tokens | timed out; 74 s on rebuild |
| rule code | 71 s, 46 of 46 | 43 s, 28 of 33 | 91 s, 18 of 18 |
| QA | passed, 7 s | passed, 8 s | passed, 7 s |
| visual review | clean | could not repair | repaired (rebuild) |
| test writing, share of cost | 42.17 of 61.07 | 0.90 of 1.38 | 0.57 of 0.81 |

## What the comparison showed

1. **The steps are right; four things inside them are missing.** Both free agents took nearly the pipeline's order
   on their own. They also walked through a session to find missing rules, checked every rule against a field that
   can express it, passed randomness and time in so tests build known states, and looked at the running page.
2. **An action cannot create a record.** Opus modelled a new game as a new record (`restart_game` returns a fresh
   `Game`). The generated router calls the method on the stored record, saves that record and drops what the method
   returned. After a loss the old game stays on screen. Haiku avoided it by resetting the same record.
3. **Creating a record runs no rule.** A create is a plain insert, so the Opus page builds the list of cells in the
   browser before posting it.
4. **Nothing presses the buttons.** Every rule test passed and QA passed in 7 s, with the new-game control dead.
   No check sends an action through the API or the page and looks at what comes back.
5. **Nothing moves time.** Opus named `tick` and `record_win` as actions a person performs, because the app has no
   other place for them.
6. **The rule count doubles inside the pipeline.** The same model wrote 23 rules as a free agent and 46 through the
   decomposition prompt; each rule costs a test-writing call, and tests are two thirds of every run's cost.
7. **A page whose text sets its frame's width moves when the text changes.** Both free agents made this mistake and
   caught it only by looking; the Haiku page shipped with it.
