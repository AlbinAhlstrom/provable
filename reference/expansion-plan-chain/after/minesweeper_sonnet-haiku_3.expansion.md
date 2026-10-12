# A minesweeper game

## 1. People and their journey
**Player** is the only role. They arrive at the board, see a fresh grid of hidden cells, a mine counter and a timer. They reveal and flag cells to clear every safe cell without hitting a mine, then see the win or loss and start a new game from the face button.

## 2. How it looks
The product looks like classic Windows Minesweeper: a grey titled desktop window on a teal desktop, with a menu bar, a sunken header panel and a sunken grid.

- **Desktop backdrop**: fills the browser page, flat teal (#008080); the window sits centred on it.
- **Window frame**: raised light grey (#C0C0C0) with a white top-left bevel and dark grey bottom-right bevel.
- **Title bar**: top of the window, dark blue (#000080) with white bold text "Minesweeper".
- **Menu bar**: under the title bar, light grey flat, with one entry "Game" in black. Highlights dark blue with white text while open.
- **Game menu**: drops below "Game", raised grey list: New, Beginner, Intermediate, Expert, Custom…, Marks (?), Best Times…, with a tick beside the current level and Marks when on.
- **Header panel**: top of the game area, sunken grey, holding counter, face and timer in a row.
- **Mine counter**: left of the header, sunken black box with three bright red (#FF0000) seven-segment digits showing mines minus flags; negative shows a minus sign.
- **Face button**: header centre, raised yellow smiley on grey square. Pressed: sunken. Cell held down: surprised "o" face. Won: sunglasses face. Lost: dead face with X eyes.
- **Timer**: right of the header, sunken black box with three red seven-segment digits counting seconds, capped at 999.
- **Grid**: below the header, sunken grey border containing square cells in rows and columns.
- **Hidden cell**: raised light grey square with white top-left and dark grey bottom-right bevel. While held down it looks sunken like a revealed empty cell.
- **Revealed empty cell**: flat pale grey (#C0C0C0) with thin darker grey outline, blank.
- **Number cell**: revealed look, bold number coloured 1 blue (#0000FF), 2 green (#008000), 3 red (#FF0000), 4 dark blue (#000080), 5 maroon (#800000), 6 teal (#008080), 7 black, 8 grey (#808080).
- **Flagged cell**: hidden-cell look with a red flag on a black base.
- **Question-marked cell**: hidden-cell look with a black "?" (only when Marks is on).
- **Mine cell**: on loss, unflagged mines show a black mine on the revealed look.
- **Exploded mine**: the mine the player hit, shown on a red (#FF0000) background.
- **Wrong flag**: on loss, a flag on a non-mine shows a mine with a red diagonal cross.
- **Won grid**: all remaining mines show flags.
- **Custom dialog**: small raised grey window titled "Custom Field" with Height, Width and Mines number fields and OK and Cancel buttons.
- **Best Times dialog**: small grey window listing fastest times for Beginner, Intermediate and Expert, with a Reset Scores and OK button.

## 3. How it is used
- Left-click a hidden cell: reveals it.
- Right-click a hidden cell, or long-press on touch: cycles hidden, flag, then question mark if Marks is on, else back to hidden.
- Click a revealed number cell: if the adjacent flags equal its number, reveals all other adjacent hidden unflagged cells (chord).
- Press both mouse buttons on a number, or middle-click: same chord.
- Press and hold on a cell: cell appears sunken and face turns surprised; releasing off the cell cancels.
- Click the face: starts a new game at the current level.
- Press F2: new game.
- Game menu, pick Beginner, Intermediate or Expert: starts a new game at that size.
- Game menu, Custom…: opens the dialog; OK validates and starts a new game.
- Game menu, Marks (?): toggles question marks.
- Game menu, Best Times…: shows the fastest times.
- Game menu, New: starts a new game.

## 4. Scope
One loop: pick a level, reveal and flag cells, win or lose, restart. Levels are Beginner, Intermediate, Expert and Custom. Single player, no accounts or online features. Best times are kept only on this device.

## 5. Things and their states
- **Cell**: holds mine or not, adjacent mine count. States: hidden, flagged, question-marked, revealed.
- **Board**: width, height, mine count, cells.
- **Game**: states ready (no mines placed yet), in progress, won, lost. Holds timer and flag count. First reveal moves ready to in progress; revealing a mine moves to lost; all safe cells revealed moves to won.

## 6. Rules
- Beginner is 9×9 with 10 mines.
- Intermediate is 16×16 with 40 mines.
- Expert is 30 columns × 16 rows with 99 mines.
- Custom height is 9 to 24, width 9 to 30, and mines 10 to (height−1)×(width−1); out-of-range values are clamped to the limit.
- Mines are placed on the first reveal, never on the clicked cell, so the first click is never a mine.
- The first click is also never adjacent to a mine in the standard layout only when space allows; otherwise only the clicked cell is safe.
- The timer starts on the first reveal and counts each second to 999.
- Each number shows the count of mines among the 8 neighbours.
- Revealing a zero cell automatically reveals all its neighbours, repeating through further zeros.
- Flood reveal skips flagged cells.
- Revealing a mine loses the game and stops the timer.
- Revealing every non-mine cell wins, stops the timer and flags all mines.
- A flagged or question-marked cell cannot be revealed by left-click; it is ignored.
- Revealed cells cannot be flagged; right-click is ignored.
- Flagging lowers the counter by one; removing raises it. Flags may exceed the mine count, so the counter may go negative.
- Chording with a mismatched flag count does nothing; if flags are wrong, chording can reveal a mine and lose.
- After win or loss, cells ignore clicks until a new game starts.
- Flags before the first reveal are allowed and do not start the timer.
- A winning time that beats the stored best for Beginner, Intermediate or Expert is saved on the device; Custom times are not saved.
- A new game resets timer to 000, counter to the mine count and face to smiling.
- The game can end only by a win, a loss, or the player starting a new game.