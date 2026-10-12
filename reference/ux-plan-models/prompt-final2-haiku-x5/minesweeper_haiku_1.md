### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the board: difficulty bar, header panel, and grid, all visible without scrolling. No intro text above it.
- Initial round is Beginner (9×9, 10 mines) in ready state; Beginner carries the tick in the difficulty bar.
- Grid shows 81 hidden raised cells; mine counter reads 010; face smiling; timer reads 000.
- DifficultyLevel records (name, width, height, mine_count) fill the difficulty bar labels; while they load, the bar shows three greyed placeholders reading "Loading levels…".
- If DifficultyLevel records are empty, the bar shows "No levels available" and the grid stays hidden; no starting records are supplied by the page.
- If DifficultyLevel load fails, the bar shows "Levels could not load. Try again." with a button "Retry" beside it.
- Game is created in ready state; no mines exist yet, so mines_placed is false.
- No empty-list state beyond the difficulty bar; the board always has cells.

### 2. Primary Navigation & View Structure
- One view only: the game board. No tabs, menus or separate pages.
- Difficulty bar sits directly above the header panel, in the window's top strip.
- Header panel holds, left to right: mine counter, face button (centred), timer.
- Grid sits below the header panel inside the sunken frame.
- Selecting a difficulty replaces the current round with a new ready round at that size; the view stays the same.
- On narrow screens the window keeps its fixed pixel width and the page scrolls horizontally; nothing reflows.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; all interaction is by cell and button.
- Flagging before the first reveal is allowed and does not start the timer; no prompt is needed.
- Timer starts only on first reveal; the timer box reads 000 until then.
- Revealed cells ignore left-click (except chord on numbers) and right-click; no message appears.
- Flagged cells ignore left-click; no message appears.
- Clicks after win or loss do nothing; no message appears.
- Chord with mismatched flag count does nothing; no message appears.
- Face button and difficulty bar always remain enabled.

### 4. Human Copy & Action Labeling
Seen:
- "Beginner", "Intermediate", "Expert" — difficulty bar labels, shown in that order, with a tick on the current one (from DifficultyLevel.name).
- "Loading levels…" — difficulty bar while records load.
- "No levels available" — difficulty bar when no records.
- "Levels could not load. Try again." — difficulty bar on failed load.
- "Retry" — button beside the load-failure message.
- Mine counter and timer show digits only; no captions.

Spoken only:
- Face button: "New round" (on the face, the button's name).
- Each hidden cell: "Hidden cell, column {column}, row {row}".
- Flagged cell: "Flagged cell, column {column}, row {row}".
- Revealed empty: "Empty cell".
- Revealed number: "{n} adjacent mines".
- Mine: "Mine". Triggered mine: "Triggered mine". Wrong flag: "Wrongly flagged cell".
- Mine counter: "Mines remaining {value}". Timer: "Elapsed {seconds} seconds".
- Difficulty choices: "Select {name}"; current one also "current".

### 5. Contextual Action Placement
- Difficulty choice sits in the bar above the header, the only place difficulty is picked.
- New round action sits on the face button, centred in the header it resets.
- Reveal and flag actions sit on the cell themselves; there is no separate toolbar.
- Chord action sits on the revealed number cell it applies to.
- Retry for a failed difficulty load sits beside its message in the difficulty bar.

### 6. Visual Direction
- **Feel**: classic Windows Minesweeper: grey beveled window, sunken panels, crisp pixel-like cells.
- **Palette**: page background #c0c0c0; surface #c0c0c0 (window and header); text #000000; accent #000080 for the selected difficulty tick and focus outline. Hidden cell face #c0c0c0 with white top-left (#ffffff) and dark bottom-right (#808080) bevels. Revealed cell flat #c0c0c0 with outline #808080. Counter and timer boxes #000000 with digits #ff0000. Number colours: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080. Flag: red #ff0000 on black base #000000. Triggered mine background #ff0000. Face yellow #ffff00 with black features.
- **Type**: sans, system UI, bold 20px for the mine counter and timer digits in monospace-like seven-segment style; body 12px.
- **First screen**: window centred on the grey page, difficulty bar on top, header panel, then the 9×9 grid. Nothing above the window.
- **Form of the main view**: a classic Minesweeper window of one fixed width; grid of square cells 24×24px each (Beginner 216px wide, Expert 720px wide), all alike whatever each holds; the window keeps fixed proportions; on narrow screens it scrolls horizontally. Header panel 40px tall; face button 26×26px; counter and timer 13×23px digit boxes.
- **Shape and rhythm**: square corners everywhere; 2px bevels; no shadows beyond bevel; 8px padding in window; 4px gap between header and grid; dense layout.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans