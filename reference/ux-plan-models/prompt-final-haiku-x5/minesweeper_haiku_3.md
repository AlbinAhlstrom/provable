### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the playable board at Beginner (9×9, 10 mines), status ready, nothing written above it.
- Mine counter shows "10" and timer shows "000" at rest; face button shows smiling expression.
- No splash, intro, or welcome text; no entity records load before play, as the game has no shown-to-audience records beyond the three difficulty presets.
- Difficulty presets are fixed in the page's own data (Beginner, Intermediate, Expert) and render immediately; no loading state is needed for them.
- If the page cannot start a round, the board area shows "Could not start a round. Try again." with a "Try again" button in the header's place.
- No empty-state needed: the board always holds cells in ready state.

### 2. Primary Navigation & View Structure
- One view only: the game screen. No tabs, menus, or secondary pages.
- Difficulty bar sits directly above the header panel, with three choices in order: "Beginner", "Intermediate", "Expert".
- Current difficulty carries a tick mark (✓) before its label.
- Header panel sits above the grid: mine counter left, face button centre, timer right.
- Grid sits below the header, inside one sunken bevelled frame; no separate scroll region on desktop.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; all interaction is by cell and button.
- Flagging is available before the first reveal; the timer does not start until the first reveal.
- The first reveal always opens an area; no prerequisite step is shown.
- Revealed cells ignore plain clicks and flag actions silently; no message is shown.
- Flagged cells ignore reveal clicks silently; no message is shown.
- After a win or loss, cell clicks and flag actions do nothing; the face button and difficulty bar stay active.
- Chording with mismatched flags does nothing silently.
- Long-press on touch must not both reveal and flag: long-press flags, a short tap reveals.
- Right-click menu is suppressed on the grid.

### 4. Human Copy & Action Labeling
Seen:
- "Beginner" — difficulty bar, top left of the bar.
- "Intermediate" — difficulty bar.
- "Expert" — difficulty bar.
- "Could not start a round. Try again." — board area, only if round creation fails.
- "Try again" — button replacing the header, only in the failure case above.
- Status for the face button, read as state, not text: no visible words on the board beyond the above.

Spoken only:
- Face button: "New game" (named by its function; the face itself is the visual).
- Cell hidden: "Hidden cell, row {r}, column {c}".
- Cell flagged: "Flagged cell, row {r}, column {c}".
- Cell revealed empty: "Empty revealed cell".
- Cell revealed number: "Revealed cell, {n} adjacent mines".
- Cell mine after loss: "Mine".
- Cell triggered mine: "Triggered mine".
- Cell wrongly flagged: "Wrongly flagged cell".
- Mine counter: "Mines remaining, {n}".
- Timer: "Elapsed seconds, {n}".
- Difficulty tick: "Current difficulty".

### 5. Contextual Action Placement
- Face button sits in the header, centred, and is the only restart control on the board.
- Difficulty choices sit above the header and start a new round on selection.
- Flag placement and removal happen on the cell itself (right-click or long-press).
- Reveal and chord happen on the cell itself (click or tap).
- The mine counter and timer sit in the header; they display state and carry no actions.
- No action sits outside the board and its header.

### 6. Visual Direction
- **Feel**: Classic Windows Minesweeper, a grey beveled window of 1990s desktop software, recognised at once by people who know the game.
- **Palette**: Page background `#c0c0c0`; surface `#c0c0c0` (window and header); text `#000000`; accent `#000080` for the current difficulty tick and focus outline; hidden cell face `#c0c0c0` with white `#ffffff` top-left and `#808080` bottom-right bevel; revealed cell `#c0c0c0` with `#808080` 1px outline; counter and timer box `#000000` with red digits `#ff0000`; number colours 1 `#0000ff`, 2 `#008000`, 3 `#ff0000`, 4 `#000080`, 5 `#800000`, 6 `#008080`, 7 `#000000`, 8 `#808080`; flag `#ff0000` on `#000000` base; triggered mine background `#ff0000`; face yellow `#ffff00` with black features.
- **Type**: `font-mono` for the counter and timer digits (bold, 24px); `font-sans` (system sans, 13px) for the difficulty bar and spoken labels; largest text on first screen is the counter digits at 24px bold.
- **First screen**: Difficulty bar at top left of the window, header panel beneath it, 9×9 grid below, all centred on the grey page. No headline, no image, no introductory text.
- **Form of the main view**: Classic Minesweeper form: a single window with a 1px-bevel frame, header and grid as one unit. Cells are 24×24px fixed, all alike; the grid keeps its natural size, 9 columns × 24px = 216px wide at Beginner. Header is 24px tall, counter and timer boxes 39×23px. On a screen narrower than the window, the window centres and the grid scrolls horizontally inside its sunken frame; nothing is resized.
- **Shape and rhythm**: Square corners (radius 0); bevels 2px outset/inset; no drop shadow; 8px spacing between difficulty bar and header, 4px between header and grid; dense layout.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=mono