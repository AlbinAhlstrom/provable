### 1. Default Landing & Cold-Start Behavior
- Arrival shows the game window itself: Beginner 9×9 board in ready state, counter "010", timer "000", smiling face. No intro text.
- Beginner is the current difficulty on arrival, marked with a tick in the difficulty bar.
- DifficultyLevel records (`DifficultyLevel.name`, `.width`, `.height`, `.mine_count`) fill the difficulty bar and size each new board.
- While DifficultyLevel loads: the bar shows three grey placeholder slots, and the board, counter, timer and face are shown disabled and unplayable.
- If DifficultyLevel is empty: the bar shows "No difficulties available" and no board is drawn; the face stays visible.
- If the DifficultyLevel load fails: the bar shows "Couldn't load difficulties." with a "Try again" button.
- Empty places: a board with no mines placed yet has no empty state; hidden cells are the classic look. Nothing else can be empty.

### 2. Primary Navigation & View Structure
- One view only: the game window. Nothing else is offered: no tabs, menus, settings, scores or account surfaces.
- The difficulty bar is the only navigation, and it starts a new round rather than changing view.

### 3. Workflow Prerequisites & Form Ergonomics
- No step needs another done first: the first reveal places mines, and flagging works before it without starting the timer.
- Chording on a number whose flags differ from its number does nothing, silently.
- Click on a flagged cell, a revealed empty cell, or any cell after win or loss does nothing, silently.
- Flagging a revealed cell does nothing, silently. After win or loss, flagging does nothing.
- Face button and difficulty choices are always allowed and start a new ready round at once, with no confirmation.
- There are no form fields.

### 4. Human Copy & Action Labeling
- **Seen**:
- "Beginner", "Intermediate", "Expert": difficulty bar, from `DifficultyLevel.name`; the current one carries a "✓" tick.
- "No difficulties available": difficulty bar when the list is empty.
- "Couldn't load difficulties.": difficulty bar on failed load.
- "Try again": button beside that message.
- Mine counter digits (e.g. "010", "-02") and timer digits (e.g. "000"): header. The state is told by the face and board, so no win or loss sentence is added.
- Digits 1–8 on revealed cells.
- **Spoken only**:
- Face button: "New game"; the state is spoken as "Smiling", "Shocked", "Cool, you won" or "Dead, you lost".
- Mine counter: "Mines left".
- Timer: "Seconds elapsed".
- Hidden cell: "Hidden, row R column C".
- Flagged cell: "Flag, row R column C".
- Revealed cell: "N mines nearby" or "Empty".
- Mine cell: "Mine". Triggered mine: "Mine, triggered". Wrong flag: "Wrong flag".
- Difficulty bar: "Difficulty". The current choice is announced as "selected".

### 5. Contextual Action Placement
- Difficulty choices sit in the bar above the header and start a new round.
- Face button sits centred in the header and restarts at the current difficulty.
- Reveal, flag and chord happen on the cells themselves: left click or tap, right-click or long-press, and a click on a number cell.
- Counter sits left and timer right in the header. Both are display only.

### 6. Visual Direction
- **Feel**: Classic Windows Minesweeper: a grey, beveled desktop window, crisp and unrounded, with a pixel-precise 3D look.
- **Palette**: page background #c0c0c0; window surface #c0c0c0; text #000000; accent #c0c0c0 (the raised face button). Bevel light #ffffff, bevel dark #808080, outline #7b7b7b. Revealed cell #bdbdbd. Digit box #000000 with digits #ff0000. Face yellow #ffff00 with black features. Flag red #ff0000 on base #000000. Mine #000000. Triggered background #ff0000. Wrong-flag cross #ff0000. Numbers: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080. Tick #000000.
- **Type**: `font-mono` for all text; the digits are red seven-segment style at 26px tall in the counter and timer. Cell digits are bold at 16px. The difficulty bar is 14px regular. There are no headings.
- **First screen**: the window is centred on the grey page. From top to bottom: the difficulty bar, the sunken header (counter, face, timer), and the sunken 9×9 grid. Nothing is written above the window.
- **Form of the main view**: one unit in one frame, as in classic Minesweeper. Cells are 24×24px, all alike, in a fixed-proportion grid (Beginner 216×216, Expert 720×384). The header spans the grid width. The face button is 40×40px. A window narrower than the screen scrolls horizontally inside the page and does not shrink the cells. Touch uses long-press to flag.
- **Shape and rhythm**: 0 radius and 2–3px bevels (white top and left, #808080 bottom and right; sunken is the reverse). Window padding is 6px and header padding 4px. It is dense, with no gaps between cells.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#c0c0c0 on_accent=#000000 heading=mono