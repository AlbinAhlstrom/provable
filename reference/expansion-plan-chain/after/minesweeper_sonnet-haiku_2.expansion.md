# A minesweeper game

## 1. People and their journey
**Player** (the only role): someone who wants to play minesweeper for fun. They arrive at a board already set up, choose a difficulty if they wish, reveal and flag cells, and finish when every safe cell is revealed (won) or a mine is revealed (lost). They can then start a new game.

## 2. How it looks
The product looks like the classic Windows Minesweeper: a grey titled desktop-style window on a teal desktop, with a menu bar, a sunken status panel and a sunken grid of raised square tiles.

- **Page background**: flat teal (#008080) filling the browser; the window sits at the top centre.
- **Window**: raised light-grey (#C0C0C0) frame with a 3D bevel, containing the title bar, menu bar and game area.
- **Title bar**: top of window, flat dark blue (#000080), white bold text "Minesweeper". Greyed out to #808080 when the window is not focused.
- **Menu bar**: below the title bar, light grey, with one item, "Game". The open menu is a raised grey list; hovered entries are dark blue with white text.
- **Game menu**: New (F2), then Beginner, Intermediate, Expert, Custom… (one checked with a tick), then Marks (?) with a tick when on, then Best Times… (local only), then Exit omitted.
- **Game area**: grey raised panel under the menu bar holding the status panel and the board, with a 3D bevel.
- **Status panel**: sunken strip above the board, holding mine counter, face button and timer.
- **Mine counter**: left of the status panel, black box with bright red (#FF0000) seven-segment digits, 3 digits, showing mines minus flags. Goes negative with a minus sign if over-flagged.
- **Face button**: centre of the status panel, raised grey square with a yellow smiley. While a tile is held down: open-mouthed "oh" face. Won: sunglasses face. Lost: dead face with X eyes. Pressed: sunken.
- **Timer**: right of the status panel, same style as the counter, showing whole seconds from 000 up to a maximum of 999.
- **Board**: sunken grid below the status panel, of square tiles in rows and columns.
- **Hidden tile**: raised light grey with a bevel.
- **Pressed tile**: while the mouse or finger is held on it, flat with a thin darker-grey border like a revealed tile.
- **Revealed tile**: flat light grey with a thin darker-grey (#808080) top and left border; empty if it has no adjacent mines.
- **Number tile**: revealed tile showing a bold number coloured: 1 blue (#0000FF), 2 green (#008000), 3 red (#FF0000), 4 dark blue (#000080), 5 maroon (#800000), 6 teal (#008080), 7 black, 8 grey (#808080).
- **Flagged tile**: hidden-style raised tile with a red flag on a black base.
- **Question-marked tile**: raised tile with a black "?" (only when Marks is on).
- **Mine tile**: after a loss, unflagged mines show a black mine on a revealed tile.
- **Exploded mine**: the mine the player revealed, shown on a bright red (#FF0000) background.
- **Wrongly flagged tile**: after a loss, a flagged tile with no mine shows a mine crossed with a red X.
- **Won board**: remaining unflagged mines are automatically flagged, and the counter shows 000.
- **Custom dialog**: small grey raised window with fields Height, Width, Mines, and OK and Cancel buttons.
- **Best Times dialog**: small grey raised window listing the fastest time and name for each of the three levels, with a Reset Scores button and OK.
- **New record dialog**: small grey window asking for a name (default "Anonymous") and an OK button.

## 3. How it is used
- Click a hidden tile: reveals it.
- Right-click a hidden tile, or long press on touch: cycles hidden → flag → (question mark if Marks is on) → hidden.
- Click a number tile with the right count of adjacent flags (mouse: left and right buttons together, or middle-click; touch: tap): reveals all its other unflagged neighbours.
- Hold the mouse button down on a tile: it appears pressed, and the face turns "oh". Releasing off the tile cancels.
- Click the face button, or press F2: starts a new game at the current settings.
- Open the Game menu by click; pick a difficulty to start a new game at that size.
- Choose Custom…: enter height, width and mines, then OK to start, or Cancel to dismiss.
- Toggle Marks (?) in the menu: turns question marks on or off.
- Choose Best Times…: shows the records; Reset Scores clears them.
- Press Escape: closes an open menu or dialog.

## 4. Scope
One loop: pick a difficulty (Beginner, Intermediate, Expert, Custom), play a round to a win or a loss, then start again. Best times are kept on the device only. No accounts, leaderboards, multiplayer, payments or admin.

## 5. Things and their states
- **Game**: holds the settings, the mine layout, the flag count and the elapsed time. States: ready (nothing revealed, timer stopped), in progress, won, lost. The first reveal moves ready → in progress. Revealing a mine → lost. Revealing every safe cell → won. New game → ready.
- **Cell**: holds mine or not, the adjacent mine count (0–8) and a state. States: hidden, flagged, question-marked, revealed.
- **Best time record**: a name and a time per level.

## 6. Rules
- Beginner is 9×9 with 10 mines; Intermediate is 16×16 with 40; Expert is 30×16 (30 columns, 16 rows) with 99.
- Custom height is 9 to 24, width 9 to 30, mines 10 to (height−1)×(width−1); out-of-range values are clamped to the nearest allowed value.
- The default level at first load is Beginner. The last chosen level persists on the device.
- Mines are placed on the first reveal, never on the first-clicked cell. Before that, the board has no mines.
- The timer starts on the first reveal and counts every second. It stops on a win or a loss, and at 999.
- A cell's number is the count of mines in its up to eight neighbours.
- Revealing a cell with zero adjacent mines automatically reveals all its neighbours, repeating through further zero cells.
- Revealing a mine ends the game as lost; all mines are shown.
- Revealing a flagged or question-marked cell is refused; nothing changes.
- Revealing an already revealed number cell does nothing, except as in the next rule.
- Chording: if the flags around a revealed number equal its number, all other hidden unflagged neighbours are revealed. A wrong flag means a mine is revealed and the game is lost. If the flag count differs, nothing happens.
- Flagging a revealed cell is ignored.
- The flag count may exceed the mine count; the counter goes negative.
- The counter shows mines minus flags; question marks do not count.
- The game is won when all non-mine cells are revealed; flags are not required.
- After a win or a loss, tiles ignore clicks, and only a new game restarts play.
- Changing the difficulty or pressing the face starts a new game and resets the timer and the counter.
- A winning time at a standard level (not Custom) that beats a stored record prompts for a name and is saved as the new record.
- Marks off: right-click cycles only hidden ↔ flag, and existing question marks revert to hidden.