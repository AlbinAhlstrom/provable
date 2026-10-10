### 1. Default Landing & Cold-Start Behavior
- The page opens on the single game view: a Beginner board in the ready state, with every cell a hidden cell.
- The header shows the mine counter at "010", the face button smiling and the timer at "000".
- The difficulty bar is filled by DifficultyLevel records, one choice per record, labelled `DifficultyLevel.name`.
- The tick sits on the record whose name is Beginner.
- Board size and mine total come from `DifficultyLevel.width`, `DifficultyLevel.height` and `DifficultyLevel.mine_count` of the ticked record.
- While the records load, the difficulty bar shows "Loading levels…" in grey.
- During loading, the board still shows Beginner 9×9 with 10 mines, so play can begin at once.
- If the load returns no records, the bar shows "No difficulty levels available". The Beginner 9×9 board stays playable.
- If the load fails, the bar shows "Couldn't load difficulty levels." followed by a "Retry" text button. The Beginner board stays playable.
- Nothing else on the page can be empty: the board always exists, and an unrevealed board is shown entirely as hidden cells.

### 2. Primary Navigation & View Structure
- The product is one view: the Minesweeper window. It has no tabs, routes or pages.
- From top to bottom the window holds the difficulty bar, the header panel and the grid.

### 3. Workflow Prerequisites & Form Ergonomics
- No step requires an earlier one. Revealing, flagging and restarting are all available from the first visit.
- Flagging in the ready state places the flag. The timer stays at "000" and the round stays ready.
- Clicking a flagged cell does nothing: no message, no sound, no visual change.
- Clicking or right-clicking a revealed cell does nothing, except chording when its adjacent flags equal its number.
- Chording when the flag count differs from the number does nothing, silently.
- After a win or loss, cell clicks and long-presses do nothing. The face button and difficulty bar still work.
- A long-press of 500ms on touch toggles the flag. A shorter tap reveals the cell.
- Moving the pointer off a held cell before release cancels the reveal. The cell pops back up and the face smiles again.
- The product has no forms or text fields.

### 4. Human Copy & Action Labeling
**Seen**
- "Beginner", "Intermediate", "Expert": the difficulty bar labels, taken from `DifficultyLevel.name`, with "✓" before the current one.
- "Loading levels…": in the difficulty bar while the records load.
- "No difficulty levels available": in the difficulty bar when the load returns no records.
- "Couldn't load difficulty levels.": in the difficulty bar on a failed load.
- "Retry": a text button beside the failure message.
- Mine counter digits, for example "010" or "-03": in the left header box.
- Timer digits, for example "000" to "999": in the right header box.
- Cell digits "1" to "8": on revealed number cells.
- Win and loss are told by the face, the flags and the mines alone. No sentence announces them.

**Spoken only**
- Face button: "New game". Its state is added as "smiling", "shocked", "won" or "lost".
- Mine counter: "Mines left: 10".
- Timer: "Seconds: 0".
- Grid: "Minefield, 9 by 9".
- Hidden cell: "Hidden, row 3, column 4".
- Flagged cell: "Flagged, row 3, column 4".
- Revealed cells, by kind:
  - "Empty, row 3, column 4"
  - "2, row 3, column 4"
  - "Mine"
  - "Triggered mine"
  - "Wrong flag"
- Difficulty bar: "Difficulty". The current choice is marked selected.

### 5. Contextual Action Placement
- Revealing, flagging and chording happen on the cell itself, in the grid.
- Starting a new round at the current difficulty is the face button, centred in the header panel.
- Choosing a difficulty is done in the difficulty bar above the header. A click starts a new round at that size.
- "Retry" sits immediately right of the failure message in the difficulty bar.
- The right-click context menu is suppressed over the grid.

### 6. Visual Direction
**Feel**: Classic Windows Minesweeper. The look is a grey, beveled, pixel-crisp window, with no modern polish.

**Palette**
- Page background: #c0c0c0.
- Window surface: #c0c0c0.
- Text: #000000.
- Accent (the face button's face): #ffff00, with a #000000 outline and features.
- Bevel light: #ffffff. Bevel dark: #808080.
- Revealed cell fill: #c0c0c0, with a 1px #808080 outline.
- Counter and timer boxes: #000000. Lit segments: #ff0000. Unlit segments: #400000.
- Number colours:
  - 1 #0000ff
  - 2 #008000
  - 3 #ff0000
  - 4 #000080
  - 5 #800000
  - 6 #008080
  - 7 #000000
  - 8 #808080
- Flag: red #ff0000 on a #000000 base and pole.
- Mine: #000000 with a #ffffff highlight dot.
- Triggered mine background: #ff0000.
- Wrong-flag cross: #ff0000.
- Difficulty tick and labels: #000000. Loading and empty notes: #404040.

**Type**
- Everything uses `font-sans`.
- Difficulty bar text: 12px, regular weight.
- Cell digits: 16px, bold.
- The largest element is the counter and timer digits, drawn as seven-segment numerals 26px tall in red. `font-mono` bold is the fallback.

**First screen**
- The window sits centred horizontally, 24px from the top. It opens with the difficulty bar, header and Beginner grid, ready to play.
- There is no title or introduction above the window.

**Form of the main view**
- The view is the classic Minesweeper window, built as one framed unit of one width. The header spans the grid's width exactly.
- Cells are fixed squares of 24×24px, all alike whatever they hold. Hidden cells have a 3px bevel: white top-left, #808080 bottom-right.
- Counter and timer boxes are 41×26px. The face button is 26×26px, with a 2px bevel that inverts when pressed.
- Expert is 720px wide plus the frame. On screens narrower than the window, the grid scrolls horizontally inside the frame and cells never shrink.

**Shape and rhythm**
- No corner radius anywhere. Depth comes only from bevels; there are no drop shadows.
- The outer window bevel is 3px. The header panel and grid are each sunken with a 2px inverted bevel.
- Window padding is 6px. There is a 6px gap between the bar, header and grid.
- The header is 8px tall above and below its contents. Spacing is dense and tight, like the original.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#ffff00 on_accent=#000000 heading=sans