# A minesweeper game

## 1. People and their journey
**Player** is the only role. They arrive at a fresh board, choose a difficulty if they wish, reveal a first cell, reason from numbers, flag suspected mines, and finish by clearing every safe cell (win) or revealing a mine (loss). They can then start a new game.

## 2. How it looks
The product looks like classic Windows Minesweeper: a grey beveled window, a LED-style counter bar, and a grid of square grey tiles.

- **Page background**: flat mid-grey (#c0c0c0) behind and around the game window, with the window centred.
- **Game window**: raised grey panel with a light top-left bevel and dark bottom-right bevel, holding the top bar and the board.
- **Difficulty selector**: a row above the top bar with three choices: Beginner, Intermediate, Expert. The current choice is underlined; hover gives a light-blue highlight.
- **Top bar**: sunken grey strip across the window top with the mine counter left, face button centre, timer right.
- **Mine counter**: black rectangle, three red seven-segment digits, showing mines minus flags placed. Goes negative (e.g. -01) when flags exceed mines.
- **Face button**: raised grey square with a yellow smiley. While a cell is held pressed it shows a surprised "o" face. Won: sunglasses face. Lost: dead "x-eyes" face. Pressed: bevel inverts.
- **Timer**: black rectangle, three red seven-segment digits, seconds elapsed, capped at 999. Stopped on win or loss.
- **Board**: sunken grid of square cells under the top bar. Beginner 9×9 with 10 mines; Intermediate 16×16 with 40; Expert 30×16 with 99.
- **Hidden cell**: raised grey square with bevel. While pressed, it shows flat sunken grey.
- **Flagged cell**: hidden-cell look with a red flag on a black base.
- **Revealed empty cell**: flat light grey with thin darker grid lines, blank.
- **Number cells**: revealed cell with a bold digit: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 grey.
- **Mine cell on loss**: revealed flat grey with a black spiked mine; the cell that was hit has a red background.
- **Wrong flag on loss**: a mine drawn with a red cross over it, on a flag placed on a safe cell.
- **Unflagged mines on win**: they are automatically shown as flags, and the counter reads 000.

## 3. How it is used
- Click a difficulty choice: starts a new game at that size.
- Left-click a hidden cell: reveals it. The first click starts the timer.
- Press and hold on a cell: the cell looks pressed and the face turns surprised; releasing reveals it.
- Right-click a hidden cell (touch: long press): cycles it between hidden and flagged.
- Click a revealed number cell: if its adjacent flag count equals its number, all other hidden neighbours are revealed (chording).
- Click the face button: starts a new game at the current difficulty.
- Press F2: starts a new game at the current difficulty.

## 4. Scope
Choose a difficulty, play one round of reveal and flag moves until win or loss, then restart. There is no saving, no accounts, no scores board, and no custom board size.

## 5. Things and their states
- **Game**: difficulty, mine layout, timer, flags remaining. States: ready (no reveal yet), in progress, won, lost. The first reveal moves it to in progress; revealing a mine moves it to lost; revealing every safe cell moves it to won. A new game returns it to ready.
- **Cell**: mine or not, adjacent mine count (0–8), state hidden, flagged or revealed. Hidden toggles with flagged; hidden becomes revealed.

## 6. Rules
- Mines are placed randomly at the first reveal, never on the first clicked cell.
- The first clicked cell is never a mine, so a first click can never lose.
- Each cell's number is the count of mines in its up to 8 neighbours.
- Revealing a mine ends the game as lost.
- Revealing a cell with count 0 automatically reveals all its neighbours, repeating outward.
- Cascade reveal skips flagged cells and never reveals mines.
- Flagged cells cannot be revealed by left-click; the click is ignored.
- Flags can be placed only on hidden cells; right-click on a revealed cell is ignored.
- Flags are unlimited, even beyond the mine count; the counter goes negative.
- Chording only acts if the flag count equals the number; otherwise nothing happens.
- Chording with a wrong flag reveals a mine and loses the game.
- Chording on a revealed cell with 0 or on a hidden cell does nothing.
- Win happens when all non-mine cells are revealed, whether or not mines are flagged.
- On win, the timer stops and remaining mines are flagged.
- On loss, the timer stops, all unflagged mines are shown, and wrong flags are marked.
- After win or loss, reveal and flag clicks are ignored until a new game starts.
- The timer starts at the first reveal, counts whole seconds, and stops at 999.
- Right-click does not start the timer; flags can be placed before the first reveal.
- The player may end a round by starting a new game at any time; the current round is discarded.
- Changing difficulty during play abandons the round without a prompt.