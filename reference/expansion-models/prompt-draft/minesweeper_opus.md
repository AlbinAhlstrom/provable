# Minesweeper

## 1. People and their journey
**Player** (the only role). They arrive at the page and a fresh Beginner board is waiting. They choose a difficulty and start clicking cells. They use the numbers to work out where the mines are, flag the cells they believe hold mines, and keep revealing safe cells. The round ends when they uncover every safe cell (win) or reveal a mine (loss). At any point they can start a new round by clicking the face button. To play well they need to see the mines-remaining counter, the elapsed time, the face showing how the round stands, and every cell's state.

## 2. How it looks
It looks like the classic Windows Minesweeper: a grey, bevelled 3D window holding a black-and-red digital counter panel above a grid of raised grey squares.

- **Page background**: flat teal (#008080) that fills the whole window, with the game centred on it.
- **Difficulty bar**: a row above the game window with three flat grey text buttons, Beginner, Intermediate and Expert. The selected one appears sunken with bold text.
- **Game window**: a light grey (#C0C0C0) panel with a raised bevel, white on its top and left edges and dark grey (#808080) on its bottom and right.
- **Header panel**: a sunken grey strip across the top of the window. It holds the mine counter on the left, the face button in the centre and the timer on the right.
- **Mine counter**: a sunken black box showing three red seven-segment digits for mines minus flags. A negative value shows a leading minus, for example "-02".
- **Face button**: a raised grey square with a yellow smiley face. It shows an open-mouthed "oh" face while a cell is pressed, sunglasses when the round is won and X eyes when the round is lost. It appears sunken while it is clicked.
- **Timer**: a sunken black box showing three red seven-segment digits for seconds elapsed, starting at 000 and stopping at 999.
- **Board**: a sunken grey frame holding the grid. Beginner is 9×9, Intermediate is 16×16 and Expert is 30 columns by 16 rows.
- **Hidden cell**: a raised grey square with white top and left edges and dark grey bottom and right edges. It appears flat and sunken while pressed.
- **Flagged cell**: a hidden cell carrying a red triangular flag on a black pole with a black base.
- **Revealed empty cell**: a flat grey square with a thin dark grey outline and no mark.
- **Revealed number cell**: a flat grey square with a bold number, each number in its own colour:
  - 1 is blue
  - 2 is green
  - 3 is red
  - 4 is navy
  - 5 is maroon
  - 6 is teal
  - 7 is black
  - 8 is grey
- **Mine (on loss)**: a black round mine with spikes and a white glint, shown on every unflagged mine cell.
- **Exploded mine**: the mine the player clicked, drawn on a red background.
- **Wrong flag (on loss)**: a flag on a cell with no mine, shown as a mine crossed with a red X.
- **Win board**: every mine cell shows a flag, and the mine counter reads 000.

## 3. How it is used
- **Click a hidden cell** (tap on touch): reveals it. A mine ends the round as a loss, a number shows its count, and a blank opens all connected blank cells and their bordering numbers.
- **Right-click a hidden cell** (long press on touch): places a flag. Doing it again on a flagged cell removes the flag.
- **Press and hold on a hidden cell**: the cell appears sunken and the face shows "oh". Releasing over a cell reveals that cell, and dragging off before release cancels.
- **Chord (left and right click together, or middle-click, or click a revealed number; tap a number on touch)**: if the flags touching the number equal the number, every other unflagged hidden neighbour is revealed.
- **Click the face button**: starts a new round at the current difficulty.
- **Click a difficulty button**: starts a new round at that size.

## 4. Scope
The loop is to choose a difficulty, reveal and flag cells until the round is won or lost, and then start again. Out of scope: accounts, leaderboards, saved best times, custom board sizes, question-mark marks, sound, multiplayer, payments and administration.

## 5. Things and their states
- **Round**: holds the difficulty, the size, the mine count, the board, the timer value and the flag count. Its states are:
  - **Ready**: no click has been made yet.
  - **In progress**: entered on the first reveal.
  - **Won**: entered when every safe cell is revealed.
  - **Lost**: entered when a mine is revealed.
  - The face button or a difficulty button returns the round to Ready with a new board.
- **Cell**: holds whether it has a mine and its count of adjacent mines. It moves between Hidden and Flagged by flag toggles, and from Hidden to Revealed when revealed. Flagged cells cannot be revealed directly.
- **Mine layout**: placed when the first reveal happens.

## 6. Rules
- **Sizes**: Beginner is 9×9 with 10 mines. Intermediate is 16×16 with 40 mines. Expert is 30×16 with 99 mines.
- **Mine placement**: mines are placed at random on the first reveal, never on the clicked cell or its eight neighbours.
- **Adjacency count**: each safe cell's number is the count of mines among its up-to-eight neighbours, including diagonals.
- **Reveal**: revealing a safe cell shows its number, or shows it blank if the number is zero.
- **Flood fill**: revealing a blank cell automatically reveals all of its neighbours, repeating through every connected blank cell.
- **Flagged cells**: a click on a flagged cell is ignored and nothing changes.
- **Revealed cells**: a right-click on a revealed cell is ignored.
- **Clicking a revealed cell**: a plain click on a revealed blank cell does nothing. A click on a revealed number cell attempts a chord.
- **Flag limit**: flags are unlimited, so the counter may go negative.
- **Chord**: chording reveals the remaining hidden neighbours only when the adjacent flag count equals the number. Otherwise it is ignored.
- **Wrong chord**: if a chord reveals a mine because a flag was misplaced, the round is lost.
- **Loss**: revealing a mine loses the round. The clicked mine shows on red, all other mines are revealed, and wrong flags are crossed out.
- **Win**: the round is won when every non-mine cell is revealed, whether or not the mines are flagged. Remaining mines are then auto-flagged.
- **Timer start**: the timer starts at the first reveal.
- **Timer stop**: the timer stops on a win or loss, and it caps at 999.
- **After the round ends**: all clicks on the board are ignored until a new round starts.
- **Ending by choice**: the player may end a round at any time with the face button or a difficulty change. The round is discarded with no outcome.