# A minesweeper game

## 1. People and their journey
**Player** (the only role). Arrives at a fresh board, sees the mine counter, timer and grid, and decides which cell to reveal or flag. Plays until every safe cell is revealed (win) or a mine is revealed (loss), then chooses to start a new game or change difficulty.

## 2. How it looks
The product looks like classic Windows Minesweeper: a grey beveled window with a raised panel holding a counter, a face button and a timer above a sunken grid of square tiles.

- **Page background**: flat mid-grey (#c0c0c0) filling the view, with the game window centred on it.
- **Game window**: raised grey frame with a light-white top-left bevel and dark-grey bottom-right bevel, holding the difficulty bar, header panel and board.
- **Difficulty bar**: a row at the top of the window with three choices: Beginner, Intermediate, Expert. The current one is shown with a sunken button.
- **Header panel**: sunken-bordered grey strip across the top of the window, holding the mine counter, face button and timer.
- **Mine counter**: left of the header; black rectangle with three red seven-segment digits showing mines minus flags. It goes negative (for example -02) when flags exceed mines.
- **Face button**: centre of the header; raised square, yellow round face. Smiling normally; shocked "o" mouth while a tile is held down; sunglasses after a win; dead "x" eyes after a loss. Sunken while pressed.
- **Timer**: right of the header; black rectangle with three red seven-segment digits counting seconds, capped at 999. Stops on win or loss.
- **Board**: sunken-bordered grid of square tiles below the header, with no gaps between tiles.
- **Hidden tile**: raised grey square with white top-left and dark-grey bottom-right bevels. Looks flat-sunken while held down by the pointer.
- **Revealed tile**: flat light-grey square with a thin darker-grey outline, showing a number or nothing.
- **Number colours**: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 grey. A zero shows blank.
- **Flagged tile**: hidden-style raised tile with a red flag on a black base.
- **Mine (on loss)**: revealed tile with a black spiky mine. Unflagged mines are shown on loss.
- **Exploded mine**: the mine tile the player clicked, with a red background.
- **Wrong flag (on loss)**: a flagged tile that was not a mine shows the mine with a red cross over it.
- **Win display**: when the game is won, all unflagged mines automatically get flags and the counter shows 000.

## 3. How it is used
- **Click a hidden tile** (tap on touch): reveals it. The first reveal starts the timer.
- **Click a number tile** whose adjacent flag count equals its number (chord): reveals all its other unflagged hidden neighbours.
- **Right-click a hidden tile** (long press on touch): places a flag; on a flagged tile it removes the flag.
- **Press and hold on a tile**: the face turns shocked until release.
- **Click the face button**: starts a new game with the same difficulty.
- **Click a difficulty choice**: starts a new game at that size.
- **Click a flagged tile**: nothing happens.
- **Click any tile after the game ends**: nothing happens.

## 4. Scope
One loop: choose a difficulty, reveal and flag tiles, finish with a win or loss, then restart. Beginner is 9×9 with 10 mines, Intermediate is 16×16 with 40, and Expert is 30×16 with 99. There is no custom size, no saved games and no sound.

## 5. Things and their states
- **Game**: holds difficulty, board, elapsed seconds and flag count. States: ready (no reveal yet), in progress, won, lost. The first reveal moves it from ready to in progress; revealing a mine moves it to lost; revealing every safe tile moves it to won. The face button or a difficulty choice starts a new game in the ready state.
- **Tile**: holds a mine flag and an adjacent-mine count (0–8). States: hidden, flagged, revealed. Reveal moves hidden to revealed, and the flag action toggles hidden and flagged.

## 6. Rules
- Mines are placed at the first reveal, never on the clicked tile, so the first click is never a mine.
- The first click's neighbours are also kept mine-free, so the first reveal opens an area.
- A tile's count is the number of mines among its up to 8 neighbours.
- Revealing a mine ends the game as lost.
- Revealing a zero tile automatically reveals all its neighbours, repeating through further zeros.
- Cascades never reveal flagged tiles, and the cascade stops at numbered tiles.
- Revealing a flagged tile is refused and nothing changes.
- Flags can only be placed on hidden tiles; flagging a revealed tile is ignored.
- Flags may exceed the mine count; the counter goes negative.
- A chord on a number whose adjacent flags do not match is ignored.
- A chord reveals neighbours, so a wrong flag can cause a loss on a mine.
- A chord on a hidden or revealed zero tile does nothing.
- The game is won when all non-mine tiles are revealed; flags are not required.
- The timer starts on the first reveal, ticks once a second and stops on win or loss.
- Flagging before the first reveal is allowed and does not start the timer.
- After a win or loss, reveals, flags and chords are ignored until a new game.
- The player can end a game early only by starting a new one; there is no resign or draw.
- The board is not resized or changed mid-game.