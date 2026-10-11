### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the game: a Beginner 9×9 board in ready state, mine counter at 010, timer at 000, face smiling.
- No splash screen, intro text or landing page precedes the board.
- No game entity is loaded from a server; the board is generated locally in the browser on load.
- DifficultyLevel records (name, width, height, mine_count) are loaded from the API; while loading, the difficulty bar shows "Loading levels…" in place of the three choices and the grid area stays blank.
- If the DifficultyLevel load fails, the difficulty bar shows "Levels could not load." and the face button still starts a Beginner round from the built-in preset.
- If the DifficultyLevel list is empty, the difficulty bar shows "No levels available." and the Beginner round still opens.
- Mines are not placed until the first reveal; the ready board shows all cells hidden.
- No cell state is persisted; a page reload starts a fresh ready round at the last chosen difficulty.

### 2. Primary Navigation & View Structure
- One view only: the game window. No tabs, menus, accounts or secondary pages.
- Difficulty bar sits above the window and lists Beginner, Intermediate, Expert in that order.
- The current difficulty carries a tick; choosing another starts a new ready round at that size immediately.
- Header panel, then grid, stacked inside the single window frame.
- Face button and difficulty bar are the only controls outside the grid; no other navigation exists.
- On a screen narrower than the window, the window keeps its fixed pixel width and the page scrolls horizontally rather than reflowing cells.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; all input is by clicking, tapping or holding cells and buttons.
- Flagging is available before the first reveal; it does not start the timer.
- Chording is offered only on revealed number cells; hidden and flagged cells never chord.
- A flagged cell click does nothing, with no message shown.
- A revealed cell click or right-click does nothing, with no message shown.
- After a win or loss, cell clicks and flag actions do nothing; the face button and difficulty bar remain fully active.
- Chording with a flag count that differs from the number does nothing; no message is shown.
- The face button is always enabled; it never needs a prerequisite.

### 4. Human Copy & Action Labeling
Seen text:
- "Beginner" — difficulty bar, first choice, with tick when current.
- "Intermediate" — difficulty bar, second choice, with tick when current.
- "Expert" — difficulty bar, third choice, with tick when current.
- "Loading levels…" — difficulty bar, while DifficultyLevel loads.
- "Levels could not load." — difficulty bar, on failed load.
- "No levels available." — difficulty bar, when the list is empty.
- No other visible text; the counter and timer are digits only, and state is shown by the face and the board.

Spoken only (accessible names):
- "New game" — face button.
- "Mine counter, [n] mines remaining" — counter box.
- "Timer, [n] seconds" — timer box.
- "Hidden cell, row [r], column [c]" — hidden cell.
- "Flagged cell, row [r], column [c]" — flagged cell.
- "Revealed empty cell" / "Revealed cell, [n] adjacent mines" — revealed cells.
- "Mine" / "Triggered mine" / "Wrongly flagged cell" — loss-state cells.
- "Game board" — grid container.
- "Difficulty: [name], current" — difficulty choice with tick.

### 5. Contextual Action Placement
- Face button sits centred in the header, the only restart control, acting on the whole game.
- Difficulty choices sit above the window, acting on the whole game as a new round.
- Flag and reveal actions are on the cell itself; no separate action bar exists.
- Chord action is on the revealed number cell itself, triggered by a click.
- Mine counter sits left of the header; timer sits right of the header; both are read-only.
- No confirmation step precedes a new round; restarting an in-progress round is immediate.

### 6. Visual Direction

- **Feel**: Classic Windows Minesweeper: grey, beveled, utilitarian, instantly recognisable.
- **Palette**: Page background #c0c0c0 (flat mid-grey); window surface #c0c0c0; primary text #000000; accent #000080 (selected tick and highlights); revealed empty cell #c0c0c0 with outline #808080; hidden cell face #c0c0c0 with white #ffffff top-left and #808080 bottom-right bevel; sunken panel edges #808080 and #ffffff; counter and timer background #000000 with digits #ff0000; flag #ff0000 on base #000000; mine #000000 with spikes; triggered mine background #ff0000; wrongly flagged cross #ff0000; number colours: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080; face yellow #ffff00 with black features.
- **Type**: `font-mono` for counter and timer digits, bold; `font-sans` (system UI, bold 12px) for difficulty labels; no headings exist.
- **First screen**: The game window centred on the grey page, header panel above a Beginner 9×9 grid, difficulty bar above the window; nothing written above the board. The window is the first and only thing seen.
- **Form of the main view**: Classic Minesweeper grid: a rectangle of square cells, 24×24px each, all alike whatever they hold; the whole keeps its fixed proportions (9 columns × 9 rows at Beginner, 16×16 at Intermediate, 30×16 at Expert). The header panel spans the full grid width, with counter left, face centred, timer right. On a narrower screen the window keeps its pixel width and the page scrolls horizontally.
- **Shape and rhythm**: Square corners (0px radius); 2px raised or sunken bevels built from white, #808080 and #000000 edges; no shadows; 16px spacing between the difficulty bar and the window; dense, tool-like layout with no decorative padding.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans