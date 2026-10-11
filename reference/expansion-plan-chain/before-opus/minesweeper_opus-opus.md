### 1. Default Landing & Cold-Start Behavior
- No entity is marked "shown to audience". Game is created by the player, so nothing loads from records and no loading, empty or error states are needed.
- The page opens on the single game view with a Beginner 9×9 board, 10 mines, round in state ready.
- If a difficulty and Marks setting were saved on this device, the board opens at that difficulty with that Marks setting.
- A saved Custom difficulty restores its last clamped height, width and mines.
- On first visit, Marks is off and Beginner is checked in the Game menu.
- The mine counter reads "010", the timer reads "000", the face is smiling and every square is hidden.
- The board is never empty. Before any click, the full grid of raised hidden squares is the familiar starting state.
- No welcome text, instructions or overlay appear. The board itself is the invitation to click.

### 2. Primary Navigation & View Structure
- The product has one view: "Minesweeper", the game window centred on the teal page.
- The only navigation is the "Game" menu in the menu bar. It opens a dropdown and never changes views.
- The Custom Field dialog is a modal over the game window. It is centred on the window and the board behind it is inert.
- The dropdown opens on click of "Game". It closes on choosing an item, clicking outside, or pressing Escape.

### 3. Workflow Prerequisites & Form Ergonomics
- Uncovering needs nothing first. The first click is always safe, and mines are placed after it.
- Flagging before the first uncover is allowed and leaves the timer at 000.
- Chording needs matching flags. When they don't match, releasing does nothing, with no message.
- Clicking a flagged square does nothing silently.
- Clicking or right-clicking an uncovered square does nothing silently, except for chording.
- After a win or loss, every square ignores input silently. The face shows the outcome and is the way on.
- The menu and the face stay usable in every round state.
- A long-press on touch lasts 400 ms and flags the square. A short tap uncovers it; a tap on a number chords it.
- If the pointer drags off a square before release, the uncover is cancelled and the pressed look follows the pointer.
- The face shows its open "O" mouth while a square is held.
- Custom Field has a "Height" number input, prefilled with the current height, min 9, max 24.
- Custom Field has a "Width" number input, prefilled, min 9, max 30.
- Custom Field has a "Mines" number input, prefilled, min 10, max (height−1)×(width−1).
- Custom values are never refused. On OK each is clamped to its nearest limit; an empty or non-numeric field becomes its minimum.
- Mines are clamped after height and width are clamped.
- In the dialog, Enter presses OK and Escape presses Cancel. Cancel leaves the current game untouched.
- F2 starts a new game at any time, except while the dialog is open.

### 4. Human Copy & Action Labeling
**Seen**
- "Game": the menu bar item.
- "New": first menu item, with "F2" right-aligned in the same row.
- "Beginner", "Intermediate", "Expert", "Custom…", "Marks (?)": the remaining menu items, in that order.
- A divider line sits after New and another after Custom….
- "Custom Field": the dialog title bar.
- "Height", "Width", "Mines": the field labels, each left of its input.
- "OK", "Cancel": the dialog buttons.
- Counter and timer digits are drawn as seven-segment figures, not text, for example "010", "000", "-05".
- Numbers 1–8 appear on uncovered squares.
- "?" appears on question-marked squares.
- There are no win or loss sentences. The face, the board reveal and the stopped timer carry the outcome.

**Spoken only**
- Face button: "New game".
- Mine counter: "Mines left: {n}".
- Timer: "Seconds: {n}".
- Board grid: "Minefield, {height} rows by {width} columns".
- Squares: "Row {r}, column {c}", followed by the square's state.
- The square states are spoken as "hidden", "flagged", "question mark", "empty", "{n}", "mine", "exploded mine" and "wrong flag".
- On game end, a polite live region announces "Won" or "Lost".
- Check marks are spoken as "checked" on the current difficulty and on Marks when it is on.

### 5. Contextual Action Placement
- New game sits on the face, centred in the top panel above the board it resets, and is duplicated in Game → New.
- Difficulty, Custom… and Marks (?) sit in the Game menu at the top-left of the window.
- Uncover, flag, mark and chord happen on the squares themselves.
- OK and Cancel sit bottom-right in the dialog, with OK first.

### 6. Visual Direction
**Feel**: Classic Windows 3.1/95 Minesweeper, pixel-exact bevelled silver on teal and instantly recognisable.

**Palette**
- Page background: teal #008080.
- Window, menu, panel and squares: silver #c0c0c0.
- Bevel light: #ffffff.
- Bevel dark and grid lines: #808080.
- Outer border and text: #000000.
- Menu highlight and title bar: navy #000080, with white #ffffff text.
- Counter and timer: background #000000, digit #ff0000, unlit segments #3a0000.
- Face: #ffff00 with a #000000 outline and features.
- Exploded square: #ff0000.
- Mine: #000000 with a #ffffff glint.
- Flag: #ff0000 triangle on a #000000 pole and base.
- Wrong-flag X: #ff0000.
- Number colours: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080.
- Dialog inputs: #ffffff with a sunken bevel.

**Type**
- `font-sans` carries the menu, dialog and labels at 13px, weight 400, in black.
- Numbers on squares are 16px bold `font-sans`.
- The largest element on the first screen is the red seven-segment digits, 26px tall and drawn as SVG segments.

**First screen**
- The game window sits centred horizontally on the teal page, 48px from the top. Nothing sits above or around it.
- Inside the window, from top to bottom: the menu bar (20px), the top panel, then the board.

**Form of the main view**
- The window is one bevelled unit; menu, panel and board share its width.
- The window has a 1px black border, a 3px raised bevel and 6px inner padding.
- The top panel is 46px tall with a 2px sunken bevel and 6px horizontal padding.
- The counter and timer boxes are each 52×32px with a 1px sunken bevel.
- The face button is 34×34px with a 2px raised bevel and a 24px face. It shows the sunken bevel when pressed.
- Squares are fixed 24×24px, all alike, with a 3px raised bevel when hidden.
- Uncovered squares are flat, with a 1px #808080 line on their top and left edges.
- The board frame is a 3px sunken bevel, and the grid keeps fixed proportions.
- Beginner is 216px of grid, Intermediate 384px, and Expert 720×384px.
- On screens narrower than the window, the window keeps its size and the page scrolls horizontally. Squares never shrink below 24px.

**Shape and rhythm**
- Corners are square, radius 0.
- There are no shadows; bevels only.
- The layout is dense, with the 6px spacing set out above. The dialog is 240px wide with 10px padding.

LAYOUT columns=9 rows=9
TOKENS background=#008080 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans