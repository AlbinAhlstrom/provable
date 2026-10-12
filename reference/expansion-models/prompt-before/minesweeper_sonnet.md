# Minesweeper: Product & Behavioral Specification

## 1. Persona and Journey
**The Player** is the only role. They want a quick, classic round of minesweeper. They see the board, the mines-remaining counter and the round status. They decide which cell to reveal or flag next. They finish with a win or a loss and can start a new round at once. There are no accounts, scores shared with others, or administrators.

## 2. Presentation and Interaction
The game looks like classic Minesweeper:
- Grey, raised square tiles in a tight grid with a bevelled border. Revealed tiles are flat and lighter, with thin lines.
- Numbers use the familiar colours: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 grey.
- Flags are red on a pole. Mines are black spiked circles. A wrongly flagged cell is shown crossed out at the end of a loss. The mine that was triggered is highlighted red.
- A header above the grid shows the mines-remaining counter on the left, a smiley new-round button in the centre (neutral, worried while pressing, sunglasses on a win, dead on a loss) and an elapsed-seconds counter on the right. Counters use red digits on black.
- Primary click or tap reveals. Secondary click or long-press flags and unflags. Clicking a revealed number whose adjacent flags match that number reveals its remaining neighbours (chording).
- Beginner (9×9, 10 mines), Intermediate (16×16, 40) and Expert (30×16, 99) difficulties can be chosen.

## 3. Scope
One local, single-player round at a time: choose difficulty, play, see the outcome, restart.

## 4. Core Concepts
- **Board:** a grid of cells with a chosen size and mine count.
- **Cell:** has a mine or not, an adjacent-mine count (0–8), and a state: hidden, flagged or revealed.
- **Round:** not started → in progress → won or lost.
- **Moves:** reveal, flag/unflag, chord.

## 5. Rules
- **Mine count:** the board holds exactly the chosen number of mines, at most one per cell.
- **Adjacency numbers:** each non-mine cell shows how many of its up to eight neighbours hold mines.
- **First reveal is safe:** the first revealed cell, and its neighbours, never contain a mine. Mines are placed after that first reveal.
- **Reveal a hidden cell:** the cell becomes revealed.
- **Zero cascade:** revealing a cell with count 0 automatically reveals all its neighbours, repeating through further zeros. Flagged cells are never auto-revealed.
- **Reveal a mine:** the round is lost. All mines are shown and wrong flags are marked.
- **Flagging:** a flag can only be placed on a hidden cell, and removed by flagging again. Flags may exceed the mine count, in which case the counter goes negative.
- **Flagged cells are protected:** a flagged cell cannot be revealed until unflagged.
- **Revealed cells:** these cannot be flagged or revealed again, apart from chording.
- **Chording:** it applies only to a revealed numbered cell whose adjacent flag count equals its number. It reveals all non-flagged neighbours. If a flag is wrong, a mine is revealed and the round is lost. Otherwise it does nothing.
- **Win:** every non-mine cell is revealed. Mines are then auto-flagged and the counter shows 0.
- **Ending a round:** a round ends only by win, loss, or the player starting a new round, which abandons the current one.
- **Finished rounds:** after a win or loss, reveal and flag are rejected and the board is unchanged.
- **Timer:** it starts on the first reveal and stops on win or loss.
- **Invalid moves:** moves outside the grid, or on cells in the wrong state, are ignored with no state change.