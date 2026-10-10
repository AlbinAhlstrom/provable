### 1. Default Landing & Cold-Start Behavior
- The first visit opens directly on the playable board at Beginner (9×9, 10 mines); no splash, no intro text.
- The round is in ready state: all 81 cells hidden, mine counter shows 10, timer shows 000, face smiling.
- No mines are placed until the first reveal, so the board is never shown with a mine layout before play.
- No "shown to audience" entities are loaded; DifficultyLevel presets are fixed in the page, so no loading or error state is needed.
- Board never appears empty: the hidden grid is the first-visit content itself.
- Ready round with no reveal yet: header shows counter, face and timer only; no status line.
- A failed or missing round creation falls back to a fresh Beginner ready round, with no error text.

### 2. Primary Navigation & View Structure
- One view only: the game board. No tabs, menus, or separate pages.
- Difficulty bar sits above the header, showing "Beginner", "Intermediate", "Expert" as the three choices.
- Current difficulty carries a tick mark; selecting another starts a new ready round at that size.
- Face button restarts at the current difficulty; no other navigation exists.
- Selecting the already-current difficulty restarts the round as well, matching the face button.
- No accounts, leaderboards, settings or admin surfaces are shown.

### 3. Workflow Prerequisites & Form Ergonomics
- No form fields exist; all inputs are board clicks, taps, and difficulty choices.
- Flagging before the first reveal is allowed and does not start the timer; no prompt is needed.
- Revealed cells ignore left click and right click; they do nothing and show no message.
- Flagged cells ignore left click; the flag stays in place with no message.
- Chord on a number whose flag count differs from its number does nothing silently.
- After win or loss, all cell clicks and flag actions are ignored; the face and counter convey the outcome.
- Face button and difficulty bar stay enabled at all times, including after win or loss.

### 4. Human Copy & Action Labeling
**Seen**
- "Beginner", "Intermediate", "Expert" — difficulty bar, above header.
- Mine counter digits and timer digits only; no text labels beside them.
- No headings, captions, instructions, or status sentences are shown on the page.
- Face button has no visible text; it is an icon only.

**Spoken only**
- Difficulty buttons: "Beginner difficulty", "Intermediate difficulty", "Expert difficulty"; current one adds "selected".
- Face button: "New game".
- Mine counter: "Mines left: [n]" where n may be negative.
- Timer: "Time: [n] seconds".
- Hidden cell: "Hidden cell, row [r], column [c]".
- Flagged cell: "Flagged cell, row [r], column [c]".
- Revealed empty cell: "Empty cell, row [r], column [c]".
- Revealed number cell: "[n] adjacent mines, row [r], column [c]".
- Mine cell: "Mine".
- Triggered mine: "Triggered mine".
- Wrongly flagged cell: "Wrongly flagged cell".
- Face states: "Game in progress", "Game won", "Game lost".

### 5. Contextual Action Placement
- Difficulty bar sits directly above the header, spanning the window width.
- Face button sits centred in the header, the only restart control, with the board directly below.
- Flag and reveal actions sit on each cell itself: left click or tap reveals, right click or long press flags.
- Chord action sits on each revealed number cell: click it to reveal its neighbours when flags match.
- Mine counter sits left of the header and timer sits right, each adjacent to the face button.

### 6. Visual Direction
- **Feel**: Classic Windows Minesweeper: grey, beveled, the familiar 1990s desktop game window.
- **Palette**: Page background #c0c0c0; window and header surface #c0c0c0; text #000000 for counters and default digits; accent #000080 for focus and selection ticks; hidden cell face #c0c0c0 with white (#ffffff) top-left and #808080 bottom-right bevel; flat revealed cell #c0c0c0 with #808080 hairline outline; number colours: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080; flag red #ff0000 on black base #000000; counter and timer boxes background #000000 with red #ff0000 seven-segment digits; triggered mine background #ff0000; face yellow #ffff00 with black features; mines black #000000 spiky.
- **Type**: `font-mono` for counter and timer digits (bold, 28px); `font-sans` for difficulty labels (13px, regular); no headings exist.
- **First screen**: The playable window centred on the grey page, with difficulty bar above the header and the 9×9 hidden grid below; nothing written above it.
- **Form of the main view**: Classic Minesweeper window: one bevelled frame containing the difficulty bar, header panel and grid, drawn as one unit. Cells are fixed 24px squares; the header is 40px tall; the grid is fully sized to the chosen difficulty and centred. Hidden cells look raised; revealed cells look flat; repeated cells are all alike regardless of content. On narrower screens the window keeps its pixel size and scrolls horizontally rather than reflowing.
- **Shape and rhythm**: Square corners (0 radius); 2px bevel borders (white and #808080 for raised, inverted for sunken); 12px padding around the window; 8px gap between difficulty bar, header and grid; compact, dense layout.

LAYOUT columns=9 rows=9

TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#000080 on_accent=#ffffff heading=sans