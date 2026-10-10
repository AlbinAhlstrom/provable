### 1. Default Landing & Cold-Start Behavior
- The first screen is the playable board at Beginner (9×9, 10 mines), in ready state, with no reveal yet.
- The mine counter reads 010, the timer reads 000, and the face is smiling.
- No splash, intro text, or sign-up; the game is usable immediately.
- No entity is loaded from an API at start; the difficulty presets are fixed in the page.
- Difficulty records (DifficultyLevel) are shown in the difficulty bar with name, width, height and mine count; while loading, the bar shows three disabled labels.
- If DifficultyLevel records fail to load, the bar shows "Difficulties unavailable" and the Beginner board still plays.
- No mines are placed until the first reveal; the board is blank hidden cells before then.
- Board state is not persisted; a page reload starts a fresh ready round at Beginner.

### 2. Primary Navigation & View Structure
- One view only: the game window. No tabs, menus, or separate pages.
- Difficulty bar sits above the header panel, containing "Beginner", "Intermediate", "Expert".
- The current difficulty carries a tick mark beside its name.
- Header panel holds mine counter (left), face button (centre), timer (right), in that order.
- Grid sits below the header inside the sunken area.
- Choosing a difficulty or pressing the face button starts a new ready round at that size; no confirmation.
- A finished round stays on screen (won or lost) until the player starts another round.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; all input is by clicking cells, the face button, or difficulty labels.
- Before the first reveal, flagging is allowed and the timer stays at 000 until a reveal.
- Flags can be placed in a ready round without starting the timer, so no prerequisite message is needed.
- Clicking a flagged cell does nothing; no message is shown.
- Clicking or right-clicking a revealed cell does nothing, except chording on a number cell.
- Chording with a flag count differing from the number does nothing; no message is shown.
- Clicks after win or loss do nothing; the frozen board is the message.
- Revealing a mine ends the round as lost immediately; no confirmation is asked.

### 4. Human Copy & Action Labeling
**Seen:**
- "Beginner", "Intermediate", "Expert" — difficulty bar, labels beside the header.
- "Difficulties unavailable" — difficulty bar, only when DifficultyLevel fails to load.
- "Loading difficulties…" — difficulty bar, while DifficultyLevel loads.
- Face button has no text; its expressions carry the state.
- Counter and timer show digits only; no captions.
- No other text is shown: the board, counter, timer and face already tell the player what happened.

**Spoken only (screen reader names):**
- Face button: "New game" (ready, in progress), "Won" (after win), "Lost" (after loss).
- Difficulty items: "Beginner, 9 by 9, 10 mines", "Intermediate, 16 by 16, 40 mines", "Expert, 30 by 16, 99 mines"; current item adds "current".
- Hidden cell: "Hidden cell, row R, column C".
- Flagged cell: "Flagged cell, row R, column C".
- Revealed empty cell: "Empty, row R, column C".
- Number cell: "Number N, row R, column C".
- Mine cell: "Mine, row R, column C"; triggered: "Triggered mine"; wrongly flagged: "Wrong flag".
- Mine counter: "Mines left N"; timer: "N seconds".

### 5. Contextual Action Placement
- Difficulty choice sits in the bar directly above the board it resizes.
- New-round action is the face button in the header, centred over the grid it restarts.
- Reveal, flag and chord actions sit on the cell itself; no separate toolbar.
- Counter and timer sit in the header beside the face, read-only.
- Nothing is placed outside the window.

### 6. Visual Direction
- **Feel**: Classic Windows Minesweeper: grey, beveled, utilitarian, and instantly familiar.
- **Palette**: Page background #c0c0c0 (flat mid-grey, as specified); surface #c0c0c0 for window and header; text #000000; accent #000080 for the current difficulty tick and focus outline. Hidden-cell bevel: white #ffffff top-left, #808080 bottom-right, #000000 outer edge. Revealed cell and sunken panels: #c0c0c0 fill with #808080 outline. Digit colours: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080. Counter and timer box: #000000 with digits #ff0000. Flag: #ff0000 on #000000 base. Triggered mine background: #ff0000. Face fill: #ffff00 with #000000 features.
- **Type**: Sans for body and labels, Tailwind font-mono for the counter and timer digits (seven-segment look), font-sans for difficulty labels; the largest text on the first screen is the timer and counter digits at 28px, bold.
- **First screen**: The difficulty bar and the full Beginner window, centred on the grey page, with the header and grid already visible. No headline, no intro, no photographs.
- **Form of the main view**: A Minesweeper board, one window unit of fixed width, with a header panel and a sunken square-celled grid. Cells are fixed 24px squares for all difficulties; the grid is 9×9 at Beginner (216px square), 16×16 at Intermediate, 30×16 at Expert, with no scaling. The window is one frame with the difficulty bar on top. A hidden cell is a raised grey square; a revealed cell is flat grey with a thin outline. On screens narrower than the window, the whole window scrolls horizontally rather than shrinking cells.
- **Shape and rhythm**: Zero corner radius everywhere; bevels are 2px. Spacing inside the window is 4px between header and grid, 8px padding in the header. No shadows, no gradients. Dense, compact layout with no whitespace beyond the window padding.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans