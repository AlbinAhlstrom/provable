# STEPS: how "A minesweeper game" was built

Written as the work happened. The four blocks below are the contract I held myself to;
the numbered log follows.

## Rule list (the behaviours the product must have)

Board and setup
- R1. A game is created from a preset: beginner 9x9 with 10 mines, intermediate 16x16 with 40, expert 16 rows x 30 columns with 99.
- R2. A custom game takes rows (5-24), columns (5-30) and mines (1 to rows*cols-9); anything else is rejected.
- R3. A new game is `ready`: nothing revealed, no mines placed yet, timer at 0.

First move
- R4. Mines are placed at the first reveal, never on the first cell or any of its neighbours, so the first click always opens an area.
- R5. Placement is a pure function of (size, mine count, first cell, seed): the same inputs give the same board; the seed is fixed when the game is created.
- R6. The first reveal turns the game to `playing` and starts the timer.

Revealing
- R7. Revealing a safe cell shows how many of its up-to-8 neighbours are mines.
- R8. Revealing a cell with 0 mine neighbours opens its neighbours too, repeatedly (flood fill); the fill stops at numbered cells and never opens or removes a flag.
- R9. Revealing a flagged cell does nothing (the flag protects it). Revealing an already revealed cell does nothing.
- R10. Revealing a mine loses the game: status `lost`, that cell is the exploded one, the timer stops.

Flags
- R11. Flagging toggles a flag on a hidden cell; a revealed cell cannot be flagged (no change). Flags are allowed before the first reveal.
- R12. Mines remaining = mine count minus flags placed; it may go negative when the player over-flags.

Chording
- R13. Chording a revealed number whose flagged neighbours equal that number reveals all its other hidden neighbours (with flood fill).
- R14. Chording does nothing when the flag count does not match, on a hidden cell, or on a 0.
- R15. A chord with a wrong flag reveals a mine and loses the game.

Ending
- R16. The game is `won` the moment every safe cell is revealed; the timer stops and every mine is flagged automatically (mines remaining = 0).
- R17. After `won` or `lost` no action is accepted (rejected, state unchanged).
- R18. A cell outside the board is rejected for every action.

Time
- R19. Elapsed time is 0 before the first reveal, runs from the first reveal while playing, and is frozen at the finishing move afterwards. The clock is passed in, never read by the domain.

What the player may see (the server is the authority)
- R20. While a game is `ready` or `playing`, the view contains only hidden / flagged / revealed-number cells: no mine position and no seed ever leaves the server.
- R21. After a loss the view shows the exploded mine, every other unflagged mine, and every wrong flag; correct flags stay flags.

Statistics
- R22. Per difficulty: games played (finished), games won, win rate, best (lowest) winning time. Unfinished games do not count.

Persistence
- R23. A game saved and loaded again is identical (mines, flags, revealed cells, times, status), so a page reload or server restart resumes it.

## Records

`Game` (the only record; statistics are derived from games, not stored)

| Field | Type | Meaning |
| --- | --- | --- |
| id | str | opaque id, given by the app |
| difficulty | `beginner` / `intermediate` / `expert` / `custom` | |
| rows, cols, mine_count | int | board configuration |
| seed | int | fixes the mine layout; never sent to the browser |
| status | `ready` / `playing` / `won` / `lost` | |
| mines | set of (row, col) or None | None until the first reveal |
| revealed | set of (row, col) | |
| flags | set of (row, col) | |
| exploded | (row, col) or None | the mine that ended a lost game |
| created_at, started_at, finished_at | float seconds or None | timestamps handed in by the app |

Browser view of a game (`GameView`): id, difficulty, rows, cols, mine_count, status,
mines_remaining, elapsed_seconds, created_at, board (one string per row; per cell `H` hidden, `F` flag,
`0`-`8` revealed, and after a loss `M` mine, `X` exploded mine, `W` wrong flag).

## Actions

| Action | Arguments | Endpoint |
| --- | --- | --- |
| create game | difficulty, and rows/cols/mines when custom | `POST /api/games` |
| list games | - | `GET /api/games` |
| get game | id | `GET /api/games/{id}` |
| reveal | row, col | `POST /api/games/{id}/reveal` |
| toggle flag | row, col | `POST /api/games/{id}/flag` |
| chord | row, col | `POST /api/games/{id}/chord` |
| read statistics | - | `GET /api/stats` |
| read presets | - | `GET /api/difficulties` |

## Definition of done

1. Every rule R1-R23 has at least one pytest unit test against the domain, written before the code, all green.
2. The HTTP layer is tested (TestClient): each endpoint, error codes, and that no response leaks mines or seed during play.
3. `npm run build` passes with strict TypeScript (no errors).
4. I have played in a real browser against the running API: a full win, a full loss, flagging, chording, a custom game, a reload that resumes the game, all three presets rendered, a narrow (phone) viewport.
5. No console errors in the browser; no server tracebacks in the log.
6. README says how to run it; servers I started are stopped.

---

# Log

## 1. Read the pitch and decided what "delighted" means
- Step: Turned the one-line pitch into a product scope before touching code.
- Decided:
  - Classic Minesweeper, faithfully: three presets, first-click-safe, flood fill, flags, chording, timer, mine counter, win/lose reveal. Rejected inventing variants (hex, lives): someone who types "a minesweeper game" wants the game they know.
  - Additions that make it pleasant rather than bare: custom boards, best times and win rate per difficulty, resume after reload, touch support (flag mode + long press), keyboard play.
  - Rejected question-mark cells: rarely used, adds a third state to every flag rule. Rejected a "no-guess" solver-backed generator: big scope, not expected by default.
  - Rejected player accounts / names: single-player on one machine; a leaderboard of one name is noise.
- Produced: the scope above.
- Checked: tool versions (Python 3.11.9, FastAPI 0.143, pytest 9.1, httpx 0.28, Node 20.5, npm 9.8); ports 8101 and 5181 free. Python Playwright is NOT installed, so browser verification will use the browser tools.
- Fixed: nothing.

## 2. Listed the rules
- Step: Wrote the rule list R1-R23 (top of this file) as testable sentences, one behaviour each.
- Decided:
  - First click opens an area (safe cell AND its neighbours), not merely "is not a mine": a lone "1" as first result forces a guess, which feels unfair. Consequence: custom mines capped at rows*cols-9.
  - Harmless repeats (reveal a revealed or flagged cell, flag a revealed cell, chord that does not match) are no-ops, not errors: they happen constantly with a mouse and are not mistakes. Real violations (off board, game already over, bad configuration) are errors.
  - Win auto-flags the remaining mines so the counter reads 0, as the classic does.
  - Over-flagging is allowed and the counter goes negative; rejected capping flags at the mine count because that leaks nothing and blocks nothing useful, it only surprises.
  - Hidden information is a rule (R20/R21), not an API detail: if the browser got the mines, the server would not be the authority.
- Produced: rule list.
- Checked: walked the list against a mental play-through (new game, flag first, first click, chord, lose, win on first click with 1 mine) looking for undefined cases; that added "flags allowed before first reveal" (R11) and "win can happen on the very first reveal" (covered by R16 + R6).
- Fixed: nothing.

## 3. Chose the records, fields and actions
- Step: Decided the data model and the action list (tables above).
- Decided:
  - One record, `Game`. Rejected a stored `Score`/`Leaderboard` record: best times are derivable from won games, and a second copy can drift.
  - Randomness: the game stores a `seed` (chosen by the app at creation); placement is `place_mines(rows, cols, count, safe_cell, seed)`, pure and deterministic. Rejected placing mines at creation (cannot guarantee a safe first click) and rejected moving a mine on first click (classic trick, but leaves the first click a lone number).
  - Clock: every time-dependent method takes `now`; the domain never reads a clock.
  - Tests build exact boards through `Game.with_mines(...)` so rules are tested on known layouts, not on seeds.
  - Cells as sets of (row, col) rather than a grid of cell objects: the rules are set operations (revealed | flags, mines - flags) and it serialises small.
  - View board as one string per row (`H`, `F`, `0`-`8`, `M`, `X`, `W`): 480 cells of expert stay a ~500 byte payload per click; rejected an object per cell.
  - Storage: SQLite via stdlib (one row per game, JSON body). Rejected a single JSON file: every click would rewrite every game ever played.
  - Three separate POST actions (reveal, flag, chord) rather than one "click" endpoint: the browser decides only which gesture happened, never what it means.
- Produced: tables at the top of this file.
- Checked: each rule maps to a field or action that can express it (R21 needs `exploded`; R19 needs `started_at`/`finished_at`; R5 needs `seed`).
- Fixed: nothing.

## 4. Wrote the domain tests first (RED)
- Step: Wrote pytest files for R1-R23 against a domain API that did not exist yet, then ran them.
- Decided:
  - The API the tests demand: `Game.new(...)`, `Game.with_mines(...)`, `reveal(row, col, now)`, `toggle_flag(row, col)`, `chord(row, col, now)`, `elapsed(now)`, `mines_remaining`, `board()`, `view(now)`, `to_dict()/from_dict()`, `place_mines(...)`, `neighbours(...)`, `summarize(games)`.
  - Boards in tests are ASCII art (`*` mine, `.` safe) through `tests/helpers.board`, so each expected result can be checked by eye.
  - Test names start with the rule id (`test_r8_...`) so a failing test names the broken rule.
- Produced: `tests/helpers.py`, `tests/test_setup.py`, `tests/test_first_move.py`, `tests/test_play.py`, `tests/test_view_stats_persistence.py`, `pytest.ini`.
- Checked: `python -m pytest -q` -> 4 collection errors, `ModuleNotFoundError: src.domain.game` (the expected RED). Then re-derived every hand-written expected board cell by cell before writing any code.
- Fixed (defects in my own tests, found by the re-derivation, before the domain existed):
  - `test_r8` expected board was wrong (I had written `2221H` for a row that is `2211H`, and a first draft with a nonsensical `or` of two expectations). Recomputed: `0002H / 0002H / 2211H / HHHHH`; kept one exact assertion.
  - `test_r16_win_flags_every_mine` kept revealing after the board was already won on the 2nd reveal, which would raise GameOver. Cut to the two reveals that win.
  - `test_r13` asserted `status == "playing"` after a chord that in fact clears the whole board; changed to "not lost" and let the next test assert the win.
  - Removed an unused first game in `test_r16_win_on_the_very_first_reveal`.

## 5. Wrote the domain (GREEN)
- Step: Implemented `src/domain/minefield.py`, `src/domain/game.py`, `src/domain/stats.py`.
- Decided:
  - Flood fill is an explicit stack, not recursion: a 24x30 open board would exceed Python's recursion limit.
  - Reveal and chord share one `_open(cells)` that settles win/loss, so the two paths cannot disagree about ending the game.
  - Bounds are checked before "game over" so an off-board cell is always OutOfBounds.
  - `GameView` is a separate frozen dataclass built by the domain; the app can only serialise what the domain chose to show.
  - Errors are three exception types under `GameError`, with messages written for a person (they are shown in the UI).
  - On a losing chord the exploded cell is the first mine in reading order (deterministic).
- Produced: the three domain modules.
- Checked: `python -m pytest -q` -> 98 passed on the first run.
- Fixed: nothing; but 98 green on the first run is suspicious, hence step 6.

## 6. Mutation-checked the tests
- Step: Because everything passed first time, checked that the tests can fail: a throwaway script copied the project, broke one rule at a time (18 mutations: flood fill opening flags, no auto-flag on win, only the first cell safe, timer not frozen, mines leaking into the in-play view, wrong flags not marked, chord ignoring flag count, actions after game over, stats counting unfinished games, best time = max, mine cap off by one, seed ignored, ...) and ran the suite.
- Decided: a hand-picked mutation list per rule rather than installing a mutation tool: 2 minutes, targeted at the rules.
- Produced: nothing kept (script lived in a temp folder).
- Checked: 18/18 mutations killed.
- Fixed: nothing. Known blind spot, accepted: "chord on a 0 does nothing" (R14) cannot be observed, since all neighbours of a revealed 0 are already open or flagged; the test documents the intent only.

## 7. Storage adapter and HTTP layer, tests first
- Step: Wrote `tests/test_repository.py` and `tests/test_api.py` (FastAPI TestClient, injected clock / seed / id), then `src/adapters/sqlite_repository.py` and `src/app.py`.
- Decided:
  - `create_app(repository, clock, new_seed, new_id)` factory: the clock and the randomness live at the edge and are injectable, so API tests are deterministic.
  - Error mapping: game over -> 409; off-board / bad configuration / malformed body -> 422; unknown id -> 404. Every error body is `{"detail": "<sentence>"}` (also for request-validation errors, which FastAPI would otherwise return as a list) so the UI can show it as is.
  - A process-wide lock around load-change-save: two fast clicks must not overwrite each other. Rejected per-game locks: single player, not worth it.
  - `GET /api/games` returns summaries without the board (and never mines or seed); `GET /api/stats` is `summarize()` over stored games.
  - The app serves `frontend/dist` when it exists, so the built product runs as one process; dev uses the Vite proxy instead of CORS.
  - `app` is created lazily (module `__getattr__`) so importing `src.app` in tests does not create the real database file.
  - API tests may peek at the stored mines through the repository to steer a game to a win or loss; the API itself gives them no way to.
- Produced: `tests/test_repository.py`, `tests/test_api.py`, `src/adapters/sqlite_repository.py`, `src/app.py`.
- Checked: `python -m pytest -q` -> 116 passed. Honest note: for this step I wrote the tests first but did not run them RED before writing the adapter and app (I did for the domain).
- Fixed: one over-clever assertion in the leak test (string surgery on `"mines_remaining"`) replaced by a plain `'"mines"' not in text` before the first run.

## 8. Designed the page before writing it
- Step: Decided layout, interactions and look.
- Decided:
  - One screen, top to bottom: title; difficulty picker (Beginner / Intermediate / Expert / Custom, custom opens an inline form); board card with mines-left, New game, timer; status line; then Best times and Recent games.
  - Gestures: left click reveals; right click flags; clicking a revealed number chords (no middle-click needed, works on trackpads); touch: long-press flags, plus a visible "Flag mode" toggle because long-press is undiscoverable; keyboard: arrows move, Enter/Space reveal, F flags.
  - The browser only maps a gesture to one of the three actions and renders the returned board. It keeps no rules. The ticking clock is display only: it counts on from the server's `elapsed_seconds`; the final time is the server's.
  - No optimistic updates: the server answers in milliseconds locally, and an optimistic reveal would mean computing rules in the browser. Requests go through a queue so rapid clicks apply in order.
  - The current game id is kept in localStorage, so a reload resumes the game (R23 made visible).
  - Pressing New game on an untouched board does not create another record (avoids piling up empty games).
  - Look: calm slate palette, raised tiles, classic number colours tuned for contrast, light and dark via `prefers-color-scheme` using CSS variables (one set of classes, two palettes). Cell size scales with the viewport between 22 and 34 px; the expert board scrolls sideways on a phone instead of shrinking below a touchable size.
  - Rejected emoji faces for the reset button (render differently per OS); a labelled "New game" button and a result banner say the same thing more clearly.
- Produced: the plan in this entry.
- Checked: against the rule list: every rule a player can observe has a place on the page (R12 counter, R19 timer, R21 loss board, R22 stats).
- Fixed: nothing.

