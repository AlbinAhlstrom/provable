### 1. Default Landing & Cold-Start Behavior

- The only view is the game panel, opening directly on a ready round at the first loaded preset (Beginner), with no intro text above it.
- Opening board: all cells hidden, counter shows the preset's mine_count as "010", timer "000", face smiling.
- DifficultyPreset.name fills the three difficulty buttons, in record order, with the current preset underlined.
- DifficultyPreset.rows and columns set the board size; mine_count sets the counter at round start.
- While presets load: the difficulty row shows three disabled buttons labelled "Loading levels", and the board area is empty sunken frame.
- Empty presets list: difficulty row shows "No difficulty levels are available." and no board is drawn.
- Failed presets load: difficulty row shows "Levels could not load." with a "Try again" button beside it.
- Round cells have no records: the board is created in memory from the selected preset, so it never waits on the API.

### 2. Primary Navigation & View Structure

- One view only; there is no navigation, tabs, menu or second page.
- Order top to bottom: difficulty selector row, then the game panel holding header strip and board.
- Header strip order left to right: mine counter, face button, timer.
- Board sits directly below the header strip inside the same panel.
- Selecting a difficulty replaces the round in place; the page does not change view.

### 3. Workflow Prerequisites & Form Ergonomics

- No prerequisite steps: the first left-click on any hidden cell is always allowed and places mines.
- Chording is available only on revealed numbers; no message is shown when a chord is ignored.
- Flagging is available from the start; no step must precede it.
- Reveals and flags after a win or loss do nothing and show no message; the face and counter carry the outcome.
- Clicking a flagged or revealed cell does nothing, with no message.
- No form fields exist; the product takes no typed input.

### 4. Human Copy & Action Labeling

Seen text:
- "Beginner", "Intermediate", "Expert" — difficulty buttons, from DifficultyPreset.name, in the difficulty row above the panel.
- "Loading levels" — disabled difficulty buttons while presets load.
- "No difficulty levels are available." — difficulty row when the list is empty.
- "Levels could not load." — difficulty row on failed load.
- "Try again" — button beside the load error; reloads presets.

Spoken only (screen reader names, no visible text):
- "Mines left" — mine counter.
- "Seconds elapsed" — timer.
- "New round" — face button.
- "Hidden cell, row R, column C" — hidden cell.
- "Flagged cell, row R, column C" — flagged cell.
- "Revealed, N adjacent mines" — numbered cell; "Revealed, empty" for zero cells.
- "Mine" — revealed mine cell.
- "Difficulty: [name]" — selected difficulty button, with pressed state announced.

### 5. Contextual Action Placement

- Difficulty buttons sit above the panel, the only place a difficulty is chosen.
- The face button sits centred in the header strip and is the only way to abandon a round.
- Reveal, flag and chord actions sit on the cell they change; no separate action bar exists.
- Right-click or long press on a hidden or flagged cell toggles its flag in place.
- Win and loss outcome is shown by the face and the board, not by a message beside them.

### 6. Visual Direction

- **Feel:** Classic Windows Minesweeper: a grey, beveled utility window with sharp corners and a plain, dense, game-board character.
- **Palette:** Page and panel grey #c0c0c0; revealed cells #c0c0c0; text #000000; accent #000080 for the underlined current difficulty and focus rings; bevel light #ffffff, bevel dark #808080; counter and timer box #000000; LED digits #ff0000; face yellow #ffff00; flag red #ff0000 with black pole and base; mine black #000000 with white highlight #ffffff; clicked mine background #ff0000; number 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080.
- **Type:** Sans family (font-sans) for labels and buttons, 14px bold; numerals in the board and digits use 16px bold; no display type. Largest text on screen is 16px.
- **First screen:** The game panel, centred on grey, with difficulty row above, header strip with counter "010", face and timer "000", and a 9×9 grid of raised hidden cells beneath. No headline, no photograph, no text beyond the difficulty buttons.
- **Form of the main view:** The familiar Minesweeper form: one panel of one width, a header strip above a square grid. Each cell is 24px square, fixed, with no scaling; the Expert board is 720px wide. Hidden cells are raised with 2px light top-left and dark bottom-right bevels; revealed cells are flat with a 1px #808080 border. On screens narrower than the panel, the panel keeps its size and scrolls horizontally inside the page.
- **Shape and rhythm:** Zero corner radius everywhere; 2px bevels, no drop shadows; 8px panel padding; 8px gap between difficulty row and panel; compact, dense spacing with no decorative elements.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans