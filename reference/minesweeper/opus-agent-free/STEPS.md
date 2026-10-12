# STEPS: Minesweeper from the pitch "A minesweeper game"

## Rule list (behaviours the product must have)

Board and setup
- R1. Three classic levels: Beginner 9x9 / 10 mines, Intermediate 16x16 / 40, Expert 30x16 / 99. Plus Custom (5-40 columns, 5-30 rows, 1 to cells-9 mines).
- R2. Mines are placed on the first reveal, never before. The first revealed cell and its 8 neighbours are mine-free, so the first click always opens an area.
- R3. Exactly the configured number of mines is placed, uniformly at random among allowed cells.

Play
- R4. Revealing a safe cell shows the count of mines in its 8 neighbours (blank for 0).
- R5. Revealing a 0 cell flood-opens all connected 0 cells and their numbered border. Flagged cells are not opened by the flood.
- R6. Flag toggles on a hidden cell (right-click / long-press / F key / flag mode). A flagged cell cannot be revealed.
- R7. Chord: activating a revealed number whose flagged-neighbour count equals the number opens its other hidden neighbours. A wrong flag there means a mine blows up.
- R8. Revealing a mine loses: the hit mine is highlighted, all other mines are shown, wrong flags are marked, the board locks.
- R9. Win when every safe cell is revealed (flags are not required). Remaining mines are auto-flagged, the board locks.

HUD
- R10. Mine counter = mines minus flags (may go negative).
- R11. Timer starts on the first reveal, stops on win or loss, shows whole seconds capped at 999.
- R12. New-game button (face) restarts the same level; face shows state (playing, pressing, won, lost).
- R13. Outcome is announced in text (not only by a face or colour), with the time, and whether it is a new best.

Around the game
- R14. Best time, games played and wins are kept per board configuration in localStorage.
- R15. Chosen level, theme and a game in progress survive a page reload (timer continues from where it was).
- R16. Fully playable by keyboard: arrows move, Enter/Space reveal or chord, F flags, R / F2 new game. Visible focus.
- R17. Playable by touch: tap reveals, long-press flags, and a Dig/Flag mode switch for people who dislike long-press.
- R18. Works on a phone-width screen (cells resize; a board too wide scrolls inside its own frame, the page does not).
- R19. Light and dark theme (follows the system, can be switched).
- R20. Screen readers get a labelled grid: each cell says its row, column and state.
- R21. Runs by opening index.html directly, no build step, no network.

## Definition of done

- Every rule above is covered by an automated check: pure-logic rules by Node unit tests, UI rules by a headless-browser script that actually plays (click, right-click, keyboard, touch long-press, reload).
- A full game is won and a full game is lost in a real browser engine, with the right HUD/outcome each time.
- No console errors or failed requests during those runs.
- I have looked at screenshots of: fresh board, mid-game, lost, won, Expert, phone width, dark theme, and fixed what looked wrong.
- README says how to run and test it.

## Steps

### 1. Read the pitch and listed the rules
- Step: Wrote down what "a minesweeper game" has to do before touching code (the rule list above), from the classic Windows game plus what people expect in a browser today (touch, keyboard, persistence).
- Decided:
  - First click opens an area (cell + neighbours safe), not just "first click is not a mine". Reason: a lone "1" on the first click forces a guess, the most common complaint about naive clones.
  - Flag only, no question-mark state. Rejected the classic three-state cycle: it adds an extra click to un-flag and most players turn it off.
  - No "no-guess board generator" (needs a solver; a large feature with subtle bugs). Recorded as a known limit instead.
  - Win does not require flags. That is the classic rule and avoids a "why have I not won" confusion.
  - Custom mines capped at cells-9 so R2 can always hold. Rejected a fallback rule for denser boards: one more branch for boards nobody enjoys.
- Produced: the rule list and definition of done at the top of this file.
- Checked: Re-read the list against my memory of the classic game: counter may go negative, timer caps at 999, chord exists, wrong flags shown on loss. All present.
- Fixed: nothing yet.

### 2. Chose technology and structure
- Step: Picked the stack and the file layout.
- Decided:
  - Plain HTML + CSS + JavaScript, no framework, no build. Reason: the whole product is one screen; a toolchain would only add ways to fail to run. Rejected React/Vite.
  - Classic scripts, not ES modules. Reason: ES modules do not load from file:// in Chrome, and I want double-click-to-run (R21). The engine uses a small UMD wrapper so Node tests can require it.
  - Game rules in a pure engine (`src/engine.js`, no DOM) and a separate UI (`src/app.js`). Reason: the rules can be unit-tested in milliseconds and the UI cannot corrupt them.
  - Data model: flat typed arrays indexed `row * cols + col` (`mine`, `adj`, `state`), plus `status` (ready/playing/won/lost), counters and `exploded`. Rejected a 2-D array of cell objects: slower to flood-fill, harder to serialise.
  - Engine functions mutate the game and return the list of changed cell indexes, so the UI repaints only those. Rejected immutable copies: 480 cells copied per click for no benefit.
  - Injectable random source and a `?seed=` URL parameter. Reason: deterministic boards for the browser test (and repeatable boards for players).
  - DOM buttons for cells, not canvas. Reason: free keyboard focus and screen-reader support (R16, R20); 480 buttons is cheap.
  - Inline SVG symbols for flag and mine, not emoji. Reason: emoji look different (or are missing) per platform.
