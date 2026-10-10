# Minesweeper

## 1. People and their journey

**Player** (the only role; the intent names a single-player game for people who play for fun)

- Needs to see: the board, which cells are hidden, revealed or flagged, the number of mines left to flag, the elapsed time, and whether the round is in progress, won or lost.
- Needs to decide: which cell to reveal and which to flag, based on the numbers already shown.
- Path: arrives at a new round on the default difficulty → reads the board → reveals a first cell (the first click is always safe) → reveals and flags cells until every safe cell is revealed (won) or a mine is revealed (lost) → sees the result and may start a new round.

## 2. How it looks

A plain grey grid of square tiles on a grey frame with a counter bar above it, as in the classic Windows Minesweeper.

Layout, from back to front:

- Window background: flat mid-grey (#C0C0C0) filling the whole screen behind everything.
- Outer frame: raised light-grey panel with a white top-left bevel and dark-grey bottom-right bevel, enclosing the whole game.
- Header bar: sunken panel at the top of the frame, holding the mine counter at the left, the reset face button at the centre and the timer at the right.
- Mine counter: three-digit red-on-black LCD-style readout showing mines remaining (total mines minus flags placed), never below zero shown as negative; shows "000" when flags equal or exceed mines.
- Timer: three-digit red-on-black LCD-style readout showing whole seconds elapsed, starting at the first reveal, stopping at win or loss, capped at 999.
- Reset face button: raised square at the header centre showing a smiling yellow face when idle or playing; a face with open mouth and X eyes after a loss; sunglasses face after a win; a pressed (sunken) face while the pointer is held down on the board.
- Board: sunken grey panel directly below the header, holding the tile grid, with the tile size and grid dimensions set by difficulty.
- Hidden tile: raised light-grey square with white top-left and dark-grey bottom-right bevel; sinks to a flat grey tile while pressed.
- Revealed empty tile: flat light grey (#C0C0C0) square with a thin grey outline, no number.
- Revealed number tile: flat grey square showing its adjacent-mine count in a coloured digit: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 grey.
- Flagged tile: raised hidden tile with a red flag glyph on a black pole; if the flag was wrong at round end, shows a red cross on white.
- Mine tile (revealed at loss): flat grey square with a black mine glyph; the one tripped mine has a red background.
- Question-mark tile: not present in this product.
- Win banner: none; the win state is shown only by the sunglasses face, the timer stopping and all remaining hidden mines flagged automatically.

## 3. How it is used

- Left-click a hidden tile (mouse) / tap a hidden tile (touch): reveals it; first reveal starts the timer and guarantees no mine under it or its neighbours.
- Right-click a hidden tile (mouse) / long-press a hidden tile (touch): places a flag; press again to change it to a question mark when marks are on, then clear it. Tapping a flag does nothing.
- Right-click a flagged tile: removes the flag and returns it to hidden.
- Left-click a revealed number tile whose adjacent flags equal its number (mouse) / tap it (touch): reveals all its hidden neighbours that are not flagged; if a wrong flag was placed, a mine is revealed and the round is lost.
- Left-click (or press and hold) a revealed number tile (mouse) / press and hold it (touch): shows its hidden neighbours pressed down while held, without revealing.
- Click the reset face (mouse) / tap the reset face (touch): starts a new round at the current difficulty.
- Press the pointer on the board and move it, then release (mouse) / drag (touch): moves the pressed highlight across tiles, revealing on release on a hidden tile.
- Press the keyboard F2: starts a new round.
- Press the keyboard number keys 1, 2, 3: select Beginner, Intermediate, Expert difficulty and start a new round at it.
- Use the Game menu (mouse) / the menu button (touch) to choose Beginner, Intermediate, Expert or Custom; Custom opens a field asking width, height and mine count.

## 4. Scope

A player opens the game to a new round on Beginner (9×9, 10 mines). They reveal a first cell, which opens a safe area, then reveal and flag until all safe cells are revealed and the round is won, or they reveal a mine and the round is lost. They read the result from the face and timer, then start a new round, optionally choosing Intermediate (16×16, 40 mines), Expert (30×16, 99 mines) or Custom (width 8 to 30, height 8 to 24, mines from 10 up to 99 and less than the number of cells minus 9). Custom is the only form; it asks only for those three numbers.

## 5. Things and their states

- **Board:** holds the grid of cells, its width, height and mine count. States: not yet started (no reveal yet), in progress, won, lost. Moves from not started to in progress on first reveal; to won when every non-mine cell is revealed; to lost when a mine is revealed.
- **Cell:** holds its position, whether it has a mine, its adjacent-mine count, and its mark. States: hidden, revealed, flagged, question-marked (only when marks are on). Hidden → revealed by a reveal; hidden → flagged by a flag action; flagged → hidden by removing the flag; flagged → question-marked and question-marked → hidden by further presses when marks are on.
- **Mine layout:** holds the set of mine cells, placed once at the first reveal so that the clicked cell and its neighbours are mine-free. States: unplaced, placed. Moves from unplaced to placed on first reveal; does not change after.
- **Round (session):** holds the board, the start time, the elapsed time and the outcome. States: ready, playing, won, lost. Moves to playing on first reveal; to won or lost as the board does; stops the timer on either.

## 6. Rules

- A first reveal always opens a cell with zero adjacent mines; a first click on a mine is moved to another cell.
- Revealing a hidden cell with no adjacent mines automatically reveals all its neighbours, repeating across connected zero cells.
- Revealing a mine ends the round as lost; all mines are revealed and wrong flags are marked.
- The round is won when every non-mine cell is revealed; all mines are flagged automatically.
- Flags cannot be revealed by a normal reveal; a flagged cell is ignored by left-click.
- Right-click or long press on a revealed cell does nothing.
- Chording (clicking a revealed number) reveals neighbours only when its flag count equals its number; otherwise nothing changes.
- Chording with a wrong flag reveals the wrongly unflagged mine and loses the round.
- Flag count cannot exceed the mine count only for the display; further flags are still allowed but the mine counter shows 000 at zero.
- Actions on a won or lost round are ignored, except the reset face and F2 and difficulty keys, which start a new round.
- The timer stops at win or loss and does not resume on the same round.
- Question marks are placed only when marks are on; default is off.
- Custom sizes outside the stated limits are refused with a message and the form keeps its values.
- Ending the round by the player: the player may start a new round at any time, which abandons the current one with no result recorded.