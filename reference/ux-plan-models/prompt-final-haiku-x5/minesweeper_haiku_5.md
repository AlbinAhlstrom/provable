### 1. Default Landing & Cold-Start Behavior
- The page opens directly on a ready Beginner round: 9×9 grid, 10 mines, no cells revealed, timer at 000.
- The mine counter shows 010 and the face is smiling; nothing is written above the window.
- The difficulty bar fills from `DifficultyLevel.name`, `width`, `height` and `mine_count`, with the Beginner choice ticked.
- While the levels load, the bar shows the text "Loading levels…" in place of the three choices.
- If no levels exist, the bar shows "No levels to choose from." and the board stays unplayed.
- If the levels fail to load, the bar shows "Levels could not load." with a "Try again" button beside it.
- The board itself is never empty: it shows hidden cells from the first frame.

### 2. Primary Navigation & View Structure
- The product is one view: the game window, with no tabs, menus or secondary pages.
- The window holds three stacked parts in order: difficulty bar, header panel, sunken grid.
- The difficulty bar sits above the header, outside the sunken panel but inside the window frame.
- The header holds the mine counter at left, the face button centred, and the timer at right.
- Changing difficulty replaces the whole round and resizes the window to the new grid.
- No separate pages exist for rules, results or history; the outcome shows on the face and grid.

### 3. Workflow Prerequisites & Form Ergonomics
- The timer shows 000 until the first reveal; flagging before that does not start it, and no hint is needed.
- Revealing the first cell is always safe, so no prerequisite message is needed before play.
- Flagging is available from the first frame; no flag is required before revealing.
- A flagged cell ignores left click without a message; the flag itself is the visible feedback.
- A revealed cell ignores flag actions and a mismatched chord without a message.
- After a win or loss, cell clicks do nothing; the face shows the outcome and the face button starts a new round.
- There are no text fields or forms; the only inputs are the difficulty choices, the face button and cell gestures.

### 4. Human Copy & Action Labeling
Seen:
- "Beginner", "Intermediate", "Expert" — from `DifficultyLevel.name`, in the difficulty bar.
- "Loading levels…" — difficulty bar, while records load.
- "No levels to choose from." — difficulty bar, when the list is empty.
- "Levels could not load." — difficulty bar, when the load fails.
- "Try again" — button beside the load-failure message, reloads the levels.
- Page title "Minesweeper" — browser tab only.

Spoken only (screen reader names):
- "Difficulty: Beginner, current" (and the other levels, marked "current" only on the active one).
- "New game" — face button; states the current face as "smiling", "shocked", "sunglasses" or "dead" in its name.
- "Mine counter, 10" and "Timer, 0 seconds".
- "Hidden cell, row 3, column 4"; "Flagged cell"; "Revealed, empty"; "Revealed, 2 adjacent mines"; "Mine"; "Triggered mine"; "Wrongly flagged".

### 5. Contextual Action Placement
- Difficulty choices sit in the bar directly above the header, where the round's size is read.
- The face button sits centred in the header, the single control for restarting the current difficulty.
- Left click, tap or hold on a hidden cell reveals or presses it in place.
- Right-click or long-press on a hidden cell places a flag on that cell.
- Right-click or long-press on a flagged cell removes its flag on that cell.
- Left click on a revealed number cell chords it in place, with no separate chord button.
- No action is placed outside the window, so nothing sits away from the board it affects.

### 6. Visual Direction

- **Feel**: Classic Windows Minesweeper, the grey beveled window of the familiar desktop game, flat and tool-like.

- **Palette**: Page background and surface `#c0c0c0`; text `#000000`; accent `#000080` for the difficulty tick and keyboard focus ring; bevel light `#ffffff`; bevel shadow `#808080`; outer frame `#000000`; counter and timer box `#000000`; counter and timer digits `#ff0000`; flag `#ff0000` on a `#000000` base; face `#ffff00` with `#000000` features; triggered mine background `#ff0000`; mine `#000000`; wrong-flag cross `#ff0000`; number 1 `#0000ff`; number 2 `#008000`; number 3 `#ff0000`; number 4 `#000080`; number 5 `#800000`; number 6 `#008080`; number 7 `#000000`; number 8 `#808080`.

- **Type**: Sans family (`font-sans`) for labels and the difficulty bar, 13px, regular, with the current choice in bold; seven-segment digits in `font-mono` bold. Largest text on the first screen is the mine counter and timer digits at 28px bold.

- **First screen**: The game window centred on the grey page, beginning at its top edge with the difficulty bar, then the header and the Beginner grid. Nothing is written above it; the window is the whole first screen.

- **Form of the main view**: A classic minesweeper board: square cells in a rectangular grid, each cell 24px by 24px and fixed, so the grid's size depends only on the difficulty. A hidden cell is a raised grey square with white top-left and `#808080` bottom-right edges; a revealed empty cell is flat `#c0c0c0` with a thin `#808080` outline. The difficulty bar, header and grid form one unit, one width equal to the grid plus 8px padding, inside one raised window frame. On a screen narrower than the window, the window keeps its size and the page scrolls horizontally, with the window kept centred.

- **Shape and rhythm**: Square corners (0 radius); 2px bevels for raised and sunken parts; no shadows beyond the bevel; cells touch with no gap; 8px padding inside the window; 8px between the difficulty bar, header and grid; very dense, tool-like page.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans