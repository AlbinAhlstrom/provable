# Minesweeper: Product Specification

## 1. People and their journey

**Player** (the only role). Wants to play one round of classic minesweeper for fun.

- Arrives at a fresh board with the difficulty already set, or chooses one.
- Reveals cells to find the safe ones and flags cells they believe hold mines.
- Finishes when the round is won or lost, then either starts a new round or stops.

## 2. How it looks

Minesweeper, as most people know it from the classic Windows game: a grey, beveled, 1990s-style window with a single board of square tiles, a red digit counter and timer, and a smiley face button.

- **Page background:** solid mid-grey (#C0C0C0), filling the whole window with no gradient or image.
- **Menu bar:** along the top, flat grey, with the words "Game" and "Help" in black, 12px sans-serif. "Game" opens a menu of Beginner, Intermediate, Expert, and Exit (Exit is not offered in the web page and is omitted).
- **Status panel:** directly under the menu bar, a sunken grey strip with a dark outline, holding the mine counter on the left, the face button in the centre, and the timer on the right.
- **Mine counter:** a black box with a sunken edge, showing three red seven-segment digits, zero-padded, from 000 up to 999 and down to negative values like -05.
- **Timer:** identical to the mine counter in style, showing elapsed seconds in red digits, capped at 999.
- **Face button:** a raised square, 26px, yellow circle face with black eyes and smile. While the left button is held on the board it shows a surprised "o" mouth. After a win it shows sunglasses and a smile. After a loss it shows X eyes and a frown.
- **Board:** a sunken grey panel directly below the status panel, holding a grid of square tiles with no gap between them.
- **Hidden cell:** a raised light-grey tile (#C0C0C0) with a white top and left bevel and a dark-grey bottom and right bevel, empty.
- **Hidden cell while pressed:** the same tile, flat, with the bevel reversed to a sunken look, while the mouse button is held down over it.
- **Flagged cell:** a hidden tile showing a small red flag on a black pole, with a black base.
- **Revealed empty cell:** a flat light-grey tile with a thin grey outline and no number.
- **Revealed number cell:** a flat light-grey tile with one digit in the centre, coloured by value: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 grey.
- **Mine cell (after loss):** a flat light-grey tile with a black circle with spikes. The mine the player clicked has a red background behind it.
- **Wrong flag (after loss):** a flat light-grey tile with a red X over a black mine circle.
- **Unrevealed mine (after loss):** a flat light-grey tile with a black mine circle, shown for every mine the player did not flag.

## 3. How it is used

- **Left-click a hidden cell:** reveals it. Touch: tap.
- **Right-click a hidden cell:** places a flag, or removes one if already flagged. Touch: press and hold for about half a second, then release.
- **Left-click a revealed number:** if the number of flags around it equals its number, reveals all its unflagged hidden neighbours. If a wrong flag is among them, the game is lost. Touch: tap the number.
- **Left-click a flagged cell:** nothing happens; the flag must be removed first with a right-click or long press.
- **Click the face button:** starts a new round at the current difficulty. Touch: tap.
- **Game menu, Beginner / Intermediate / Expert:** starts a new round at that difficulty. Touch: tap in the menu.
- **Help menu:** not included in the product.

## 4. Scope

A player opens the page, sees a Beginner board, optionally picks another difficulty, reveals a cell (which starts the timer), uses numbers and flags to deduce mines, and reaches a win or a loss. They can then start a new round. Out of scope: user accounts, saved games, leaderboards, multiplayer, payments, and any admin tools.

## 5. Things and their states

- **Board:** holds a grid of cells and the mine layout. Fixed for a round; created at the first reveal. Its size and mine count come from the difficulty.
- **Cell:** holds its mine status, its adjacent-mine count (0 to 8), and its display state. States: hidden, flagged, revealed. Hidden to revealed when revealed by the player or by a cascade; hidden to flagged and back by flag actions; flagged cells cannot be revealed directly.
- **Game session:** holds the outcome and elapsed time. States: ready (no reveal yet), in progress (after first reveal), won, lost. Ready to in progress on the first reveal; in progress to won when every safe cell is revealed; in progress to lost when a mine is revealed. Won and lost end the timer and are final until a new round starts.

## 6. Rules

- The board is a grid of square cells. Beginner is 9 by 9 with 10 mines; Intermediate is 16 by 16 with 40 mines; Expert is 30 by 16 with 99 mines.
- Mines are placed randomly, with no mine on the first revealed cell or any of its eight neighbours. If a player tries a first reveal that is not possible, the layout is reshuffled to allow it.
- Each non-mine cell shows the count of mines among its eight neighbours; a cell with zero neighbouring mines shows no number.
- Revealing a zero-count cell also reveals all its neighbours, and repeats for any neighbour that is also zero, until the edge of the connected empty area.
- Revealing a mine ends the game as lost.
- Flags can be placed on hidden cells only. Placing a flag on a revealed cell is refused and nothing changes.
- Flagging a hidden cell is refused once every mine has... no; flags are never limited in number, so a flag is always accepted on a hidden cell.
- Revealing a flagged cell is refused and nothing changes; the flag must be removed first.
- The mine counter shows the total mine count minus the number of flags placed, and may go negative.
- The timer starts at the first reveal, increases by one each second, and stops when the game is won or lost.
- The game is won when every non-mine cell is revealed; flags do not need to be correct or complete for a win.
- On a loss, every mine that was not flagged is revealed, every wrong flag is shown as a wrong flag, and the timer stops.
- A left-click on a revealed number whose flag count does not match its number is refused and nothing changes.
- Chording reveals the unflagged hidden neighbours of a number whose flag count matches; if any of those neighbours is a mine, the game is lost.
- Actions after a won or lost game are refused, except the face button and the difficulty menu, which start a new round.
- The face button, and the difficulty choice, end the current round immediately and start a new one; the current round is abandoned and not counted.