### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the board: difficulty bar, header panel and grid, with Beginner selected and a ready round.
- No text sits above the window; the board is the first thing seen.
- DifficultyLevel records are loaded from the API; the difficulty bar shows `DifficultyLevel.name` for each record, in order.
- While DifficultyLevel records load, the bar shows three grey placeholder tabs of the same width, and the grid shows an empty sunken area.
- If DifficultyLevel is empty, the grid area shows "No difficulties available." in place of the bar's choices.
- If DifficultyLevel fails to load, the grid area shows "Difficulties could not be loaded. Try again." with a button "Try again".
- Board size and mine count come from `DifficultyLevel.width`, `DifficultyLevel.height` and `DifficultyLevel.mine_count`, with Beginner as the initial selection.
- Before the first reveal the mine counter shows the mine count, the timer shows 000, and the face is smiling.
- Hidden cells fill every grid position on the first visit; no cell is revealed or flagged.
- Game records are created on the first reveal or on a difficulty choice; no starting records are supplied by the plan.

### 2. Primary Navigation & View Structure
- One view: the game window. There are no tabs, menus or other pages.
- The difficulty bar sits above the header panel and is always visible.
- The header panel holds mine counter (left), face button (centre), timer (right), in that order.
- The grid sits below the header panel inside the same sunken frame.
- Choosing a difficulty replaces the current round with a new ready round at that size.
- On a narrow screen the window keeps its width and scrolls horizontally inside the page rather than reflowing cells.

### 3. Workflow Prerequisites & Form Ergonomics
- The first reveal is the only step that precedes play; it needs no prompt because every hidden cell accepts it.
- Flagging is available before the first reveal; flagging does not start the timer.
- Mines are placed at the first reveal, so no mine is shown before it.
- A revealed cell ignores flag actions; the click changes nothing and shows no message.
- A flagged cell ignores reveal clicks; nothing changes and no message appears.
- Clicks on any cell after a win or loss do nothing; no message appears.
- Chording with a flag count that differs from the number does nothing; no message appears.
- There are no form fields.

### 4. Human Copy & Action Labeling
**Seen:**
- "Beginner", "Intermediate", "Expert" — difficulty bar, labels from DifficultyLevel.name; the tick marks the current choice.
- Mine counter digits — header, left; mines minus flags, may be negative.
- Timer digits — header, right; elapsed seconds, three digits, capped at 999.
- Face button — header, centre; no visible text.
- "No difficulties available." — grid area, when DifficultyLevel is empty.
- "Difficulties could not be loaded. Try again." — grid area, when DifficultyLevel fails.
- "Try again" — button under the load-failure message; reloads DifficultyLevel.

**Spoken only:**
- Face button: "New round" while at rest, "Won" after a win, "Lost" after a loss.
- Hidden cell: "Hidden cell, column {n}, row {m}".
- Flagged cell: "Flagged cell, column {n}, row {m}".
- Revealed empty cell: "Empty cell, column {n}, row {m}".
- Revealed number cell: "{number} adjacent mines, column {n}, row {m}".
- Mine cell: "Mine, column {n}, row {m}"; triggered mine: "Triggered mine, column {n}, row {m}".
- Wrongly flagged cell: "Wrongly flagged, column {n}, row {m}".
- Difficulty tick: "Selected" on the current difficulty.

### 5. Contextual Action Placement
- Difficulty choice sits in the bar above the window; clicking it starts a new round at that size.
- New round action sits on the face button in the header, at the centre of the window.
- Reveal and chord actions sit on the grid cell clicked.
- Flag and unflag actions sit on the grid cell right-clicked or long-pressed.
- Try again sits under the DifficultyLevel load-failure message in the grid area.
- No action sits outside the window.

### 6. Visual Direction
- **Feel**: classic Windows Minesweeper: a grey, beveled, slightly worn desk tool, familiar at a glance.
- **Palette**: page background #c0c0c0; surface #c0c0c0 for the window, header and bar; text #000000; accent #000080 for the selected difficulty tick and focus outline. Revealed empty cell #c0c0c0 with outline #808080. Bevel light #ffffff, bevel dark #808080, bevel darkest #000000. Number colours: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080. Mine digits and counter box #000000 with red digits #ff0000. Face yellow #ffff00 with black features. Triggered mine background #ff0000. Flag red #ff0000 on black base #000000. Wrong-flag cross #ff0000.
- **Type**: `font-mono` for mine counter and timer digits; `font-sans` for difficulty labels at 13px, weight 400. The largest text on the first screen is the 13px labels, so no heading is shown.
- **First screen**: the difficulty bar, header panel and 9×9 grid, centred on the grey page with 24px of margin on all sides; nothing written above it.
- **Form of the main view**: the familiar Minesweeper form: one window of one width, with a header panel above a square-celled grid. Cells are 24px square, all alike whatever their content; the grid keeps its proportions, so a 30×16 board is 720px by 384px. The header panel is 40px tall. On a narrow screen the window keeps its width and the page scrolls horizontally.
- **Shape and rhythm**: no corner radius; 2px bevels (white top and left, #808080 bottom and right) on raised parts, 2px sunken bevels on the header and grid; 12px between the difficulty bar and header, 8px between header and grid; dense, with no shadows.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans