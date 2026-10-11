### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the board in ready state: no splash, no intro text, no modal.
- The difficulty bar sits above the header; Beginner is ticked by default.
- The header shows mine counter "010", face button smiling, timer "000".
- The grid shows 9×9 hidden cells; no mines are placed until the first reveal.
- No entity is "shown to audience" from the API: DifficultyLevel records are the three presets from the specification and are shown as the bar's labels; if the load fails, the bar shows "Difficulty unavailable" and the board stays on Beginner.
- While DifficultyLevel records load, the bar shows three greyed labels "Beginner", "Intermediate", "Expert" with no tick, and the grid is not yet drawn.
- If DifficultyLevel loads empty, the bar shows the three specification presets so the game stays playable.
- Board ready state has no separate empty-state message; the hidden grid is the empty state.

### 2. Primary Navigation & View Structure
- One view only: the game board window. No tabs, no menus, no secondary pages.
- Order inside the window: difficulty bar, header panel (mine counter, face button, timer), sunken grid.
- Difficulty bar items in order: "Beginner", "Intermediate", "Expert".
- Selecting a difficulty starts a new ready round at that size; the bar does not change view.
- Board is a fixed-size window: cells are 24px square; the window fits its content and does not scroll on desktop.
- On a screen narrower than the window (under 480px), the board scales down uniformly so the whole grid remains visible; cells are no smaller than 16px and the Expert grid scrolls horizontally if it still does not fit.

### 3. Workflow Prerequisites & Form Ergonomics
- Revealing is available from the start; no prerequisite step is required.
- Flagging is available in ready state; it does not start the timer.
- Timer sits at "000" until the first reveal; no message explains this.
- Chording is offered only on revealed number cells; hidden cells are not chordable.
- Refused actions do nothing and show no message: revealing a flagged cell, flagging a revealed cell, any cell click after win or loss, chording with mismatched flags.
- No forms or text fields exist; difficulty is chosen by button only.

### 4. Human Copy & Action Labeling
**Seen**
- Difficulty bar labels: "Beginner", "Intermediate", "Expert".
- Window title bar: "Minesweeper".
- Difficulty indicator: a tick mark beside the current label.
- Mine counter: digits only, no caption.
- Timer: digits only, no caption.
- Face button: image only, no text.
- Loss and win are shown by the face and board, not by sentences.

**Spoken only**
- Difficulty bar: "Beginner difficulty", "Intermediate difficulty", "Expert difficulty"; current one also "selected".
- Face button: "New game" (on the face button).
- Mine counter: "Mines remaining: [value]".
- Timer: "Elapsed seconds: [value]".
- Hidden cell: "Hidden cell, row [r], column [c]".
- Flagged cell: "Flagged cell, row [r], column [c]".
- Revealed empty cell: "Empty cell".
- Revealed number cell: "[n] adjacent mines".
- Mine: "Mine". Triggered mine: "Mine, triggered". Wrongly flagged: "Wrongly flagged cell".
- Grid: "Minesweeper grid, [width] by [height]".

### 5. Contextual Action Placement
- Difficulty choices sit in the bar above the header, the only place difficulty changes.
- The face button sits centred in the header and is the only restart control.
- Reveal, flag and chord actions sit on the cell they change.
- Hold-to-press visual appears on the hidden cell under the pointer.
- The mine counter and timer sit in the header, left and right of the face button, where the player reads them.
- No action bar, toolbar or context menu exists.

### 6. Visual Direction
- **Feel**: Classic Windows XP-era Minesweeper: a grey beveled utility window, flat and tactile.
- **Palette**: Page background `#c0c0c0`; window surface `#c0c0c0`; text `#000000`; accent `#000080` (selected difficulty tick and focus). Hidden cell face `#c0c0c0` with white `#ffffff` top-left and `#808080` bottom-right bevel. Revealed cell `#c0c0c0` flat with `#808080` 1px outline. Number colours: 1 `#0000ff`, 2 `#008000`, 3 `#ff0000`, 4 `#000080`, 5 `#800000`, 6 `#008080`, 7 `#000000`, 8 `#808080`. Counter and timer box `#000000` with red `#ff0000` digits. Triggered mine background `#ff0000`. Flag `#ff0000` on `#000000` base. Face yellow `#ffff00` with black features.
- **Shared surfaces**: Hidden cells, flags and the mine counter sit on the grey `#c0c0c0` surface; number colours at 1 to 8 range from light to dark, so the grey middle tones keep the darkest and lightest digits readable: numbers 1 to 8 are drawn on `#c0c0c0` and `#c0c0c0` is a middle tone between `#ffffff` and `#000000`.
- **Type**: Sans-serif system UI for the window title only (`font-sans`, 12px, bold); digits in the counter and timer are a seven-segment style in red on black, 28px tall; cell numbers are bold `font-sans` 14px.
- **First screen**: The board itself, centred on the grey page, with the difficulty bar, header and grid as one window. No headline, no text above it.
- **Form of the main view**: Classic Minesweeper form: one window, header strip above a square-celled grid. Cells are 24px squares, all alike whatever they hold; the grid keeps its proportions as a rectangle of width × height cells. Header is 40px tall, spanning the grid width. Window has 4px padding and a 3D bevel of 2px.
- **Shape and rhythm**: Square corners (0px radius) everywhere. Bevels are 2px: white top and left, `#808080` bottom and right. No shadows. Gap of 8px between difficulty bar, header and grid. Dense: no whitespace beyond the 4px window padding.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans