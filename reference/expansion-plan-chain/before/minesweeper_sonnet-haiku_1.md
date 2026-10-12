### 1. Default Landing & Cold-Start Behavior
- No entity is marked "shown to audience"; the page loads no records, so there is no loading, empty or error state for content.
- The page opens directly on a new Beginner game (9×9, 10 mines), in the ready state, with counter "010", face smiling, timer "000".
- The game view is the only view and is active on arrival; nothing is written above it.
- Board shows 81 hidden raised tiles; no tile is revealed and no flag is placed.
- Timer reads "000" and does not run until the first reveal.
- Game state is held in the page only; a reload starts a fresh Beginner game.
- No empty-list or no-results message is needed; the board is always full of hidden tiles.

### 2. Primary Navigation & View Structure
- One view: the Minesweeper game window; there are no tabs, menus or secondary pages.
- Window order top to bottom: difficulty bar, header panel, board.
- Difficulty bar holds three choices in this order: "Beginner", "Intermediate", "Expert".
- Current difficulty choice is shown with a sunken button; the others are raised.
- Header panel holds, left to right: mine counter, face button, timer.
- Board sits below the header panel inside a sunken border.
- Choosing a difficulty or pressing the face button replaces the board in place; no page change occurs.
- On a narrow screen the window keeps its full size and the page scrolls horizontally rather than reflowing the board.

### 3. Workflow Prerequisites & Form Ergonomics
- No step depends on another step being done first; the first reveal is the only start, and it needs no setup.
- Flagging is allowed before the first reveal and does not start the timer.
- Flagging a revealed tile does nothing; no message is shown.
- Clicking a flagged tile does nothing; no message is shown.
- Any reveal, flag or chord after a win or loss does nothing; no message is shown.
- A chord whose flag count does not match its number does nothing; no message is shown.
- A chord on a zero tile does nothing; no message is shown.
- Difficulty choices and the face button are always enabled, including mid-game, and restart the game immediately.
- No form fields exist; there are no inputs, validation or refused-entry messages.

### 4. Human Copy & Action Labeling
- Seen: "Beginner", "Intermediate", "Expert" on the difficulty choices.
- Seen: the counter and timer carry numbers only; no captions are shown.
- Seen: no headline, instruction or footer text is written on the page.
- Spoken only: difficulty buttons "Beginner difficulty", "Intermediate difficulty", "Expert difficulty"; the current one also reads "selected".
- Spoken only: face button "New game"; its state names read "shocked", "won", "lost" or "smiling" as the face shows.
- Spoken only: mine counter "Mines left, [value]"; timer "Seconds elapsed, [value]".
- Spoken only: each hidden tile "Hidden tile, row [r], column [c]"; flagged tile "Flagged tile, row [r], column [c]"; revealed tile "[n] adjacent mines" or "Empty" for zero.
- Spoken only: the board "Minesweeper board, [columns] by [rows]".
- Spoken only: a flagged tile on a loss "Wrong flag"; an exploded mine "Exploded mine".

### 5. Contextual Action Placement
- Reveal and chord actions sit on the tile clicked; flag action sits on the tile right-clicked or long-pressed.
- Difficulty choices sit in the bar above the window content, where they change the whole game.
- The face button sits centred in the header, the only control that restarts the current difficulty.
- No action sits outside the window; there are no action bars, dialogs or confirmation prompts.
- Hold feedback sits on the face: shocked while a tile is pressed, returning on release.

### 6. Visual Direction

- **Feel**: Classic Windows Minesweeper: a grey beveled utility window with a sunken grid and seven-segment LED readouts.
- **Palette**: Page background #c0c0c0; window surface #c0c0c0; text #000000 on grey; accent #000080 for the focus outline; black #000000 LED panels with red #ff0000 digits; hidden tile #c0c0c0 with bevel white #ffffff and dark grey #808080; revealed tile #c0c0c0 flat with 1px outline #808080; number colours 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080; flag red #ff0000 on black #000000 base; exploded mine background #ff0000; face yellow #ffff00 with black outline.
- **Type**: Sans-serif system UI for all text (font-sans); LED digits use a seven-segment rendering in red on black; largest text is the timer and counter digits at 28px bold.
- **First screen**: The game window centred on the grey page at its natural size, with the difficulty bar, header and Beginner board fully visible without scrolling on a 1024px-wide screen; no text above it.
- **Form of the main view**: Familiar Minesweeper grid: square tiles of 24px, no gaps, board sized 9 columns by 9 rows for Beginner (216px square) with the header above it; tiles keep fixed size and the whole board keeps its proportions; Intermediate and Expert change the column and row count but not the tile size; on narrow screens the window keeps its width and scrolls horizontally.
- **Shape and rhythm**: Square corners (0 radius); 2px raised bevels (white top-left, #808080 bottom-right); 1px outlines; 8px padding inside the window frame; 6px spacing between difficulty choices and header; no shadows; dense layout.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans