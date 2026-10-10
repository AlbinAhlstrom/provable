### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the playable board at Beginner (9×9, 10 mines), status ready, with no overlay or introduction.
- No "shown to audience" entity is loaded; DifficultyLevel records are the three presets, so the difficulty bar is built from DifficultyLevel.name in order Beginner, Intermediate, Expert.
- While DifficultyLevel records load, the difficulty bar shows its three labels greyed with no tick and the grid area shows a blank sunken panel.
- If DifficultyLevel records are empty, the difficulty bar shows "No levels available" and the grid stays blank with the face button disabled.
- If DifficultyLevel records fail to load, the difficulty bar shows "Levels could not load. Try again." with a "Try again" button beside it.
- Game board is ready before any reveal: mine counter shows the difficulty's mine count, timer shows 000, face is smiling.
- Hidden cells fill the grid from the first visit; no empty-state text is needed because the board is always present.
- Mines are not placed until the first reveal; the grid shows only hidden cells on cold start.

### 2. Primary Navigation & View Structure
- One view only: the game window. No tabs, menus, accounts or secondary pages.
- Window contains, top to bottom: difficulty bar, header panel, grid.
- Difficulty bar sits above the header panel, inside the same window frame.
- Selecting a difficulty replaces the current round with a new ready round at that size; no confirmation.
- Grid is always the active area; no separate win or loss screens, outcome is shown in the header and on the board.
- Round outcome is conveyed by the face button and the board states only.
- On narrow screens (below 420px wide) the window keeps its fixed pixel width and scales down uniformly using CSS transform so the whole board stays visible without horizontal scrolling.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; all interaction is by cell, face button and difficulty choices.
- Flagging is available before the first reveal; the timer does not start until the first reveal.
- Mines are not shown until the first reveal, so no prerequisite message is needed.
- Reveal, chord and flag actions on a ready, in-progress board are always enabled.
- Clicking a flagged cell does nothing; no message is shown.
- Clicking or right-clicking a revealed cell (except chord) does nothing; no message is shown.
- After a win or loss, cell clicks do nothing; no message is shown, the face and board show the outcome.
- Chording a number whose flag count differs from its number does nothing; no message is shown.
- Face button and difficulty bar remain active at all times, including after a win or loss.

### 4. Human Copy & Action Labeling
**Seen:**
- "Beginner", "Intermediate", "Expert" — difficulty bar labels, above the header panel.
- "Levels could not load. Try again." — difficulty bar, on DifficultyLevel load failure.
- "Try again" — button beside that message.
- "No levels available" — difficulty bar, when DifficultyLevel is empty.
- No other visible text; the board, counter, timer and face carry their state without words.

**Spoken only:**
- Difficulty tick: "Current difficulty: Beginner" (name taken from DifficultyLevel.name).
- Face button: "New game" at rest, "Game won" after win, "Game lost" after loss.
- Each hidden cell: "Hidden cell, row {row_index}, column {column_index}".
- Flagged cell: "Flagged cell, row {row_index}, column {column_index}".
- Revealed number cell: "{adjacent_mine_count}, row {row_index}, column {column_index}".
- Revealed empty cell: "Empty, row {row_index}, column {column_index}".
- Mine cell: "Mine, row {row_index}, column {column_index}".
- Mine counter: "Mines remaining: {value}".
- Timer: "Time: {elapsed_seconds} seconds".

### 5. Contextual Action Placement
- Face button sits centred in the header panel, between the mine counter and timer.
- Difficulty choices sit in the bar above the header, on the window's top edge.
- Reveal, flag and chord actions sit on the cell itself; no separate action bar.
- Mine counter sits left of the header; timer sits right of the header.
- "Try again" for DifficultyLevel load failure sits beside its message in the difficulty bar.
- No other actions exist on the page.

### 6. Visual Direction
- **Feel**: classic Windows Minesweeper: grey beveled chrome, sunken panels, red LED digits, familiar to anyone who has played it.
- **Palette**: page background #c0c0c0; window surface #c0c0c0; text #000000; accent #000080 for the selected difficulty tick and focus outlines; raised bevel white #ffffff top-left, #808080 bottom-right, outer dark #000000; revealed cell surface #c0c0c0 with outline #808080; counter and timer panel #000000 with digits #ff0000; number colours 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080; mine #000000 on #c0c0c0; triggered mine background #ff0000; flag #ff0000 on #000000 base; wrong flag cross #ff0000; face yellow #ffff00 with black features.
- **Type**: `font-mono` for mine counter and timer digits (bold, 23px); `font-sans` system UI for difficulty labels (13px, regular); no heading text.
- **First screen**: the window centred on the page at its natural size, board fully visible with the difficulty bar, header and all hidden cells, with no text above it.
- **Form of the main view**: classic Minesweeper form: a single framed window of fixed width, a sunken grid of square cells. Cells are 16×16px fixed each, grid spacing 0; Beginner 9×9 cells, Intermediate 16×16, Expert 30×16 (columns×rows) each cell fixed size, the window width grows with columns, not the cells. Header panel is 42px tall, counter and timer boxes 39×23px, face button 26×26px. Window padding 6px; on screens narrower than the window, the whole window scales down uniformly to fit.
- **Shape and rhythm**: square corners (0 radius) everywhere; 2px raised and sunken bevels, no shadows; spacing 6px between difficulty bar, header and grid; dense, no decorative spacing.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans