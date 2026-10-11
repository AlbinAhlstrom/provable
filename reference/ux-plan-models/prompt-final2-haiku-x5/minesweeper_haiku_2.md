### 1. Default Landing & Cold-Start Behavior

- The page opens on one view: the Minesweeper window, centred on the grey page, with Beginner active.
- On first visit the board shows a 9×9 grid of hidden cells, mine counter "010", timer "000", smiling face.
- No mines are placed until the first reveal; the opening board carries no mine data.
- `DifficultyLevel.name` fills the difficulty bar: one choice per record, in record order.
- While `DifficultyLevel` records load, the bar shows "Loading levels…" in place of the choices, and the board area stays empty.
- If `DifficultyLevel` records are empty, the bar shows "No difficulty levels are available." and the board area stays empty.
- If `DifficultyLevel` records fail to load, the bar shows "Difficulty levels could not be loaded." with a "Try again" button beside it.
- `DifficultyLevel.width`, `height` and `mine_count` set the board size and mine count of each choice when a round starts.
- `Game` is not shown to the audience; the board is the game, created when a difficulty is chosen.

### 2. Primary Navigation & View Structure

- The product is one view; there are no tabs, pages, menus or secondary screens.
- The difficulty bar sits above the window's header panel, reached first on every screen.
- Header panel order is fixed: mine counter left, face button centre, timer right.
- Grid sits below the header panel, inside a sunken bevelled frame.
- Selecting a difficulty or pressing the face button replaces the current round in place; the page never navigates.
- On screens narrower than the window, cells keep 16px size and the grid frame scrolls horizontally; the header and bar do not wrap.

### 3. Workflow Prerequisites & Form Ergonomics

- No step needs another first: the board is playable as soon as it shows, and flagging before the first reveal is allowed.
- Clicking a flagged cell, a revealed cell without chording, or any cell after win or loss does nothing and shows no message.
- A chord with a flag count that differs from the number does nothing and shows no message.
- A difficulty choice is disabled while the round is being created, to prevent duplicate rounds.
- There are no form fields; the product asks for no text input.

### 4. Human Copy & Action Labeling

**Seen**
- "Beginner", "Intermediate", "Expert": difficulty bar, from `DifficultyLevel.name`, in the bar above the header.
- "✓": tick marking the current difficulty, beside its name in the bar.
- "Loading levels…": difficulty bar, while records load.
- "No difficulty levels are available.": difficulty bar, when the list is empty.
- "Difficulty levels could not be loaded.": difficulty bar, when the load fails.
- "Try again": button beside the load-failure message, reloads `DifficultyLevel` records.

**Spoken only**
- Face button: "New game".
- Difficulty choice: "Start a [DifficultyLevel.name] game", with "current" when ticked.
- Mine counter: "Mines left [number]".
- Timer: "Seconds elapsed [number]".
- Hidden cell: "Hidden, row [n], column [n]".
- Flagged cell: "Flagged, row [n], column [n]".
- Revealed empty cell: "Empty, row [n], column [n]".
- Revealed number cell: "[number] adjacent mines, row [n], column [n]".
- Mine or triggered mine: "Mine, row [n], column [n]".
- Wrongly flagged cell: "Wrong flag, row [n], column [n]".
- Round state change: "Round won" or "Round lost", announced once in a live region.

### 5. Contextual Action Placement

- Difficulty choices sit in the bar above the header, the only place a round is started by choice.
- The face button sits centred in the header, the only place a round is restarted at the current difficulty.
- Reveal and chord act on the cell clicked; flag acts on the cell right-clicked or long-pressed.
- Hold-to-press feedback shows on the hidden cell being held, and the face turns shocked for that duration.
- "Try again" sits beside its load-failure message in the difficulty bar.

### 6. Visual Direction

- **Feel**: Classic Windows Minesweeper: grey beveled window, sunken panels, square cells, flat and unadorned.
- **Palette**: Page and window #c0c0c0, text #000000, accent navy #000080 for the window title bar and focus outline. Cell and counter colours are fixed by the specification: number digits 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080; mine #000000; triggered mine background #ff0000; counter and timer digits #ff0000 on #000000; bevel white #ffffff and dark grey #808080; face yellow #ffff00 with black features.
- **Type**: Sans family (`font-sans`) for the difficulty bar, MS Sans Serif style fallback at 13px regular; digits in the counter and timer are seven-segment drawn, not typed; largest text on screen is 13px.
- **First screen**: The window opens at once, with the difficulty bar, header and 9×9 hidden grid visible; no text introduces it and nothing sits above it.
- **Form of the main view**: The familiar Windows Minesweeper window, one unit of one width inside one frame. Cells are 16×16px, all alike, fixed size; the window is sized to its content, so the grid is 144×144px at Beginner, 256×256px at Intermediate and 480×256px at Expert. A hidden cell is a raised grey square; a revealed empty cell is flat light grey with a thin outline, blank.
- **Shape and rhythm**: Square corners, no shadows; 2px bevels in white and #808080; 8px padding inside the window; 8px between header panel and grid; 8px between difficulty bar and window; dense, with no decoration.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans