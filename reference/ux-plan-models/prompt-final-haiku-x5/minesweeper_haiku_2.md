### 1. Default Landing & Cold-Start Behavior
- On arrival, the single game view opens at once: Beginner selected, a ready round, the full hidden board, counter at 010, timer at 000, smiling face.
- No intro, splash or instructions appear above the game.
- DifficultyLevel records (name, width, height, mine_count) load from the API and fill the difficulty bar.
- While levels load, the three difficulty labels show with no tick, and the board area is an empty sunken frame.
- If the load fails, the board area shows "Could not load levels." and the difficulty bar stays disabled.
- If no levels are returned, the board area shows "No levels available."
- Before the first reveal, the board shows all hidden cells, and the timer reads 000.

### 2. Primary Navigation & View Structure
- The product is one view: the game window. It has no tabs, menus or secondary pages.
- Order within the window, top to bottom: difficulty bar, header panel (mine counter, face button, timer), grid.
- Difficulty bar sits above the header, directly over the window's top edge, as the specification places it.
- Choosing a difficulty replaces the current round with a new ready round at that size.
- No separate result page exists; win and loss appear on the board and face.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; all input is by clicking, tapping, holding or right-clicking cells and buttons.
- Flagging is available before the first reveal; the timer does not start until the first reveal.
- The mine counter and timer are visible from the first screen, so no step is hidden behind another.
- A chord on a number cell whose flag count differs from its number does nothing, with no message.
- Clicks on flagged cells, revealed cells (without chord) and any cell after win or loss do nothing, with no message.
- Actions after a loss or win are ignored silently; the face and board already show the outcome.
- Hold on a hidden cell shows the pressed look at once; the cell reveals only on release.

### 4. Human Copy & Action Labeling
Seen:
- "Beginner" — difficulty bar, first choice.
- "Intermediate" — difficulty bar, second choice.
- "Expert" — difficulty bar, third choice.
- "Could not load levels." — board area, when the level load fails.
- "No levels available." — board area, when the level list is empty.
- Mine counter and timer show digits only; no words accompany them.

Spoken only (screen reader names):
- Difficulty choice: "Beginner, 9 by 9, 10 mines", "Intermediate, 16 by 16, 40 mines", "Expert, 30 by 16, 99 mines"; the chosen one also reads "selected".
- Face button: "New game".
- Mine counter: "Mines minus flags: [number]".
- Timer: "Seconds elapsed: [number]".
- Hidden cell: "Hidden, column [n], row [m]".
- Flagged cell: "Flagged, column [n], row [m]".
- Revealed number cell: "[n] adjacent mines, column [n], row [m]".
- Revealed empty cell: "Empty, column [n], row [m]".
- Mine cell: "Mine".
- Triggered mine: "Mine, triggered".
- Wrongly flagged cell: "Wrongly flagged".

### 5. Contextual Action Placement
- Difficulty choices sit in the bar above the header, the only place to change size.
- The face button sits centred in the header and is the only control that restarts the current difficulty.
- Mine counter and timer sit either side of the face button, showing status beside the control that restarts.
- Reveal, flag and chord actions sit on the cells themselves; no separate toolbar exists.
- Flag placement and removal use the right button or long-press on the cell it changes.

### 6. Visual Direction

- **Feel**: Classic Windows Minesweeper: a grey, beveled utility window, flat and tactile, with red digits on black.

- **Palette**: Page background and window surface #c0c0c0; bevel highlight #ffffff; bevel shadow #808080; darkest bevel edge #000000; text #000000; accent (face and selected tick) #000080; on accent #ffffff. Counter and timer box #000000; counter and timer digits #ff0000; face fill #ffff00; face outline #000000; number 1 #0000ff; number 2 #008000; number 3 #ff0000; number 4 #000080; number 5 #800000; number 6 #008080; number 7 #000000; number 8 #808080; flag #ff0000; flag base #000000; mine #000000; triggered mine background #ff0000; cross over wrong flag #ff0000; revealed cell outline #808080.

- **Type**: Sans family for labels (`font-sans`, bold 12px); mono family for digits (`font-mono`, bold). Largest text on the first screen is the counter and timer digits, 28px bold.

- **First screen**: The game window fills the centre of the grey page, with difficulty bar, header and board already visible. No headline, photograph or introduction sits above it. The first screen opens on a Beginner board of hidden cells.

- **Form of the main view**: The familiar Minesweeper form: a rectangular grid of square cells inside a sunken frame, with a header strip above. Cells are 24px square, all alike, and the grid keeps its fixed proportions for each difficulty. The window is one unit with a fixed width fitted to its board. Hidden cells look raised; empty revealed cells look flat and blank. On a screen narrower than the window, cells step down to 16px minimum; below that the sunken grid scrolls horizontally, and the header stays fixed to the window.

- **Shape and rhythm**: Square corners, no rounding. Bevels are 2px: white top and left, dark grey bottom and right. Gaps: 4px between the difficulty bar, header and grid. Density is high, matching the classic game.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans