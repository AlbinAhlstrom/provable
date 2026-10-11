# A minesweeper game

## 1. People and their journey
**Player** (the only role): someone playing for fun. They arrive at a fresh board, choose a difficulty if they wish, reveal cells, flag suspected mines, and finish when every safe cell is revealed (won) or a mine is revealed (lost). They then start a new round.

## 2. How it looks

The product looks like classic Windows Minesweeper: a grey, beveled window with a header panel above a square-cell grid.

- **Page background:** flat mid-grey (#c0c0c0) fills the page; the game panel is centred on it.
- **Game panel:** raised grey bevel, white on top and left edges, dark grey on bottom and right, with padding around its contents.
- **Difficulty selector:** a row of three text buttons above the header: Beginner, Intermediate, Expert. The current one is underlined; pressed buttons look sunken.
- **Header panel:** sunken bevel strip across the top of the panel, holding the mine counter, face button and timer.
- **Mine counter:** left of the header; black box with red seven-segment digits, three wide, showing mines minus flags. It goes negative (e.g. -02) when flags exceed mines.
- **Face button:** centred in the header; raised grey square with a yellow smiley. Sunken while pressed. Shows an "ooh" face while a cell is held down, sunglasses face when won, dead face (X eyes) when lost.
- **Timer:** right of the header; black box with red seven-segment digits, three wide, showing seconds from first reveal. Stops on win or loss; caps at 999.
- **Board:** sunken bevel below the header, a grid of square cells: 9×9 with 10 mines, 16×16 with 40, 30×16 with 99.
- **Hidden cell:** raised grey square with light top-left and dark bottom-right edges. While held down it looks flat like a revealed empty cell.
- **Revealed empty cell:** flat light grey with a thin darker grey border and no number.
- **Number cells:** a revealed cell shows its adjacent mine count in bold colour: 1 blue (#0000ff), 2 green (#008000), 3 red (#ff0000), 4 dark blue (#000080), 5 maroon (#800000), 6 teal (#008080), 7 black, 8 grey (#808080).
- **Flagged cell:** a hidden-looking raised cell with a red flag on a black pole and base. Flagged cells ignore reveal clicks.
- **Mine cell:** revealed with a black spiked mine circle with a white highlight. The mine that was clicked has a red background.
- **Wrong flag:** after a loss, a flag on a non-mine cell shows a mine with a red diagonal cross over it.
- **Won board:** unflagged mines are automatically shown as flags, and the counter reads 000.

## 3. How it is used

- Click a difficulty button: starts a new round at that size.
- Left-click a hidden cell: reveals it. The first reveal starts the timer.
- Left-click a revealed number whose adjacent flags equal its number, or press left and right buttons together (a two-finger tap is unavailable on touch): reveals all its unflagged neighbours.
- Right-click a hidden cell (long press on touch): cycles it from hidden to flagged and back to hidden.
- Click the face button: abandons the round and starts a new one at the same difficulty.
- Hold the mouse button on a hidden cell: the face shows "ooh"; releasing outside the cell cancels the reveal.

## 4. Scope
One loop: pick a difficulty, play a board by revealing and flagging until won or lost, then restart. There are no accounts, leaderboards, multiplayer, payments or admin. Custom board sizes are not offered.

## 5. Things and their states
- **Cell:** holds mine or not, adjacent count, and state: hidden, flagged, revealed.
- **Round:** holds difficulty, the cells, flag count, and elapsed time. States: ready (no reveal yet), in progress, won, lost. The first reveal moves ready to in progress. Revealing a mine moves it to lost. Revealing every non-mine cell moves it to won.

## 6. Rules
- Mines are placed on the first reveal, never on the clicked cell or its neighbours, so the first click is always a zero-count cell and opens an area.
- A cell's count is the number of mines among its up to eight neighbours.
- Revealing a mine ends the round as lost.
- Revealing a zero-count cell automatically reveals all its neighbours, repeating through further zero cells.
- Flood reveal never reveals flagged cells, and stops at numbered cells.
- Revealing a cell that is flagged or already revealed is ignored.
- A flag can only be placed on a hidden cell; flagging a revealed cell is ignored.
- Flags can exceed the mine count; the counter goes negative.
- Chording on a number with a mismatched flag count is ignored.
- Chording reveals every unflagged neighbour; a wrong flag means a mine is revealed and the round is lost.
- Winning requires every non-mine cell revealed; flags are not needed.
- On a loss all unflagged mines are shown, and wrong flags are marked.
- After a win or loss, reveals and flags are ignored until a new round starts.
- The timer starts on the first reveal, counts whole seconds, and stops on win or loss.
- Changing difficulty or clicking the face at any time ends the current round without an outcome and starts a new one.