### 1. Default Landing & Cold-Start Behavior
- Arrival shows the Minesweeper window itself: difficulty bar, header panel and a Beginner 9×9 board in the ready state, with no introduction above it.
- Round state on arrival is ready: counter reads 010, timer 000, face smiling, all cells hidden, so the board is never empty.
- Difficulty bar is filled from DifficultyLevel records (`DifficultyLevel.name`, `.width`, `.height`, `.mine_count`); the tick marks the current one, Beginner at first.
- Loading DifficultyLevel: the bar shows "Loading…" in its place; the sunken header and a blank grid frame stay visible, and cells are not playable.
- No DifficultyLevel records: the bar shows "No difficulties available"; the board is not drawn and the face button stays inactive.
- Failed load: the bar shows "Couldn't load difficulties." with a "Try again" button beside it.
- Empty places: none besides the above. Hidden cells are the classic raised squares, and no hint text is added.

### 2. Primary Navigation & View Structure
- One view only: the game window. No tabs, menus, routes or other screens.
- The difficulty bar is the only navigation; it lists the `DifficultyLevel.name` records in stored order (Beginner, Intermediate, Expert).

### 3. Workflow Prerequisites & Form Ergonomics
- No step needs another done first: the player may flag or reveal in any order. The first reveal starts the timer; flagging before it does not.
- Ended round (won or lost): cell clicks, flags and chords do nothing and give no message; the face button and difficulty bar stay active.
- Flagged cell clicked, revealed cell clicked or flagged, and a chord with mismatched flags: silently do nothing.
- Ready round: chording is impossible because nothing is revealed.
- No form fields; there are no text inputs.

### 4. Human Copy & Action Labeling
- **Seen**: "Beginner", "Intermediate", "Expert" are the difficulty bar items, shown as `DifficultyLevel.name`.
- **Seen**: "Loading…" is the difficulty bar while it loads.
- **Seen**: "No difficulties available" appears in the difficulty bar when there are no records.
- **Seen**: "Couldn't load difficulties." and the button "Try again" appear in the difficulty bar when the load fails.
- **Seen**: the digits in the mine counter and timer, the cell numbers and the tick next to the current difficulty are signals, not sentences.
- No win or loss message is shown: the sunglasses face, the dead face, the revealed mines and the counter reading 000 are the message.
- **Spoken only**: "New game" for the face button; its state is announced as "Smiling", "Shocked", "Cool, you won" or "Dead, you lost".
- **Spoken only**: "Mines remaining" for the counter and "Seconds elapsed" for the timer, each with its value.
- **Spoken only**: "Difficulty" for the bar group; the current item is announced "selected".
- **Spoken only**: cell names are "Hidden cell, row R column C", "Flagged cell", "Revealed, N adjacent mines", "Revealed, empty", "Mine", "Triggered mine" and "Wrong flag".
- **Spoken only**: "Minefield" for the grid.

### 5. Contextual Action Placement
- Reveal, flag and chord happen on the cells themselves: left-click or tap, right-click or long-press, and left-click on a revealed number.
- The face button sits centred in the header and starts a new round at the current difficulty.
- Difficulty choices sit in the bar above the header and start a new round at the chosen size.
- "Try again" sits beside the failed-load message in the difficulty bar.

### 6. Visual Direction
- **Feel**: classic Windows Minesweeper, a grey beveled window with crisp 3D edges.
- **Palette**: page #c0c0c0; window and cell surface #c0c0c0; bevel light #ffffff; bevel dark #808080; text #000000; accent is the face button's yellow #ffff00 with outline #000000. Counter and timer box #000000 with digits #ff0000. Revealed cell #c0c0c0 with outline #808080. Numbers: 1 #0000ff, 2 #008000, 3 #ff0000, 4 #000080, 5 #800000, 6 #008080, 7 #000000, 8 #808080. Triggered mine background #ff0000. Mine #000000. Flag #ff0000 on base #000000. Wrong-flag cross #ff0000.
- **Type**: `font-mono` for headings and body. Digits in the counter and timer are seven-segment style, 36px tall. Cell numbers are bold 16px. The difficulty bar is 14px regular, with no larger text.
- **First screen**: the window is centred on the grey page. Inside it, top to bottom: the difficulty bar, the sunken header (counter left, face centre, timer right), then the sunken 9×9 grid. The tick sits before the current difficulty name.
- **Form of the main view**: one object, with the bar, header and grid inside a single 3px raised bevel frame of one width. Cells are all 24×24px, a fixed square grid. Hidden cells have a 3px bevel; revealed cells have a 1px #808080 outline. The face button is 40×40px. On a narrower screen the window keeps its size and scrolls horizontally rather than shrinking, since Expert is 720px wide.
- **Shape and rhythm**: 0px radii, bevel borders in place of shadows, 6px padding inside the window and header, 6px between parts. Dense and compact.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#ffff00 on_accent=#000000 heading=mono