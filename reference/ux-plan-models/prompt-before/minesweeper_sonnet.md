### 1. Default Landing & Cold-Start Behavior
- The game opens straight onto a ready Beginner board (9×9, 10 mines): there is no menu, intro or splash. The mine counter reads 010, the timer 000, and the face is smiling.
- There are no empty collections. `DifficultyLevel` records load into the difficulty bar. While they load, the bar shows "Loading difficulties…" and the board is already playable at Beginner. If the list is empty, the bar says "No difficulties available" and Beginner stays in play. If the load fails, the bar says "Couldn't load difficulties. Beginner is ready to play." and the bar offers a "Try again" button.
- Flags can be placed before the first reveal. The timer and the status stay at ready.

### 2. Primary Navigation & View Structure
There is one view, the Board, with no tabs or routes. From top to bottom it holds:
1. Difficulty bar: one choice per `DifficultyLevel.name`, with a tick on the current one.
2. Header panel: mine counter, face button, timer.
3. Grid, sized by `DifficultyLevel.width` × `DifficultyLevel.height`, with `DifficultyLevel.mine_count` mines.

Win and loss are shown on the face and on the board, not in a separate screen or modal.

### 3. Workflow Prerequisites & Form Ergonomics
- There are no forms and no text inputs.
- Nothing is gated, so nothing is disabled. The first reveal is always allowed.
- Cells must not be locked without explanation. After a win or loss, a quiet status line under the grid says why clicks do nothing: "Round over. Press the face to play again."
- Board controls use the mouse (left click, right click, hold) and touch (tap, long-press). Cells are at least 24px, and larger on touch.
- The grid scrolls horizontally on narrow screens for Expert. The context menu is suppressed on the grid.

### 4. Human Copy & Action Labeling
- Difficulty choices: `DifficultyLevel.name` (Beginner, Intermediate, Expert). The current one carries a tick (✓).
- The face button has an accessible label that matches its state: "New game" at rest, "Playing", "You won", "You lost".
- Counter label: "Mines left". Timer label: "Seconds". Both are for screen readers only.
- Status line, shown only after the round ends: "You won! Press the face to play again." / "Boom. Press the face to play again."
- Cell labels for screen readers: "Hidden", "Flagged", "Empty", "1 mine nearby" and so on, "Mine", "Triggered mine", "Wrong flag".
- The wording is the same everywhere: "new game" for the face, and the difficulty name for the choices.

### 5. Contextual Action Placement
- Reveal, flag and chord happen only on cells.
- New game is the face button, in the header beside the counter and timer.
- Changing difficulty happens in the bar directly above the header. Choosing one starts a fresh ready round at that size.
- There are no global toolbars, settings or other surfaces.

### 6. Visual Direction
- **Feel**: classic Windows Minesweeper. The window is grey and beveled, with sharp corners and a pixel-crisp look.
- **Palette**:
  - Page: `gray-400`, close to #c0c0c0.
  - Surface: #c0c0c0.
  - Bevels: white highlight, `gray-500` shadow.
  - Text: black.
  - Counter and timer digits: `red-600` on black.
  - Accent: the yellow of the face button.
  - Number colours: 1 blue, 2 green, 3 red, 4 dark blue, 5 maroon, 6 teal, 7 black, 8 gray.
  - Triggered mine: `red-600`.
- **Type**: `font-mono` for the seven-segment-style digits and the numbers. `font-sans` for the difficulty bar. Bold digits. There is no headline.
- **First screen**: the window sits centred. The difficulty bar is on top, the header below it, and the grid below that, all as one framed unit of one width.
- **Form of the main view**: a classic minesweeper grid. All cells are identical squares, fixed in size whatever they hold, and the grid keeps the proportions of its width and height. A hidden cell is raised, and a revealed cell is flat.
- **Shape and rhythm**: 0 radius, 2–3px bevels, 6px padding, dense.
- LAYOUT columns=9 rows=9
- TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#ffeb00 on_accent=#000000 heading=mono