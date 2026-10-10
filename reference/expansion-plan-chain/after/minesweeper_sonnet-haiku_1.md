### 1. Default Landing & Cold-Start Behavior

- The page opens directly on the game window: a ready Beginner board, mine counter at 010, face smiling, timer at 000.
- No entity is marked "shown to audience", so no records load and no loading, empty or error state is needed.
- The board is generated locally, so it appears at once with no loading state.
- Every cell opens covered and blank; no hint, tutorial or introductory text appears above or beside the window.
- Marks is off by default, so the Game menu opens with Marks unticked.
- Beginner is ticked by default in the Game menu.

### 2. Primary Navigation & View Structure

- The product is one view: the Minesweeper window, with no other pages or tabs.
- The only navigation is the menu bar's single "Game" menu, opened by click and closed by click elsewhere or Escape.
- Game menu order: "New" (F2), divider, "Beginner", "Intermediate", "Expert", "Marks (?)".
- The face button and the Game menu both start a new round at the current level.
- Changing level in the menu starts a fresh round immediately, with no confirmation.

### 3. Workflow Prerequisites & Form Ergonomics

- Before the first reveal, flags can be placed, but the timer stays at 000 and the counter reflects flags.
- The first reveal places mines around itself, so the player never needs to set up a layout first.
- Chording is offered only on revealed numbers; a number with a wrong flag count does nothing when chorded.
- After a win or loss, the board ignores clicks and the face shows the result until "New" is used.
- Right-click on a revealed cell is ignored; no message is shown.
- Left-click on a flagged cell is ignored; no message is shown.
- Starting a new round discards the current round without confirmation, so no dialog is planned.
- There are no form fields; the product takes input only through cells, the face and the menu.

### 4. Human Copy & Action Labeling

Seen:
- "Minesweeper" in the title bar, beside the mine icon.
- "Game" as the menu bar label.
- "New  F2" as the first menu item, with its shortcut shown at the right.
- "Beginner", "Intermediate", "Expert" as level menu items, each ticked when current.
- "Marks (?)" as the toggle menu item, ticked when on.
- The mine counter and timer show digits only; no captions or units are added.

Spoken only:
- Each covered cell: "Covered cell, row R, column C".
- Each revealed cell: "Empty", or its number, e.g. "Revealed, 2 adjacent mines".
- Flagged cell: "Flagged"; marked cell: "Question mark".
- Mine counter: "Mines remaining"; timer: "Seconds elapsed".
- Face button: "New game", with state as "Smiling", "Surprised", "Sunglasses" or "Dead".

### 5. Contextual Action Placement

- The face button sits centred in the status panel, the one place to restart from the board.
- The mine counter and timer sit either side of the face, the status they describe.
- Flag and question-mark actions sit on the covered cell itself, via right-click or long-press.
- Reveal and chord actions sit on the cell itself, via left-click or tap.
- Level and Marks settings sit in the Game menu, the only place they are changed.
- The New action sits in the Game menu beside its F2 shortcut, and also on the face button.

### 6. Visual Direction

- **Feel**: the classic Windows desktop Minesweeper: a small grey program window on a flat teal desktop, square-edged and bevelled.
- **Palette**: desktop teal #008080; window and covered cells grey #C0C0C0; revealed empty cells #DCDCDC; bevel highlight #FFFFFF, shadow #808080; title bar and selected menu item navy #000080; text black #000000; counter and timer boxes black #000000 with red #FF0000 digits; flag red #FF0000 on black base; face yellow #FFFF00 with black features; mine black with white glint; clicked mine background red #FF0000; number colours: 1 #0000FF, 2 #008000, 3 #FF0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080.
- **Type**: `font-sans` for title, menu and labels, bold; `font-mono` bold for the seven-segment-style digits and revealed numbers. Largest text on the first screen is the 14px bold "Minesweeper" title bar text.
- **First screen**: the game window sits exactly centred horizontally and vertically on the teal desktop, with nothing else on screen. The window's status panel, board and menu bar are visible without scrolling at Beginner.
- **Form of the main view**: the classic Minesweeper form: a rectangular grid of square cells in a sunken frame, with a status panel above. Cells are 24px square, all alike, and do not scale with content. The Beginner window is 246px wide: a 9-cell board of 216px, plus 3px sunken frame each side, 8px padding each side and 4px window bevel each side. The status panel and menu bar stretch across the board width. On a screen narrower than the window, the window keeps its size and the page scrolls; Intermediate and Expert boards scroll sideways inside their sunken frame.
- **Shape and rhythm**: square corners throughout; no radius, no drop shadow. Bevels are 2px, white top and left, #808080 bottom and right, with 8px between window edge and content. Dense layout with no decorative spacing, and the status panel sits 8px above the board.

LAYOUT columns=9 rows=9
TOKENS background=#008080 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans