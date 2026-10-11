### 1. Default Landing & Cold-Start Behavior

- The page opens directly on the game window, with no intro text, splash or landing copy.
- The board opens at Beginner, 9 columns by 9 rows, all tiles hidden, with no mines placed yet.
- The face shows a smile, the counter shows "010" and the timer shows "000".
- The last chosen level is preselected from device storage; with no stored choice, Beginner is used.
- No shown-to-audience records exist; levels are fixed by the specification and are not loaded from the API.
- Best Times lists Beginner, Intermediate and Expert, each showing "000" and "—" until a record exists.
- If device storage cannot be read, Best Times shows "Best times can't be read on this device." and the game still plays.
- The game needs no loading state: the board is generated locally and appears at once.

### 2. Primary Navigation & View Structure

- The product is one view: the game window, with a "Game" menu in its menu bar.
- The "Game" menu holds, in order: "New", "Beginner", "Intermediate", "Expert", "Custom…", "Marks (?)", "Best Times…".
- "Custom…" opens the Custom dialog; "Best Times…" opens the Best Times dialog; both are small modal windows over the game.
- The New record dialog opens on its own, only after a standard-level win that beats a stored record.
- Escape closes an open menu or dialog; with none open, Escape does nothing.
- "Exit" is omitted; the page has no other views, tabs or navigation.

### 3. Workflow Prerequisites & Form Ergonomics

- The board is usable from the start; no step must be done before a first reveal.
- Custom dialog fields are "Height", "Width" and "Mines", each a number input with min and max set to its range.
- A line under the Custom fields reads "Height 9–24 · Width 9–30 · Mines 10 to (height−1)×(width−1)".
- Out-of-range values are clamped on OK, not refused, so no error message appears for range.
- A non-number entry in a Custom field is ignored and the field reverts to its last valid value.
- The New record name field is a text input, labelled "Name", with maximum length 31 and default value "Anonymous".
- An empty name on OK is saved as "Anonymous"; no message is shown.
- Tiles that cannot be used after a win or loss show no hint; the face already signals the outcome.

### 4. Human Copy & Action Labeling

**Seen:**
- Window title bar: "Minesweeper".
- Menu bar: "Game".
- Game menu: "New (F2)", "Beginner", "Intermediate", "Expert", "Custom…", "Marks (?)", "Best Times…".
- Custom dialog title "Custom"; labels "Height", "Width", "Mines"; buttons "OK", "Cancel".
- Custom range line: "Height 9–24 · Width 9–30 · Mines 10 to (height−1)×(width−1)".
- Best Times dialog title "Best Times"; row labels "Beginner", "Intermediate", "Expert"; empty time "000", empty name "—"; button "Reset Scores", "OK".
- Best Times unreadable message: "Best times can't be read on this device."
- New record dialog title "New record"; line "Enter your name:"; label "Name"; button "OK".

**Spoken only:**
- Mine counter: "Mines left".
- Timer: "Elapsed seconds".
- Face button: "New game".
- Board: "Minesweeper board, 9 by 9".
- Hidden tile: "Hidden, row 3, column 4".
- Flagged tile: "Flagged"; question-marked tile: "Question mark".
- Revealed tile: "Revealed, 2 adjacent mines" or "Revealed, empty".
- Mine tile: "Mine"; exploded mine: "Exploded mine".
- Wrongly flagged tile: "Wrongly flagged".

### 5. Contextual Action Placement

- "New game" (the face button) sits centre of the status panel, on the thing it restarts.
- The mine counter and timer sit either side of the face, inside the same status panel.
- Marks is toggled in the "Game" menu, beside the difficulty choices it affects.
- Reset Scores sits in the Best Times dialog, beneath the list it clears.
- OK and Cancel sit at the bottom right of the Custom dialog, the usual dialog placement.
- The New record OK button sits under the name field it saves.
- Tile actions sit on the tiles themselves: left click reveals, right click or long press flags.

### 6. Visual Direction

- **Feel:** Classic Windows Minesweeper: a grey titled desktop window on a teal desktop, with hard bevels and no rounding.
- **Palette:** Page background teal #008080; window and tile surface #C0C0C0; text #000000; accent (title bar, menu hover) #000080 with white text. Bevel light #FFFFFF, bevel shadow #808080, outer edge #000000. Mine counter and timer: black #000000 box with red #FF0000 digits. Number colours: 1 #0000FF, 2 #008000, 3 #FF0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080. Exploded mine background #FF0000. Title bar when unfocused #808080. Face button yellow #FFFF00 smiley.
- **Type:** Sans family (`font-sans`) for all text, bold for the title and numbers; the counter and timer use `font-mono` bold. The largest text is the title "Minesweeper" at 14px, bold.
- **First screen:** The game window sits at the top centre, 24px below the page top, with the teal desktop filling the rest. Nothing is written above it; the board is visible without scrolling at any common desktop size.
- **Form of the main view:** A Windows Minesweeper window: title bar, menu bar, sunken status panel, then a sunken grid of square tiles. Each tile is a fixed 24px square whatever its content, so the board is 24px × columns by 24px × rows. The window width is the board width plus 24px padding and 8px frame, with a minimum of 260px so the status panel and menu fit; the status panel stretches across the window width. On a screen narrower than the window, the board scrolls horizontally inside its sunken frame. Expert, at 30 columns, is 752px wide.
- **Shape and rhythm:** No corner radius. Bevels are 2px, raised light top-left and dark bottom-right. Spacing inside the window is 4px between rows and 12px padding around the board. The page is dense, with no shadows.

LAYOUT columns=9 rows=9
TOKENS background=#008080 surface=#C0C0C0 text=#000000 accent=#000080 on_accent=#FFFFFF heading=sans