## 9. Built the frontend
- Step: Scaffolded Vite + React 18 + TypeScript + Tailwind by hand and wrote the page.
- Decided:
  - Files: `api.ts` (typed client, one function per endpoint, errors carry the server's sentence), `Board.tsx` (renders the board strings, maps gestures to actions by event delegation on the grid), `Panels.tsx` (difficulty picker, custom form, best times, recent games), `App.tsx` (state, request queue, game card, timer), `format.ts`, `icons.tsx` (inline SVG flag / mine / wrong flag / clock).
  - One event handler set on the grid instead of four per cell: 480 expert cells stay cheap and `Cell` can be memoised on its symbol.
  - Strict TypeScript including `noUncheckedIndexedAccess`.
  - The custom form shows the mine range as a hint computed from the server's limits, but submits whatever is typed and shows the server's refusal: validation stays on the server.
  - StrictMode double-runs effects in dev; a `booted` ref keeps the first load from creating two games.
- Produced: `frontend/` (package.json, vite/tailwind/postcss/ts config, index.html, `src/*`).
- Checked: `npm run build` (tsc + vite) passed first time.
- Fixed: before the first browser run I noticed `border-bad/40` and `ring-accent/30`: Tailwind cannot apply an opacity modifier to a `var()` colour, so those classes would silently produce nothing. Replaced by the plain colours.

## 10. Played it in a real browser: first round
- Step: Started the API (port 8101, scratch database through `MINESWEEPER_DB`) and Vite (5181), opened the page in the browser pane and played with real mouse clicks.
- Decided: verify with real clicks and right-clicks at screen coordinates for the main game, reading the board back from the DOM after each batch; solve the board by actual deduction so the win is a real win.
- Produced: nothing new.
- Checked:
  - First paint: ready board, counter 10, timer 000, no console errors.
  - First click opened an area (R4), status playing, timer started.
  - Right-click flagged three deduced mines, counter 10 -> 7 (R11, R12).
  - Clicking the "1" at row 3 col 3 with its flag placed opened the neighbour (chord, R13).
  - Deduced and clicked every safe cell: status won, all 10 mines shown as flags, counter 0, timer frozen at 043, line "Cleared in 43.4 s. New best for Beginner." (R16, R19); Best times and Recent games updated (R22). A click on the finished board did nothing.
- Fixed:
  - Defect: the board card was far wider than a 9x9 board (about 680px for a 324px board) because the hint text under the board set the card's intrinsic width. Fix: the footer row is `w-0 min-w-full`, so it no longer contributes to the width; card is now 368px. (My first click also missed because the hot reload of this fix shifted the layout mid-click; repeated it.)

## 11. Second round: loss, reload, expert, phone, custom, touch, keyboard
- Step: Drove the remaining paths; where coordinates were impractical (480 cells, touch events) I dispatched real DOM events from the page (click, contextmenu, pointerdown/up with pointerType touch, keydown) and read the DOM back.
- Decided: synthetic events are acceptable for gesture plumbing since they go through the same handlers and the same API; layout was judged from screenshots.
- Produced: nothing new.
- Checked:
  - Loss: clicked hidden cells until a mine; status lost, one `X` (red), the other nine mines shown, the correct flag kept, line "You hit a mine after 0.9 s." (R10, R21).
  - Reload: the lost game came back identical; later a game in progress came back with the timer still running at 017 (R23, R19).
  - Expert: 16 rows, 480 cells, counter 99, first click floods correctly.
  - Phone (375x812): no sideways page scroll; picker wraps to 2x2; beginner cells 33px.
  - Custom: 8 columns x 6 rows with 45 mines was refused by the server and the message shown in the alert; with 6 mines it started (6 rows, 8 columns, counter 6).
  - Touch: long-press before the first reveal flagged the cell and the following click was swallowed (status still ready); a short tap revealed.
  - Flag mode: on -> a click flags; 16 rapid clicks all arrived in order (counter -10, R12); a wrong flag showed as crossed out after the loss (`W`, R21); the toggle disappears when the game is over.
  - Keyboard: ArrowRight moved focus to the next cell; F toggled its flag.
  - Light theme and the one-process mode (API serving `frontend/dist` on 8101) both render and play.
  - Console: only the expected 422 of the refused custom board (and a vibrate warning caused by my synthetic touch). API log: no tracebacks.
- Fixed:
  - Defect: on a 1280px desktop the expert board would have been 34px cells = 1080px wide inside a 1024px column, so it scrolled sideways for no reason (found by reading the numbers at 747px and working out the desktop case). Fix: cell size is now derived from `min(100vw, 64rem)` minus the paddings; at 1280px expert cells are 28.9px and the board does not scroll (measured).
  - Defect: the server said "A 6 x 8 board holds..." (rows x cols) while the page says "8 x 6" (columns x rows), and the off-board message used 0-based "Cell (9, 0)". Changed the API tests first to demand unambiguous wording (2 failed), then the domain messages: "A board of 6 rows and 8 columns holds between 1 and 39 mines." and "Row 10, column 1 is outside the board (9 rows, 9 columns)." 116 passed; verified the new text over HTTP after restarting the API.

## 12. Wrapped up
- Step: Final test and build run, README, requirements.txt, .gitignore, stopped both servers.
- Decided: verification used a scratch database outside the project, so the product starts with empty statistics for its first real player.
- Produced: `README.md`, `requirements.txt`, `.gitignore`.
- Checked: `python -m pytest -q` -> 116 passed; `npm run build` clean; nothing listening on 8101 or 5181.
- Fixed: nothing.

## Known imperfections
- Under about 830px wide the expert board scrolls sideways inside its card (cells are never smaller than 22px). Intermediate does the same on a phone.
- Long-press, flag mode and keyboard were verified with dispatched DOM events, not a physical touch screen or key presses.
- `GET /api/stats` reads every stored game on each call; fine for one player, would want an SQL aggregate for many.
- Every "new game" on a touched board stores a record; unstarted games are never cleaned up (they are excluded from stats and from the recent list).
- "New best" is shown when the win time equals the stored best, so an exact tie also says "new best".
- No question-mark cells, no guaranteed no-guess boards, no player names; mine layouts can require a guess, as in the classic.
- The process-wide lock assumes one server process; several workers would need a database-level transaction around each move.
- For the adapter and HTTP layer I wrote tests before code but did not run them red first.
