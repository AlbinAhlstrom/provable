# Minesweeper

## 1. People and their journey
**Player** (the only role): someone playing for fun, alone.
- Arrives and sees a ready, covered board at the Beginner level with the mine counter and timer at rest.
- Decides where to reveal and where to flag, optionally changes difficulty, and finishes by winning or losing.
- Then starts a new round from the face button or the Game menu.

## 2. How it looks
Minesweeper looks like the classic Windows desktop Minesweeper: a small grey program window with a blue title bar, sitting on a plain teal desktop. Everything inside is square-edged, pixelated and bevelled.

- **Desktop backdrop**: fills the page, flat teal (#008080); the window sits centred on it.
- **Window**: light grey (#C0C0C0), raised bevel (white top and left, dark grey bottom and right), with a blue title bar.
- **Title bar**: top of the window, dark blue, white bold text "Minesweeper", with a small mine icon at the left. It has no window buttons.
- **Menu bar**: under the title bar, grey, with "Game" and nothing else. When Game is open, a raised grey drop-down panel appears with the items below.
- **Game menu items**: New (F2); a divider; Beginner, Intermediate, Expert, each with a tick beside the current level; Marks (?) with a tick when on. Hovered item is dark blue with white text.
- **Status panel**: below the menu bar, grey with a sunken bevel, holding counter, face and timer in a row.
- **Mine counter**: left of the status panel, black sunken box with three red seven-segment digits showing mines minus flags. It goes negative (for example -02) if flags exceed mines.
- **Face button**: centred in the status panel, a raised grey square with a yellow round face. Pressed, it looks sunken.
  - Ready or playing: smile.
  - While a covered cell is held down: surprised "o" mouth.
  - Won: sunglasses.
  - Lost: dead face with X eyes.
- **Timer**: right of the status panel, black sunken box with three red seven-segment digits counting seconds, stopping at 999.
- **Board**: below the status panel, in a sunken bevelled frame. It is a grid of square cells: 9×9 at Beginner, 16×16 at Intermediate, 30×16 (wide) at Expert.
- **Covered cell**: grey (#C0C0C0), raised bevel, blank.
- **Held cell**: a covered cell under the press looks flat like a revealed blank.
- **Revealed empty cell**: flat lighter grey with a thin dark-grey outline, blank.
- **Number cell**: a revealed cell showing a bold digit coloured by count:
  - 1 blue
  - 2 green
  - 3 red
  - 4 dark navy
  - 5 maroon
  - 6 teal
  - 7 black
  - 8 grey
- **Flagged cell**: a covered cell with a red flag on a black base.
- **Marked cell**: a covered cell with a black "?" (only when Marks is on).
- **Mine cell (lost)**: a revealed cell with a black spiked mine and a white glint. The mine that was clicked has a red background.
- **Wrong flag (lost)**: a flag-marked cell with no mine shows a mine crossed by a red X.
- **Unflagged mines at a win**: automatically become flags, and the counter shows 000.

## 3. How it is used
- Left-click a covered cell: reveals it. The first reveal is always safe.
- Left-click a revealed number whose adjacent flag count equals the number (chord): reveals all its other covered neighbours.
- Right-click a covered cell (or long-press on touch): cycles blank → flag → "?" (if Marks is on) → blank.
- Press and hold a covered cell: the face shows surprise. Moving off the cell cancels the reveal on release.
- Click the face: starts a new round at the current level.
- Press F2: starts a new round.
- Choose Game → Beginner, Intermediate or Expert: switches the level and starts a new round.
- Choose Game → Marks (?): toggles "?" marks. Turning it off clears existing "?" cells to blank.
- Click Game: opens the menu. Click elsewhere or press Escape to close it.
- Touch: tap reveals; long-press flags; tap a satisfied number to chord.

## 4. Scope
One loop: choose a level, reveal and flag until all safe cells are revealed or a mine is hit, then start again. No accounts, leaderboards, custom board size, or best-times list.

## 5. Things and their states
- **Cell**: holds mine yes/no, adjacent-mine count (0–8), and a mark. It is covered, flagged, questioned or revealed. Reveal moves covered or questioned cells to revealed; right-click cycles marks.
- **Round**: holds level, mine layout, flag count and elapsed seconds. States: ready (no reveal yet), in progress, won, lost. First reveal moves ready to in progress. Revealing a mine moves it to lost. Revealing every safe cell moves it to won.

## 6. Rules
- Beginner: 9×9 with 10 mines. Intermediate: 16×16 with 40. Expert: 30×16 with 99.
- Mines are placed on the first reveal, never on the first-clicked cell. Classic rules allow the first cell's neighbours to hold mines.
- A cell's number is the count of mines among its up to 8 neighbours.
- Revealing a zero-count cell automatically reveals all neighbours, repeating through further zero cells.
- Flood reveal never opens flagged cells. It does open "?" cells.
- Revealing a mine loses the round: all mines are shown, wrong flags are marked, and the clicked mine is red.
- Revealing a flagged cell is ignored.
- Revealing an already revealed number does nothing, except chording.
- Chording with the wrong flag count does nothing. If a flag is wrong, chording reveals a mine and loses.
- Flags can be placed only on covered cells. Revealed cells ignore right-click.
- Flags are unlimited; the counter may go below zero.
- The timer starts at the first reveal, ticks each second, and stops on win or loss.
- The timer shows at most 999.
- The round is won when all non-mine cells are revealed; flags are not required.
- After a win or loss, the board ignores clicks until a new round starts.
- Before the first reveal, flags are allowed, and the timer stays at 000.
- Starting a new round discards the current one without confirmation.
- Changing level always starts a fresh round.
- Marks (?) is off by default for the session.
- Ways to end: win, loss, or abandoning by starting a new round.