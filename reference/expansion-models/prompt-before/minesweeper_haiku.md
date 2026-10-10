# Minesweeper

## 1. Personas & Value Journey
**Player (the only persona).** Wants to play a classic round of minesweeper for fun. Needs to see the board, understand the rules at a glance, decide where to reveal or flag, and find out clearly whether they won or lost. (Nobody else is in scope: no accounts, admins, or spectators.)

Journey: start a new round → read the hidden board → reveal and flag cells → reach a win or loss → start another round.

## 2. Presentation & Interaction
- Looks like the classic minesweeper: a rectangular grid of grey, raised square tiles; revealed tiles flat and light grey; numbers coloured in the traditional palette (1 blue, 2 green, 3 red, 4 dark blue, and so on); mines shown as black dots and flags as red flags.
- A header bar above the grid shows a mine counter (mines minus flags), an elapsed timer, and a smiley-style face that shows game status and restarts the round when pressed.
- Interactions: primary click reveals a tile; secondary click (or long press on touch) toggles a flag; clicking a number that is already satisfied by adjacent flags may reveal its unflagged neighbours (optional convenience, not required).
- Game-over shows every mine, marks wrongly placed flags, and highlights the mine that was hit.

## 3. MVP Scope
Single round, single player, one board at a time. Choose difficulty presets (beginner, intermediate, expert) as the only setup. Nothing else.

## 4. Core Concepts & States
- **Board:** a grid of cells with a fixed size and mine count.
- **Cell:** has a mine or not, an adjacent-mine count, and a state: *hidden*, *revealed*, or *flagged*.
- **Game session (round):** states *ready* (no first move yet), *in progress*, *won*, *lost*.
- **Move:** *reveal* or *flag/unflag*.

Transitions: ready → in progress (first reveal) → won (all safe cells revealed) or lost (a mine revealed).

## 5. Business Rules
1. Mine placement: mines are placed randomly after the first reveal, so the first revealed cell and its neighbours are always mine-free.
   - The first revealed cell is never a mine.
   - Neighbours of the first revealed cell are never mines (if the layout allows, otherwise only the cell itself is guaranteed).
2. Adjacency count: each safe cell shows the number of mines in its eight neighbouring cells (0 shows as blank).
3. Reveal: a hidden cell becomes revealed.
   - Revealing a blank (0) cell automatically reveals its neighbours, recursively.
   - Revealing a mine ends the round as lost.
   - Flagged cells cannot be revealed directly; the player must unflag first.
4. Flag: a hidden cell may be flagged or unflagged. Revealed cells cannot be flagged.
   - Flags are limited to the number of mines on the board? No: flags are unlimited, but the mine counter may go negative.
5. Win: the round is won when every non-mine cell is revealed (flags on mines are not required).
6. Loss: the round is lost when a mine is revealed. All mines are then displayed.
7. Timer: starts on the first reveal and stops when the round ends.
8. Restart: the player may abandon the current round at any time and start a new one; this counts as a loss with no record kept.
9. Invalid moves (revealing a flagged cell, flagging a revealed cell, any move after the round has ended) are rejected with no change to the board or timer.
10. No accounts, scores, or saved games.