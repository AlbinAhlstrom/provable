# Minesweeper

## 1. People and their journey

**Player** (the only role; the intent names one audience: players who want to play minesweeper for fun).
- Needs to see: the hidden board, the mine counter, the elapsed time, and the session outcome.
- Decides: which cell to reveal, which hidden cell to flag or unflag, and whether to start another round.
- Path: arrives at the board with a new round ready → reveals a first cell → reads adjacency numbers and flags suspected mines → reveals every safe cell → sees the win screen; or reveals a mine and sees the loss screen → chooses to play again or stop.

## 2. How it looks

A classic Windows-style minesweeper: a grey, bevelled window holding a numbered square grid under a status bar, with flat grey cells and bright numerals on a plain surface.

Parts, back to front, top to bottom:

- **Window background:** solid mid-grey (#C0C0C0) raised frame with a white top-left bevel and dark grey bottom-right bevel, filling the screen behind the game.
- **Title bar:** dark navy (#000080) strip across the top of the window, with white text "Minesweeper" on the left.
- **Status bar:** grey band under the title holding the mine counter on the left, a smiley face button in the centre, and the elapsed timer on the right.
- **Mine counter:** black panel with red three-digit seven-segment numbers showing mines remaining (total mines minus flags placed); it can go negative.
- **Smiley button:** raised grey square with a yellow face; it shows a smile normally, a pressed face while a cell is held down, sunglasses when won, and an X-eyed face when lost; clicking it starts a new round.
- **Timer:** black panel with red three-digit numbers counting elapsed seconds from the first reveal, capped at 999; it stops when the round ends.
- **Game board:** sunken grey grid of square cells beneath the status bar, sized to the chosen difficulty.
- **Hidden cell:** raised grey square with a white top-left and dark grey bottom-right bevel; it turns sunken and flat while pressed.
- **Revealed empty cell:** flat light-grey square with no mark, the cell is blank.
- **Revealed number cell:** flat light-grey square with a single number 1 (blue), 2 (green), 3 (red), 4 (dark blue), 5 (maroon), 6 (teal), 7 (black), or 8 (grey).
- **Flagged cell:** raised hidden-style square with a red flag on it; it cannot be revealed until unflagged.
- **Revealed mine:** flat light-grey square with a black mine; on the losing cell its background is red.
- **Wrongly flagged mine (loss only):** revealed mine cell showing a red X over the mine.
- **Question mark cell:** not used; no third marking exists.
- **Difficulty menu:** a small list reached from the title bar's game menu, offering Beginner, Intermediate and Expert, each with its check mark when current.
- **Win and loss message:** no pop-up; the smiley changes face, and the timer stops.

## 3. How it is used

- **Left-click hidden cell:** reveals it; the first click of a round never hits a mine.
- **Right-click hidden cell:** places a flag; right-click a flagged cell to remove it.
- **Left-click and right-click together on a revealed number cell:** if its adjacent flags equal its number, reveals all its other hidden neighbours; otherwise nothing happens.
- **Left-click on a flagged cell:** nothing happens.
- **Left-press and hold a hidden cell:** shows it pressed; releasing over it reveals it, moving off cancels.
- **Left-press and hold on the smiley:** shows pressed face; releasing starts a new round.
- **Click smiley:** starts a new round at the current difficulty.
- **Long press (touch) on hidden cell:** places or removes a flag.
- **Tap (touch) on hidden cell:** reveals it.
- **Tap a revealed number cell with flags around it, touch:** tap the number with two fingers to chord, as with the mouse.
- **Tap smiley (touch):** starts a new round.
- **Choose Beginner, Intermediate or Expert from the game menu:** starts a new round at that size and mine count.
- **Press F2 (keyboard):** starts a new round.
- **Arrow keys:** move a highlighted cell focus; Enter reveals; F or Space places or removes a flag.

## 4. Scope

The player opens the game, which shows a new Beginner round (9×9, 10 mines). They reveal a cell; the first reveal places mines away from it and starts the timer. They read numbers, flag suspected mines and reveal safe cells until every non-mine cell is revealed (won) or a mine is revealed (lost). They may change difficulty (Beginner 9×9/10 mines, Intermediate 16×16/40 mines, Expert 30×16/99 mines) and start again.

## 5. Things and their states

- **Round (session):** holds difficulty, board, timer, mine counter, outcome.
  - Ready → In progress (first reveal) → Won (all safe cells revealed) or Lost (mine revealed).
  - Any state → Ready when a new round starts or difficulty changes.
- **Cell:** holds mine flag, adjacency count, and marking.
  - Hidden → Revealed (left-click, not flagged) or Flagged (right-click).
  - Flagged → Hidden (right-click again).
  - Revealed cells do not change.
- **Board:** holds a fixed grid of cells and mine positions for one round; set on first reveal, fixed until new round.
- **Timer:** counts seconds from first reveal; stops on Won or Lost; resets on new round.
- **Mine counter:** total mines minus flags; updates on each flag change.

## 6. Rules

- Board is a grid of cells; each cell is hidden, revealed or flagged.
- Mines are placed at random on the first reveal, never on that cell or its eight neighbours, so the first reveal opens an area when it has no adjacent mines.
- Each revealed non-mine cell shows the count of mines in its eight neighbours; zero counts show as blank and auto-reveal all neighbours recursively.
- Revealing a mine ends the round as Lost; all mines are revealed, the losing mine is red, wrongly flagged cells show a red X.
- Revealing every non-mine cell ends the round as Won; all unflagged mines are marked with flags automatically.
- A flagged cell cannot be revealed by left-click; attempts do nothing.
- Flags can be placed on hidden cells only; flagging a revealed cell does nothing.
- Flags can be placed in any number, even beyond the mine count; the mine counter goes negative.
- Chording reveals neighbours only when adjacent flags equal the number; if a wrong flag causes a mine to be revealed, the round is Lost.
- Clicks after Won or Lost are ignored, except smiley and difficulty change, which start a new round.
- The timer stops at Won or Lost and does not run before the first reveal.
- Difficulty change or smiley click resets the round to Ready with a new empty board.
- Beginner: 9×9, 10 mines. Intermediate: 16×16, 40 mines. Expert: 30×16, 99 mines.