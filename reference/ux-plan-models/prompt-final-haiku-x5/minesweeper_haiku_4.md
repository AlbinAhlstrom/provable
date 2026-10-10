### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the playable board: a Beginner 9×9 round in the ready state, no reveal yet.
- Header shows mine counter "010", face button smiling, timer "000"; no message above the board.
- No cells are revealed or flagged on arrival; mines are not placed until the first reveal.
- The difficulty bar shows Beginner with its tick already set.
- No loading state is needed: the board is generated in the browser from the DifficultyLevel presets.
- DifficultyLevel records (name, width, height, mine_count) load first; while they load, the difficulty bar shows "Loading levels…" in place of the three choices.
- If DifficultyLevel records fail to load, the difficulty bar shows "Levels could not load." and the board stays playable at Beginner from the fallback preset.
- Empty difficulty list: the bar shows "No levels available." and the board stays on its current size.
- Game records are created per round, so no empty-list state applies to the board.

### 2. Primary Navigation & View Structure
- One view only: the game screen. No tabs, menus, accounts or other pages.
- Order on screen, top to bottom: difficulty bar, header panel, grid.
- Difficulty bar holds "Beginner", "Intermediate", "Expert" in that order, each a button; the current one carries a tick.
- Choosing a difficulty starts a new ready round at that size immediately, with no confirmation.
- Face button restarts at the current difficulty; there is no separate restart control.
- No result page after win or loss; the outcome is shown on the board and face only.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; every input is a click, tap, hold or long-press on the board or bar.
- Timer waits for the first reveal; flagging before it does not start the timer, and no hint is needed.
- Chord on a revealed number cell is allowed only when its flag count matches its number; otherwise the click does nothing.
- Clicks on flagged cells, revealed cells (except chord), and any cell after win or loss do nothing, with no message.
- Flag removal is by right-click or long-press on a flagged cell.
- Flags are unlimited; the counter may go negative and is shown as is.

### 4. Human Copy & Action Labeling
Seen:
- "Beginner" — difficulty bar, top left choice.
- "Intermediate" — difficulty bar, middle choice.
- "Expert" — difficulty bar, right choice.
- "Loading levels…" — difficulty bar, while DifficultyLevel loads.
- "Levels could not load." — difficulty bar, on failed load.
- "No levels available." — difficulty bar, when the list is empty.
- No other visible text: counter, timer and face are read as numbers and images.

Spoken only:
- "Difficulty: Beginner, selected" (and the same pattern for the other two, with "selected" only on the current one) — difficulty buttons.
- "New game" — face button.
- "Mines remaining" — mine counter.
- "Elapsed seconds" — timer.
- "Hidden cell, row R column C" / "Flagged cell, row R column C" / "Revealed cell, row R column C, N adjacent mines" / "Mine" / "Empty revealed cell, row R column C" — each grid cell.

### 5. Contextual Action Placement
- Difficulty choices sit above the header, on the window's top edge, where a player expects them.
- Face button sits centred in the header, the only restart control.
- Mine counter sits left in the header, timer right, each beside the face they frame.
- Reveal, flag, chord and flag removal act on the cell that is clicked; no separate toolbar.
- Win and loss states are shown on the face and grid, adjacent to the cells they change.

### 6. Visual Direction

- **Feel**: classic Windows Minesweeper: grey, beveled, square-celled, unfussy.
- **Palette**: page background #c0c0c0 (flat mid-grey); window surface #c0c0c0; text #000000; accent #000080 for the difficulty tick and focus outlines. Hidden-cell bevel white #ffffff top-left and #808080 bottom-right. Counter and timer boxes background #000000 with digits #ff0000. Revealed cell background #c0c0c0 with outline #808080. Number colours: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080. Flag base #000000 with flag #ff0000. Mine #000000 on flat grey. Triggered mine background #ff0000. Wrong flag red cross #ff0000. Face yellow #ffff00 with black features.
- **Type**: sans for body and labels; mono-style digits for counter and timer (`font-mono`); largest text on first screen is the counter/timer digits at 24px bold. Difficulty labels 14px regular.
- **First screen**: the playable board, centred on the grey page, with the difficulty bar on top of the window and the header and grid below. Nothing written above it; the window is the whole composition.
- **Form of the main view**: classic Minesweeper form: a single window framed by a raised bevel, header panel above a square grid. Cells are fixed 24px×24px squares, all alike, the grid keeps its natural proportions and is centred. On a screen narrower than the window, the grid scrolls horizontally inside its sunken frame and the window keeps its width.
- **Shape and rhythm**: square corners (0 radius); 2px raised bevel on the window, hidden cells and face; 2px sunken bevel on header panel and grid; 8px spacing between difficulty bar, header and grid; dense, no shadows.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans