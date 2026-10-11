### 1. Default Landing & Cold-Start Behavior
The game opens directly on a ready round at Beginner (9×9, 10 mines), the last difficulty chosen on this device or Beginner by default. No welcome screen, no empty state: the board is the first thing seen. The header shows the mine counter at 010, a smiling face and the timer at 000. A short hint line beneath the difficulty bar reads "Click any square to start. The first click is always safe." It disappears once the round is in progress.

### 2. Primary Navigation & View Structure
There is one view: the game. Its parts, top to bottom:
- **Difficulty bar**: "Beginner", "Intermediate", "Expert", with a tick on the current choice.
- **Game frame**: one raised window containing the header panel and the grid.
- **Result line** (appears only after a round ends): "You cleared the board." or "Mine hit. Try again?"

No menus, tabs, accounts or secondary pages.

### 3. Workflow Prerequisites & Form Ergonomics
There are no forms and no gated actions. Every control is live from the first frame:
- Revealing a cell needs nothing beforehand; the first reveal places mines around it.
- Flagging is available before the first reveal; it does not start the timer.
- Chording a number cell is offered only when its flags match its number. When they do not, the cell gives no response, and the hint "Place flags around this number to chord it" appears on hover or long-press for a moment, so the action never looks broken.
- Once a round is won or lost, cells show no hover or press feedback, and the face button reads "New game" on hover, so the next step is obvious.

### 4. Human Copy & Action Labeling
- Difficulty labels: "Beginner", "Intermediate", "Expert" (each with its size shown on hover: "9 × 9, 10 mines").
- Face button tooltip: "New game".
- Mine counter and timer: unlabelled numerals, as in the classic game; the counter's accessible name is "Mines left".
- Result messages: "Cleared! All safe squares found." and "Boom. A mine was hit."
- Hover hint for a flagged cell: "Right-click or long-press to remove the flag."
- Cell accessible names state the cell's state plainly: "Hidden", "Flagged", "Empty", "2 nearby mines", "Mine".

### 5. Contextual Action Placement
All actions sit on or beside the board they affect. Difficulty choice sits directly above the header it resets. The face button sits inside the header, so restarting is always one click from the board. Result messages appear in the window's footer strip, under the grid, not in a global banner.

### 6. Visual Direction
**Feel**: Classic Windows Minesweeper, a grey beveled desk tool that rewards focus.

**Palette**: The page background is flat mid-grey, the window and header are light grey, and the text is near-black. The accent is the classic blue used for number 1 and the selected difficulty tick. Middle tones (400–600) are used for the grid's flat revealed cells, so both pale numbers and dark numerals read clearly on them. Mine counter and timer boxes are black with red digits.

**Type**: `font-mono` for the counter and timer digits, `font-sans` for labels. The first-screen headline is not used; the game's title is small, bold and sans, sized `text-sm`.

**First screen**: The game window centred on the grey page, with the difficulty bar above, the header panel and the grid below. Nothing sits above it but the difficulty bar.

**Form of the main view**: One object: a single window drawn as one unit of one width (grid width plus header padding), inside one raised frame. Cells are square and all equal in size; the grid keeps its natural proportions for each difficulty and grows with its column and row count, not with its content.

**Shape and rhythm**: Square corners (`rounded-none`). Raised bevels use white top-left and dark grey bottom-right borders; sunken areas invert them. Spacing is tight, `gap-1` inside the header and `p-2` around the window. Dense, like the original.

LAYOUT columns=30 rows=16

TOKENS background=#c0c0c0 surface=#d4d0c8 text=#1c1917 accent=#0000ff on_accent=#ffffff heading=sans