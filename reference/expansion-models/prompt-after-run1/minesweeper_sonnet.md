# A minesweeper game

## 1. People and their journey
**Player** (the only role): someone who wants to play minesweeper for fun.
- Arrives at a board ready to play, picks a difficulty if desired, and sees the mine counter, timer and face button.
- Decides which cells to reveal and which to flag.
- Plays until the round is won or lost, then restarts with the face button or by choosing a difficulty.

## 2. How it looks
The game looks like classic Windows Minesweeper: a grey, beveled window with a header panel above a square-celled grid.

- **Page background**: flat mid-grey (#c0c0c0), the window centred on it, with a raised 3D bevel (white top and left, dark grey bottom and right).
- **Difficulty bar**: a row above the header with three choices: Beginner, Intermediate, Expert. The current choice is marked with a tick.
- **Header panel**: sunken grey strip above the grid, holding the mine counter, face button and timer.
- **Mine counter**: left of the header; a black box with three red seven-segment digits showing mines minus flags. It goes negative when flags exceed mines.
- **Face button**: centred in the header; a raised grey square with a yellow face. It looks smiling at rest, shocked (open mouth) while a cell is held down, wearing sunglasses after a win, and dead (X eyes) after a loss. Pressed, it looks sunken.
- **Timer**: right of the header; a black box with three red digits counting seconds. It starts at the first reveal, stops on win or loss, and caps at 999.
- **Grid**: sunken bevelled area below the header, a rectangle of square cells.
- **Hidden cell**: raised grey square with a white top-left edge and dark bottom-right edge. While held down it looks flat like a revealed empty cell.
- **Revealed empty cell**: flat light grey with a thin darker grey outline, blank.
- **Revealed number cell**: same flat look, showing a digit in colour: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 grey.
- **Flagged cell**: looks like a hidden cell with a red flag on a black base.
- **Mine, after loss**: a black spiky mine on a flat grey cell. Mines not flagged are shown this way.
- **Triggered mine**: the mine cell that was revealed shows its mine on a red background.
- **Wrongly flagged cell, after loss**: a mine with a red cross over it, on a flat grey cell.
- **Win display**: on a win, all remaining mines are shown flagged and the counter reads 000.

## 3. How it is used
- Click a hidden cell with the left button or tap: reveals it.
- Click a revealed number cell: if its adjacent flags equal its number, reveals all its other hidden neighbours (chord).
- Hold the left button on a hidden cell: it looks pressed and the face turns shocked; releasing reveals it.
- Right-click a hidden cell, or long-press on touch: places a flag.
- Right-click or long-press a flagged cell: removes the flag.
- Click the face button: starts a new round at the current difficulty.
- Click a difficulty in the bar: starts a new round at that size.
- Click or right-click a revealed cell: nothing happens, except chording as above.
- Click a flagged cell: nothing happens.
- After win or loss, cell clicks do nothing.

## 4. Scope
One loop: choose a difficulty, play a round by revealing and flagging, finish in a win or loss, restart. Beginner, Intermediate and Expert are offered. There are no accounts, leaderboards, payments or admin features.

## 5. Things and their states
- **Cell**: holds mine or not, adjacent mine count, and a state of hidden, flagged or revealed. Hidden to flagged and back on flag toggle; hidden to revealed on reveal.
- **Board**: a grid of cells with a width, height and mine count.
- **Round**: states are ready (no reveal yet), in progress, won, lost. First reveal moves ready to in progress; revealing a mine moves it to lost; revealing every non-mine cell moves it to won.

## 6. Rules
- Beginner is 9×9 with 10 mines; Intermediate 16×16 with 40; Expert 30×16 with 99.
- Mines are placed at the first reveal, at random.
- The first revealed cell and its neighbours never hold a mine, so the first reveal always opens an area.
- A cell's number is the count of mines among its up to eight neighbours.
- Revealing a cell with zero adjacent mines automatically reveals all its neighbours, repeating outward.
- Cascades never reveal flagged cells; they stay flagged.
- Revealing a mine ends the round as lost.
- Revealing all non-mine cells wins the round; flags are not required.
- A flagged cell cannot be revealed; the click is ignored.
- A revealed cell cannot be flagged; the action is ignored.
- Flags are unlimited, and the counter may go below zero.
- Chording on a cell whose flag count differs from its number does nothing.
- Chording reveals neighbours even if flags are wrong, so a wrong flag can cause a loss.
- The timer starts at the first reveal; flagging before it does not start it.
- On a loss, the round freezes and the timer stops.
- A round ends only by win, loss, or the player starting a new round.