- Produced: folder layout: `index.html`, `styles.css`, `src/engine.js`, `src/app.js`, `tests/engine.test.js`, `tests/e2e.py`.
- Checked: nothing to run yet.
- Fixed: nothing.

### 3. Wrote the rules engine
- Step: Wrote `src/engine.js`: presets, config clamping, seeded generator, `createGame`, `reveal`, `toggleFlag`, `chord`, `serialize`, `deserialize`.
- Decided:
  - Mines are placed inside the first `reveal`, sampling with a partial Fisher-Yates over the cells outside the protected 3x3. Rejected "place first, then move a mine if the first click hits one": biased and does not give an opening.
  - Flood fill with an explicit stack, not recursion. Reason: a 40x30 board of zeros would overflow the call stack.
  - On loss the engine only records `status` and `exploded`; showing the other mines is the UI's job. Reason: keeps `state` meaning "what the player did".
  - On win the engine flags the remaining mines itself, so the counter reads 0 from one source of truth.
  - `deserialize` validates everything (sizes, characters, mine total, status) and returns null on any doubt. Reason: a saved game comes from localStorage, which I do not control.
  - Bad indexes are ignored rather than thrown: the UI should never crash a game on a stray event.
- Produced: `src/engine.js`.
- Checked: by the tests in step 4.
- Fixed: nothing at this point.

### 4. Wrote unit tests for the engine and ran them
- Step: Wrote `tests/engine.test.js` (Node's built-in test runner, no dependencies), one or more tests per rule R1-R9 and R15, named by rule. Boards are drawn as ASCII pictures so the expected numbers can be read off by eye.
- Decided:
  - Pictures go through the public `serialize`/`deserialize` instead of a test-only back door, so the tests use only what the UI uses.
  - First-click safety is checked over 200 seeds x 3 levels with a varying first cell, not one example, because it is a property of random output.
  - Added a coverage test (every non-protected cell gets a mine at least once in 300 boards) to catch an off-by-one in the sampling.
- Produced: `tests/engine.test.js`, `package.json` (scripts only).
- Checked: `node --test tests/`. First run: 12 passed, 9 failed.
- Fixed: The 9 failures were my tests, not the engine: I had drawn 3x3 and 3x5 pictures, and the engine (correctly) rejects boards under 5x5 or with more than cells-9 mines. Redrew the pictures as 5x5 boards and recomputed the expectations by hand. Second run: 21 passed, 0 failed. I did not loosen the engine's limits to make the tests pass.

### 5. Built the page: markup, UI logic, styling
- Step: Wrote `index.html` (HUD with mine counter, face button, timer; level switch; board; status line; Dig/Flag switch; stats; how-to-play; custom-board dialog), `src/app.js` (rendering, input, clock, stats, save/restore, theme) and `styles.css`.
- Decided:
  - Left-click on a revealed number chords (as well as middle-click). Rejected "both buttons at once": undiscoverable, impossible on a trackpad.
  - Touch: long-press (400 ms) flags, and a visible Dig/Flag switch as the alternative. In Flag mode the long-press digs, so both actions are always reachable.
  - Long-press is my own timer on pointer events; the browser's `contextmenu` is ignored for touch. Reason: iOS never fires it and Android fires it late, so relying on it would double-toggle or do nothing.
  - Outcome shown inline under the board in words, no modal. Reason: after losing, people want to look at the board, not dismiss a popup.
  - Only changed cells are repainted per move; the whole board only at game end.
  - Roving tabindex: the board is one tab stop, arrows move inside. Rejected 480 tab stops.
  - Cell size is computed from the window (24-40 px). A board that still does not fit scrolls inside its own frame so the page never scrolls sideways.
  - One localStorage key holding level, theme, stats and the game in progress. Stats are keyed by board configuration, so custom boards get their own best time.
  - The clock pauses while the tab is hidden. Reason: a phone call should not ruin a time; you cannot see the board while hidden anyway.
  - Stats count finished games only; an abandoned game is not a loss. Simple and not punishing.
  - Switching level or restarting mid-game needs no confirmation (classic behaviour, and one key brings a new game anyway).
  - Custom dialog refuses illegal values with the reason and the allowed range, rather than silently clamping them.
  - Kept a read-only `window.__minesweeper` handle so the browser test can find mines. Rejected hiding it behind a flag: it changes nothing a player could not do in dev tools.
- Produced: `index.html`, `src/app.js`, `styles.css`.
- Checked: by step 6 (I did not trust reading the code).
- Fixed: see step 6.

### 6. Wrote a browser test that plays the game, ran it, fixed what it found (round 1)
- Step: Wrote `tests/e2e.py`: drives headless Chrome through a fresh board, first click, flags, chord, keyboard, a full win, a full loss, restart, all levels, the custom dialog, reload/restore, themes, corrupt storage, and a phone-sized touch session (real touch events through the browser's input pipeline, including a 650 ms hold). It opens `index.html` from disk, which also proves R21. It collects console errors.
- Decided:
  - False start: I wrote it for Playwright first; `import playwright` failed (not installed in this Python). Rather than download packages, I checked what was installed, found Selenium 4, and rewrote the script on Selenium + Chrome DevTools commands (needed for touch and colour-scheme emulation).
  - The test reads mine positions from the live game so it can win on purpose, lose on purpose and place a deliberately wrong flag. Assertions are on what the player sees (classes, counter text, status text), not only on engine state.
  - Seeded boards (`?seed=7`) for repeatability, plus one unseeded run so `Math.random` is exercised too.
- Produced: `tests/e2e.py`, screenshots in `tests/screenshots/`.
- Checked: `python tests/e2e.py`. First run: 80 passed, 7 failed.
- Fixed:
  - Product defect: on a 375 px phone the Beginner board was 4 px wider than its frame and scrolled. `fitBoard` forgot the board's own 2 px padding. Corrected the arithmetic (26 -> 30).
  - Product weakness found while debugging a test: the page rewrites its whole store on unload, so a second open tab would overwrite the first tab's stats. Added a `storage` listener that picks up the other tab's stats and theme.
  - Test defects (4 theme checks): headless Chrome inherited my machine's dark mode, and clearing localStorage mid-page was undone by the unload save. Pinned the colour scheme per browser and used a fresh profile for the "system dark" check.
  - Test defects (2 custom-dialog checks): I typed "r" into a number field then Backspace, which turned 20 mines into 2. Replaced it with a direct check that R does not restart the game while the dialog is open.
  - Second run: 88 passed, 0 failed, no console errors.

### 7. Looked at the screenshots and fixed what looked wrong (round 2)
- Step: Opened the screenshots the test wrote: mid-game, won, lost, Expert, custom dialog, dark + lost, phone, phone Expert.
- Decided:
  - Outcome messages shortened to one line ("Boom! You hit a mine.", "Cleared in 3.1 s. New best time!"). The long versions repeated what the face button already offers.
  - During play the status line shows "N safe squares to go". Rejected an empty line (left a dead gap under the board) and rejected collapsing it (the Dig/Flag switch would jump under a finger).
- Produced: edits to `styles.css`, `src/app.js`, `index.html` unchanged.
- Checked: Compared screenshots before/after; reran `python tests/e2e.py`: 88 passed.
- Fixed:
  - Defect: the game panel changed width when the game ended (404 px while playing, 584 px after losing) because the outcome text widened it, so the board visibly jumped. The status row now takes its width from the board (`width: 0; min-width: 100%`) and sits on its own centred line.
  - Defect: on the phone there was an empty band between the board and the Dig/Flag switch during play. Filled by the progress text above.
  - Looked for and did not find: unreadable number colours in dark theme, clipped HUD on 375 px, Expert overflowing a 1280 px window.

### 8. Checked that the tests can fail (mutation check)
- Step: Broke the engine on purpose in 7 ways, one at a time (opening not protected, chord with too few flags, flag not blocking a reveal, flood stopping short, win one cell early, one mine too few, flood pushing through flags) and ran the unit tests against each.
- Decided: Done with a throwaway script outside the project that restores the file afterwards; not worth keeping as a permanent tool.
- Produced: nothing kept.
- Checked: 6 of 7 mutants caught. The seventh ("flood pushes flagged neighbours") is not a real bug: the pop-side guard still skips flagged cells, so behaviour is identical. The push-side check is only an optimisation.
- Fixed: nothing needed. Suite green again on the restored file (21/21).

### 9. Ran it over HTTP on port 5182, wrote the README, final run
- Step: Served the folder with `python -m http.server 5182`, ran the browser test against it, stopped the server and confirmed the port no longer answers. Wrote `README.md`. Final run of both suites.
- Decided: README leads with double-click, since that is the lowest-effort way to run it.
- Produced: `README.md`.
- Checked: over HTTP 88/88, from disk 88/88, unit tests 21/21, no console errors or failed requests in any run.
- Fixed: nothing.

## Known limits (not fixed)
- Boards are random, not guaranteed solvable by logic: a game can still end in a forced guess.
- Expert on a phone scrolls sideways inside its frame (cells are kept at 24 px so they stay tappable); there is no pinch-zoom.
- Touch was verified with emulated touch events in desktop Chrome, not on a physical phone; iOS Safari and Firefox were not run.
- The pause-while-tab-hidden clock and the two-tab `storage` sync were written but have no automated check.
- No question-mark marks, no sound, no hint button, no online leaderboard (deliberate scope).
- Face button uses emoji, so its look depends on the platform's emoji font.
