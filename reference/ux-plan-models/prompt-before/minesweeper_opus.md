### 1. Default Landing & Cold-Start Behavior
- First visit opens straight onto a ready Beginner board: a 9×9 grid of hidden cells, counter 010, timer 000 and a smiling face. There is no splash screen and no intro text.
- No game history exists, so there is nothing that could be empty. The board itself is the default view.
- DifficultyLevel records fill the difficulty bar. Each item shows `DifficultyLevel.name`, and its size comes from `width`, `height` and `mine_count`.
  - **Loading**: the bar shows "Loading levels…" and a Beginner 9×9/10 board stays playable.
  - **Empty list**: the bar shows "Only Beginner is available right now."
  - **Failed load**: the bar shows "Levels couldn't load — playing Beginner." with a "Retry" link.

### 2. Primary Navigation & View Structure
There is one view, called **Minesweeper**, drawn as a single window. Top to bottom it holds:
1. **Difficulty bar**: one menu item per DifficultyLevel record. The current item carries a ✓.
2. **Header panel**: mine counter, face button, timer.
3. **Grid**.

There are no other tabs, pages or settings.

### 3. Workflow Prerequisites & Form Ergonomics
- There are no forms or inputs. Every move is a pointer or touch action.
- **Reveal**:
  - Left-click or tap a hidden cell.
  - Hold to press, and the face turns shocked. Releasing reveals the cell.
  - Long-press (500 ms) places or removes a flag.
- **Flag**: right-click on desktop. Long-press on touch is suppressed until 500 ms have passed, so a tap never flags by mistake.
- **Chord**: click a revealed number cell. It acts only when the adjacent flags equal the cell's number.
- **Ignored actions**: ignored clicks (a flagged cell, a revealed cell, a finished round) give no feedback. This matches the classic game, and nothing looks disabled.
- **New round**: there is no prerequisite. The face button and the difficulty items always work.
- **Context menu**: the browser's context menu is suppressed on the grid only.

### 4. Human Copy & Action Labeling
- **Visible text**: only the difficulty names. The digits and the face carry all game state.
- **Accessible labels**:
  - Face button: "New game", announced along with the state ("Won", "Lost", "Playing").
  - Counter: "Mines left: N".
  - Timer: "Seconds: N".
  - Cells: "Hidden", "Flagged", "3 mines nearby", "Empty", "Mine", "Wrong flag".
- **Live region**: announces "You won in N seconds." or "You hit a mine." at the end of a round.

### 5. Contextual Action Placement
- The restart control lives in the face button, centred in the header and directly above the grid.
- The difficulty bar sits on the window frame, as in the classic menu.
- No controls sit outside the window.

### 6. Visual Direction
- **Feel**: classic Windows 95 Minesweeper, recognised at a glance.
- **Palette**:

| Role | Colour |
|---|---|
| Page and surface | #c0c0c0 (Tailwind neutral-400 tone) |
| Bevel highlights | white |
| Bevel shadows | #808080 |
| Text | black |
| Counter and timer | red-600 digits on black |
| Accent (face) | yellow-400 |
| Triggered-mine background | red-600 |

  Numbers use their classic colours: 1 blue, 2 green, 3 red, 4 navy, 5 maroon, 6 teal, 7 black, 8 grey.
- **Type**:
  - Difficulty bar: `font-sans`, text-sm.
  - Cell numbers: `font-sans` bold.
  - Counter and timer: `font-mono` seven-segment style, text-2xl and bold.
  - There is no headline.
- **First screen**: the centred window is the only thing on the page, and it is playable immediately.
- **Form of the main view**:
  - One beveled window holds the bar, header and grid at one shared width.
  - Cells are fixed 24px squares (28px on touch screens), all alike.
  - The grid keeps the preset's proportions: Beginner 9×9, Intermediate 16×16, Expert 30×16.
  - On narrow screens the Expert grid scrolls horizontally inside its sunken frame rather than shrinking the cells.
- **Shape and rhythm**:
  - No corner radius and no soft shadows.
  - 3px two-tone bevels, raised for the window and buttons, sunken for the header and grid.
  - 6px padding between parts.
  - Dense layout.

LAYOUT columns=9 rows=9
TOKENS background=#c0c0c0 surface=#c0c0c0 text=#000000 accent=#facc15 on_accent=#000000 heading=sans