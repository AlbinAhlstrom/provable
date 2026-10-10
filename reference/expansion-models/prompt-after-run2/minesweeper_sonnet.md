# A minesweeper game

## 1. People and their journey
**Player** (the only role). Arrives at the page, sees a ready board, chooses a difficulty if desired, clicks to reveal cells, flags suspected mines, and finishes by clearing every safe cell (win) or revealing a mine (loss). Then starts a new round with the face button or by choosing a difficulty.

## 2. How it looks
The product looks like classic Windows Minesweeper: a grey, bevelled, retro desktop-style window with a counter header and a square grid of raised tiles.

- **Page background:** flat mid-grey (#c0c0c0), the game panel centred on it.
- **Difficulty bar:** top of panel, flat grey text buttons "Beginner", "Intermediate", "Expert"; the current one is underlined.
- **Game panel:** raised grey frame with a 3px white top-left and dark grey (#808080) bottom-right bevel, holding header and board.
- **Header strip:** top of panel, sunken grey bar holding mine counter, face button and timer in one row.
- **Mine counter:** left of header, sunken black box with red (#ff0000) three-digit seven-segment numerals; shows mines minus flags, and goes negative when over-flagged.
- **Face button:** centre of header, raised grey square with a yellow smiley. Pressed: sunken. While a cell is held down: surprised "O" face. Won: sunglasses face. Lost: dead "X-eyes" face.
- **Timer:** right of header, same style as the counter; shows whole seconds from the first reveal, capped at 999.
- **Board:** below header, sunken-framed square grid of equal square cells. Beginner 9×9 with 10 mines; Intermediate 16×16 with 40; Expert 30×16 with 99.
- **Hidden cell:** raised grey tile with white top-left and dark grey bottom-right bevel. While pressed: flat and sunken.
- **Revealed cell:** flat light grey with a thin darker grey outline; empty if zero neighbouring mines, otherwise a bold number.
- **Number colours:** 1 blue (#0000ff), 2 green (#008000), 3 red (#ff0000), 4 dark blue (#000080), 5 maroon (#800000), 6 teal (#008080), 7 black, 8 grey (#808080).
- **Flagged cell:** raised tile with a red flag on a black base.
- **Mine (on loss):** unrevealed mines show a black spiky mine on the tile.
- **Exploded cell:** the mine that was clicked has a red (#ff0000) background.
- **Wrong flag (on loss):** a flagged cell with no mine shows a mine with a red diagonal cross.
- **Win display:** on a win, all unflagged mines are automatically flagged and the counter shows 000.

## 3. How it is used
- Left-click a hidden cell: reveals it; the first click starts the timer.
- Left-click a revealed number whose adjacent flag count equals the number (chord): reveals all its other hidden neighbours.
- Right-click a hidden cell, or long-press on touch: cycles it between hidden and flagged.
- Hold both mouse buttons on a number: chord, as above.
- Click the face button: starts a new board at the current difficulty.
- Click a difficulty name: starts a new board of that size.
- Press and hold on a cell: shows the pressed look and the surprised face; releasing off the cell cancels.
- Tap on touch: reveals; tapping a revealed number chords.

## 4. Scope
One loop: pick difficulty, play a board by revealing and flagging, reach win or loss, restart. Three fixed sizes; no custom size, saved scores or accounts.

## 5. Things and their states
- **Cell:** holds mine yes/no and adjacent-mine count. States: hidden → flagged (toggle) → hidden; hidden → revealed.
- **Round:** holds board, flags placed, elapsed seconds. States: ready (no reveal yet) → in progress (first reveal) → won or lost. A new round resets it.

## 6. Rules
- Mines are placed on the first reveal, never on the clicked cell or its neighbours, so the first click is always a zero.
- Adjacency count is the number of mines among the up to eight surrounding cells.
- Revealing a zero cell automatically reveals all its neighbours, repeating through connected zeros.
- Revealing a mine loses the round.
- Revealing a number shows just that cell.
- Revealing all non-mine cells wins the round.
- Flagged cells cannot be revealed by click or by flood; the click is ignored.
- Revealed cells cannot be flagged; right-click is ignored.
- Flags do not need to be correct to win; only the reveals decide it.
- The counter equals mines minus flags and may go below zero.
- Chording with a mismatched flag count does nothing.
- Chording with a wrong flag reveals a mine and loses.
- Chording skips flagged neighbours.
- The timer starts at the first reveal and stops on win or loss.
- After a win or loss, cells ignore clicks until a new round begins.
- Changing difficulty or pressing the face mid-round abandons it with no outcome.
- Right-click opens no browser context menu on the board.