# Minesweeper: Product & Behavioral Specification

## 1. Persona & Value Journey
**Player**: someone playing Minesweeper for fun.
- **Sees:** the grid, the mine counter (mines minus flags), a timer and a face button.
- **Decides:** which cell to reveal and which to flag.
- **Accomplishes:** clears every safe cell to win, or hits a mine and loses, then starts again.

## 2. Presentation & Interaction
It looks like classic Windows Minesweeper:
- **Board:** a grey bevelled panel holding a square grid of raised grey tiles.
- **Revealed cells:** shown flat and sunken.
- **Number colours:** 1 blue, 2 green, 3 red, 4 navy, 5 maroon, 6 teal, 7 black, 8 grey.
- **Flags:** small red flags on raised tiles.
- **Mines:** black mines. The mine that ended the game sits on a red background.
- **Top bar:** a red digital mine counter on the left, a yellow smiley button in the centre and a red digital timer on the right.
- **The smiley:** grins sunglasses-on when you win and shows X-eyes when you lose. Clicking it starts a new game.

Controls:
- **Left-click:** reveals a cell.
- **Right-click:** toggles a flag.
- **Difficulty picker:** Beginner 9×9 with 10 mines, Intermediate 16×16 with 40 mines, Expert 30×16 with 99 mines.

## 3. MVP Scope
The core loop is: choose difficulty, play the round, see the outcome, start a new game. Nothing else is built.

## 4. Core Concepts
- **Game:** has a difficulty, a board, a timer and a status. Its statuses move in this order:
  - **Ready:** no cell revealed yet.
  - **In Progress:** after the first reveal.
  - **Won** or **Lost:** final for that game.
- **Board:** a grid of cells with a fixed mine layout once placed.
- **Cell:** holds whether it is a mine and its adjacent-mine count (0–8). It is Hidden, Flagged or Revealed:
  - Hidden ↔ Flagged
  - Hidden → Revealed
- **Move:** a Reveal or a Flag toggle on one cell.

## 5. Rules
1. **Grid & mines:** board size and mine count are fixed by the chosen difficulty.
2. **Mine placement:** mines are placed randomly when the first reveal happens.
3. **First-click safety:** the first revealed cell is never a mine.
4. **Adjacency count:** every non-mine cell shows how many of its up-to-8 neighbours hold mines.
5. **Reveal:** revealing a Hidden cell turns it Revealed.
6. **Zero cascade:** revealing a 0-cell automatically reveals all its neighbours, repeating through connected zeros.
7. **Cascade and flags:** the cascade never reveals Flagged cells.
8. **Flag toggle:** right-click switches a cell between Hidden and Flagged.
9. **Flag lock:** a Flagged cell cannot be revealed until it is unflagged.
10. **No flag limit:** flags may exceed the mine count. The counter may go negative.
11. **Revealed cells are final:** they cannot be flagged or re-revealed. Such moves are ignored with no change.
12. **Timer:** starts on the first reveal, stops when the game ends, and caps at 999.
13. **Loss:** revealing a mine ends the game as Lost. All mines are shown, and wrongly placed flags are marked crossed.
14. **Win:** revealing every non-mine cell ends the game as Won. Remaining mines are auto-flagged.
15. **Win without flags:** flagging is never required to win.
16. **Ended games are locked:** after a win or loss, all moves on the board are ignored.
17. **Player ends the game:** a new game or a difficulty change at any time abandons the current game. An abandoned game is recorded as neither a win nor a loss.
18. **Invalid moves:** moves outside the grid or on locked cells are rejected. The board and status stay unchanged.