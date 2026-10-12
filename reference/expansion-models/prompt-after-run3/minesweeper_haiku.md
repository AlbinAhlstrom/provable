# Minesweeper

## 1. People and their journey

- **Player (single role):** someone who wants to play a classic round of minesweeper for fun.
  - Needs to see: the whole board, which cells are hidden, revealed or flagged, the mine counter, and the elapsed time.
  - Decides: which cell to reveal and which to flag, based on the numbers already shown.
  - Path: opens the game, sees a new board, makes a first reveal, works through the board, and ends with a win or a loss. Can then start a new round.

## 2. How it looks

A classic grey Windows-style minesweeper window: a raised grey frame around a top status bar and a square-cell grid, with no other decoration.

- **Window frame:** light grey (#C0C0C0) raised bevel, title bar with the text "Minesweeper" in white on dark navy (#000080).
- **Status bar:** sits directly under the title bar, light grey, sunken bevel, holds the mine counter at the left, the restart button at the centre and the timer at the right.
- **Mine counter:** sunken black box with red digits showing mines remaining (total mines minus flags placed); it goes negative when there are more flags than mines.
- **Timer:** sunken black box with red digits showing elapsed seconds, from 0 to 999, starting at the first reveal and stopping on win or loss.
- **Restart button:** light grey raised square at the centre of the status bar showing a smiling face; when pressed it sinks; shows a surprised face while a cell is held down; shows dark sunglasses on a win; shows a cross-eyed face on a loss.
- **Board area:** sunken grey panel beneath the status bar holding the grid, with a small margin around the grid.
- **Hidden cell:** light grey square, raised bevel, no number, no mark.
- **Pressed cell:** light grey square with a sunken bevel, shown while the mouse button or finger is held on a hidden cell.
- **Revealed empty cell:** flat light grey square with a thin darker grey outline, no number.
- **Revealed number cell:** flat light grey square with a thin darker grey outline, bold number in the colour of its count: 1 blue (#0000FF), 2 green (#008000), 3 red (#FF0000), 4 dark navy (#000080), 5 maroon (#800000), 6 teal (#008080), 7 black, 8 grey (#808080).
- **Flagged cell:** raised hidden-style square with a red flag icon centred on it.
- **Mine cell (after loss):** flat light grey square with a black mine icon centred on it.
- **Exploded mine cell:** the single mine the player revealed, with a red background behind the black mine icon.
- **Wrongly flagged cell (after loss):** a mine icon with a red cross across it, shown where a flag was placed on a cell with no mine.
- **Unrevealed mine (after loss):** shown as a black mine icon on a light grey square.

## 3. How it is used

- **Left-click (tap) a hidden cell:** reveals it; the first reveal of a round is never a mine.
- **Left-click (tap) a revealed empty cell that opens an area:** the area opens automatically (see Rules).
- **Right-click (long press) a hidden cell:** places a flag; the mine counter drops by one.
- **Right-click (long press) a flagged cell:** removes the flag and returns the cell to hidden.
- **Left-click (tap) a flagged cell:** nothing happens; the flag is kept.
- **Left-click (tap) a revealed number cell with exactly as many adjacent flags as its number:** reveals all its hidden neighbours at once (double-click with a mouse, or tap the number with two fingers on touch screens).
- **Left-click (tap) the smiling-face restart button:** starts a new round with the same board size and mine count.
- **Left-click (tap) the restart button on a finished round:** starts a new round.
- **Hold left button or finger on a hidden cell:** shows the pressed state; releasing reveals it.
- **Keyboard arrow keys:** move a highlighted cell focus across the board.
- **Enter or Space on the focused cell:** reveals it.
- **F key on the focused cell:** toggles a flag.
- **F2 key:** starts a new round.

## 4. Scope

A player opens the game on a new board of the default beginner size (9 by 9 with 10 mines). They reveal a first cell, which is always safe and may open a region. They reveal and flag cells using the numbers as clues until every safe cell is revealed (win) or a mine is revealed (loss). They may restart at any time. The player may pick one of three sizes before a round: beginner (9 by 9, 10 mines), intermediate (16 by 16, 40 mines), or expert (16 by 30, 99 mines). The player may not pick a board size during a round.

## 5. Things and their states

- **Board:** holds a grid of cells and a fixed mine count; it is created when a round starts and is laid out by the first reveal. Moves through: not laid out, laid out (mines placed).
- **Cell:** holds its mine status (mine or not), its adjacent-mine count (0 to 8), and its marking. Moves through: hidden, flagged, revealed. A flagged cell can return to hidden; a revealed cell does not change.
- **Game session:** holds the board, elapsed time, mines remaining and outcome. Moves through: ready (no reveal yet), in progress (after the first reveal), won, lost. Ready moves to in progress on first reveal; in progress moves to won when the last safe cell is revealed or to lost when a mine is revealed. Won and lost are final until a restart returns the session to ready.

## 6. Rules

- The mines are placed randomly after the first reveal, never on that cell or its eight neighbours.
- Each revealed cell shows the number of mines among its eight neighbours; a cell with zero adjacent mines shows no number.
- Revealing a cell with zero adjacent mines automatically reveals all its neighbours, repeating for each newly revealed zero cell, until the edge of the area is reached.
- Revealing a mine ends the round as lost.
- The round is won when every non-mine cell is revealed; flags do not need to be correct for a win.
- On a win, every remaining hidden mine is shown flagged and the mine counter shows zero.
- On a loss, every hidden mine is shown as a mine icon, every wrong flag is shown as a crossed mine, and the exploded mine is highlighted in red.
- Flags can be placed on any hidden cell, including cells that are not mines, and removed at any time during the round.
- Flags cannot be placed on revealed cells.
- Revealed cells cannot be hidden again or flagged.
- Chording (revealing the hidden neighbours of a number cell) works only when the number of adjacent flags equals the number; if the count does not match, the action is ignored and nothing changes.
- Chording that reveals a mine ends the round as lost.
- Clicks on a flagged cell do not reveal it; the flag must be removed first.
- Clicks on a finished round's board are ignored, except the restart button.
- The timer starts at the first reveal, not at the first flag, and stops at win or loss.
- The timer stops at 999 seconds and does not advance further.
- The mine counter may show negative values when flags exceed mines.
- A restart discards the current board and timer and returns the session to ready with a new random layout.
- Any action that is not permitted (for example revealing a flagged or revealed cell) is refused and nothing on the board changes.