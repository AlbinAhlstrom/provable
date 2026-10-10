### 1. Default Landing & Cold-Start Behavior

- The page opens directly on the Minesweeper window at Beginner: a ready game with 9×9 hidden cells, counter "10", timer "000", smiling face.
- Game menu `DifficultyLevel.name` records fill the Beginner, Intermediate and Expert items, each carrying its size and `mine_count`.
- While DifficultyLevel records load, the three level items show disabled as "Loading levels…"; New and Custom… stay usable.
- If DifficultyLevel is empty, the Game menu shows one disabled line "No levels available." Custom… stays usable.
- If DifficultyLevel fails to load, the Game menu shows "Levels could not be loaded." with a "Retry" item; the open Beginner board stays playable.
- Game board (`Game.cells`) starts as hidden cells only; no mines exist until the first reveal.
- Best Times dialog shows "No time yet" for any level without a stored best; it never shows an empty list.
- The Custom dialog opens pre-filled with 9, 9 and 10.

### 2. Primary Navigation & View Structure

- The product is one view: the Minesweeper window. There are no tabs and no separate pages.
- The Game menu is the only menu: New, Beginner, Intermediate, Expert, Custom…, Marks (?), Best Times….
- Game menu opens on click or Alt+G; arrow keys move between items; Escape closes it.
- Custom… and Best Times… open as modal dialogs over the window; Cancel, OK or Escape closes them.
- F2 starts a new game at the current level from anywhere in the window.
- On a screen narrower than the window, the window keeps its size and the page scrolls horizontally.
- Expert's 480px-wide grid scrolls inside the sunken grid frame; the header stays fixed above it.

### 3. Workflow Prerequisites & Form Ergonomics

- Flags may be placed before the first reveal; they do not start the timer, and the counter drops at once.
- No mines are shown or counted before the first reveal; the counter shows the level's mine count until then.
- Chord on a number with mismatched flags does nothing and gives no message.
- Right-click cycle skips "?" entirely while Marks is off, so the cycle reads hidden to flag to hidden.
- Clicks on any cell after a win or loss are ignored with no message; the face already shows the outcome.
- Custom fields: Height, Width and Mines accept whole numbers only; OK is always enabled.
- Out-of-range Custom values are clamped silently on OK; the fields show the clamped value when the dialog reopens.
- A non-number entry is refused with the message "Enter a whole number." beside the field; OK does not start a game.
- Mines field limit is `(height−1)×(width−1)` and updates when Height or Width changes before OK.

### 4. Human Copy & Action Labeling

- Window title bar: "Minesweeper".
- Menu entry: "Game"; items: "New", "Beginner", "Intermediate", "Expert", "Custom…", "Marks (?)", "Best Times…".
- Custom dialog title "Custom Field"; labels "Height", "Width", "Mines"; buttons "OK", "Cancel".
- Custom refusal message: "Enter a whole number."
- Best Times dialog title "Best Times"; rows "Beginner", "Intermediate", "Expert" with value "{n} seconds" or "No time yet".
- Best Times buttons: "Reset Scores", "OK".
- Level items in menu are labelled with `DifficultyLevel.name`, never retyped.
- Menu load messages: "Loading levels…", "No levels available.", "Levels could not be loaded.", "Retry".
- Spoken only: hidden cell "Hidden, row {r} column {c}"; revealed "Empty" or "{n} adjacent mines"; flagged "Flagged"; question mark "Question mark"; mine "Mine".
- Spoken only: counter "Mines left {n}"; timer "Seconds {n}"; face "New game" and its states "Winning" and "Lost".

### 5. Contextual Action Placement

- Face button sits centre of the header and is the only New game control on the board.
- Cell actions (reveal, flag, question mark, chord) live on the cell itself, not in any panel.
- Marks (?) toggle sits in the Game menu only, with its tick showing its state.
- Best Times "Reset Scores" sits bottom-left of its dialog, OK bottom-right, both beside the times they affect.
- Custom OK and Cancel sit bottom-right of the Custom Field dialog.
- Level choice sits only in the Game menu; the header carries no level control.

### 6. Visual Direction

- **Feel**: a Windows 95-era Minesweeper: a grey titled window on a teal desktop, flat, bevelled, and built from classic chrome.
- **Palette**: desktop #008080 (teal); window surface #C0C0C0 (grey); text #000000; title bar and menu highlight #000080 (navy); bevel light #FFFFFF and dark #808080; LED digits #FF0000 on #000000; number 1 #0000FF, 2 #008000, 3 #FF0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080; exploded mine background #FF0000; face yellow #FFFF00 with black features.
- **Type**: bold sans-serif (`font-sans`) for the title, menu and dialog text at 12px; numbers on cells bold 14px; LED digits drawn as seven-segment shapes.
- **First screen**: the window sits centred both ways on the teal desktop, with menu bar, header and the Beginner grid visible, and nothing else on screen.
- **Form of the main view**: the Minesweeper window as one unit, a grey frame with title bar, menu bar, sunken header and sunken grid. Cells are fixed 16px squares, all alike; the grid is a fixed-proportion rectangle. The window width is the grid width (9×16=144px at Beginner) plus 8px frame, with the header stretched to fill it at a minimum of 152px; Expert grows to 480px plus frame and scrolls on narrow screens. A hidden cell is a raised 16px square; a revealed cell is flat #C0C0C0 with a 1px #808080 outline.
- **Shape and rhythm**: square corners throughout; 2px bevels on raised and sunken parts; no shadows or rounding; 4px spacing inside the header and 6px around the grid; dense, with no empty margins inside the window.

LAYOUT columns=9 rows=9
TOKENS background=#008080 surface=#C0C0C0 text=#000000 accent=#000080 on_accent=#FFFFFF heading=sans