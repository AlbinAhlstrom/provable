# A minesweeper game

## 1. People and their journey
**Player** (the only role): someone who wants to play minesweeper for fun.
Journey: opens the game and sees a fresh hidden board. They reveal a cell, read the numbers, flag suspected mines, and keep going until every safe cell is revealed (win) or a mine is revealed (loss). They then start a new game.

## 2. How it looks
The product looks like classic Windows-style Minesweeper: a grey, beveled window with a counter and smiley panel above a square grid of raised grey tiles.

- **Page background**: flat, plain mid-grey (#c0c0c0), filling the window; the game panel is centred on it.
- **Game panel**: centred, raised grey with a bevel (white top-left edge, dark grey bottom-right edge), containing the header and the board.
- **Header bar**: across the top of the panel, sunken grey strip holding the mine counter, the face button and the timer.
- **Mine counter**: left of the header, black sunken box with three red seven-segment digits showing mines minus flags. Goes negative (e.g. -2) when flags exceed mines.
- **Face button**: centre of the header, raised grey square with a yellow round face. Smiling by default; "oh" mouth while a cell is held pressed; sunglasses after a win; dead X-eyes after a loss. Looks sunken while pressed.
- **Timer**: right of the header, black sunken box with three red digits counting elapsed seconds, 000 before the first reveal, stops on win or loss, caps at 999.
- **Board**: below the header, sunken grey frame holding a square grid of cells (default 9×9, 10 mines).
- **Hidden cell**: raised grey tile with a white top-left and dark-grey bottom-right bevel. When held pressed it looks flat and sunken.
- **Flagged cell**: a hidden raised tile with a red flag on a black base. It cannot be pressed to reveal.
- **Revealed empty cell**: flat light-grey tile with a thin darker-grey outline, no number.
- **Revealed number cell**: flat tile with a bold number, coloured by count: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 grey.
- **Mine at loss**: unflagged mines show as a black spiked ball on a flat tile.
- **Exploded mine**: the mine the player revealed, shown on a red background.
- **Wrong flag**: after a loss, a flag on a non-mine shows a black ball crossed with a red X.
- **Win display**: all remaining mines are automatically flagged, the counter reads 000, and the face wears sunglasses.

## 3. How it is used
- **Left-click a hidden cell**: reveals it. The first reveal starts the timer.
- **Left-click an empty (zero) cell**: reveals it and cascades to all connected empty cells and their bordering numbers.
- **Right-click a hidden cell**: cycles it between hidden and flagged. On touch, long-press does the same.
- **Click or tap a revealed number cell**: if the adjacent flag count equals its number, reveals all other unflagged neighbours (chording). Middle-click or both buttons also work on a mouse.
- **Hold the mouse button on a cell**: the cell looks pressed and the face shows "oh". Releasing outside the cell cancels it.
- **Click or tap the face button**: starts a new game at any time.
- **Click on a flagged or revealed non-number cell**: nothing happens (left-click).
- **Any click on the board after win or loss**: ignored.

## 4. Scope
One loop: start a game, reveal and flag until win or loss, restart. Left out: accounts, leaderboards, multiplayer, payments, admin, custom board sizes, difficulty menus, saved games, question-mark marks.

## 5. Things and their states
- **Cell**: holds mine or not, adjacent mine count (0–8), and state: hidden → flagged (and back) → revealed. Revealed is final.
- **Board**: a 9×9 grid of cells with 10 mines. Mines are not placed until the first reveal.
- **Game**: waiting (no reveal yet) → in progress (first reveal) → won or lost. The face button returns any state to waiting with a new board.

## 6. Rules
- Board is 9×9 with exactly 10 mines.
- Mines are placed at random on the first reveal, never on the clicked cell, and never on its neighbours, so the first reveal is always a zero.
- Each cell's number is the count of mines among its up to 8 neighbours (edges and corners have fewer).
- Revealing a mine ends the game as a loss.
- Revealing a zero cell automatically reveals all its neighbours, repeating through further zeros.
- Cascades never reveal a flagged cell and never reveal a mine.
- A flagged cell is protected: left-click on it is refused and nothing changes.
- A revealed cell cannot be flagged; the right-click is ignored.
- Flags may exceed the mine count; the counter shows the negative number.
- Flagging before the first reveal is allowed and does not start the timer.
- Chording only works when the flag count around the number equals the number; otherwise it is ignored.
- Chording on a wrongly flagged neighbour reveals a mine and loses the game.
- Chording reveals cascades from any zero cells it opens.
- Win: every non-mine cell is revealed. Flags are not required.
- On a win, the timer stops and the unflagged mines are flagged.
- On a loss, the timer stops, all unflagged mines are shown, wrong flags are marked, and the clicked mine is red.
- After a win or loss, reveal, flag and chord actions are ignored; only the face button works.
- The player ends a game early only by restarting; the current round is then discarded with no result.
- The timer counts whole seconds from the first reveal and shows at most 999.