# Minesweeper

## 1. People and their journey

**Player** (the only role). A person playing Minesweeper for fun.

- **Needs to see:** the board, how many mines are left to flag, how long the round has taken, and whether the round is still going, won or lost.
- **Decides:** which square to uncover, which square to flag, and which difficulty to play.
- **Path:**
  1. Opens the game and a Beginner board is ready.
  2. Optionally picks another difficulty.
  3. Clicks a first square, which is always safe.
  4. Uncovers and flags squares, using the numbers to deduce where the mines are.
  5. Either uncovers every safe square and wins, or uncovers a mine and loses.
  6. Clicks the face to play again.

## 2. How it looks

The game looks like classic Windows Minesweeper: a small grey bevelled window with a menu bar, a sunken top panel holding a red-digit mine counter, a smiley face button and a red-digit timer, and below it a sunken grid of raised grey squares.

- **Page background:** flat teal, with the game window centred on it.
- **Game window:** light grey (silver) with a raised bevel, white top-left edges and dark grey bottom-right edges, and a thin black outer border.
- **Menu bar:** a flat light grey strip across the window top with one item, "Game", in black text. While its list is open, the item is navy with white text.
- **Game menu list:** a raised light grey dropdown with black text. Its items are New, Beginner, Intermediate, Expert, Custom… and Marks (?).
- **Menu item states:** the hovered item is navy with white text. The current difficulty and Marks, when it is on, show a black check mark to the left.
- **Top panel:** a sunken light grey strip below the menu holding three parts: the mine counter at the left, the face in the centre and the timer at the right.
- **Mine counter:** a sunken black box showing three red seven-segment digits for mines minus flags placed. A negative value shows a minus sign followed by two digits.
- **Face button:** a raised grey square holding a yellow round face.
- **Face expressions:**
  - Smiling during play and before play begins.
  - Open "O" mouth while the player holds the mouse button down on a square.
  - Black sunglasses after a win.
  - Crossed-out X eyes after a loss.
- **Face button when pressed:** it appears sunken while held down.
- **Timer:** a sunken black box showing three red seven-segment digits for seconds elapsed. It reads 000 before the first click and stops at 999.
- **Board frame:** a sunken bevel around the grid, dark grey top-left and white bottom-right.
- **Hidden square:** a raised light grey square with a white top-left bevel and a dark grey bottom-right bevel. While pressed, it shows flat and sunken, like an empty uncovered square.
- **Flagged square:** a raised hidden square showing a small red triangular flag on a black pole and base.
- **Question-mark square:** a raised hidden square showing a black "?". It appears only when Marks is on.
- **Uncovered empty square:** flat light grey with thin dark grey grid lines and no mark.
- **Uncovered number square:** flat light grey showing a bold digit coloured by its value:
  - 1 blue
  - 2 green
  - 3 red
  - 4 navy
  - 5 maroon
  - 6 teal
  - 7 black
  - 8 grey
- **Exploded mine (on loss):** the mine the player uncovered, shown as a black round mine with spikes and a white glint on a flat red square.
- **Other mines (on loss):** every unflagged mine is shown as a black mine on a flat light grey square.
- **Wrong flag (on loss):** a flag that was not on a mine is shown as a black mine crossed by a red X on flat grey.
- **Correct flags (on loss):** flags that were on mines stay showing as flags.
- **Win board:** every remaining mine is shown as a flag, and the mine counter reads 000.
- **Custom dialog:** a raised light grey box titled "Custom Field" in white on a navy title bar. It holds three labelled white sunken number boxes (Height, Width, Mines) and raised grey OK and Cancel buttons.

## 3. How it is used

- **Uncover a square:** click, or tap, a hidden square to uncover it. A number, empty square or mine appears.
- **Uncover a blank region:** uncovering a square with zero neighbouring mines automatically uncovers all its neighbours, repeating outward until numbered squares border the opened region.
- **Cancel a press:** press and hold on a square, then drag off it before releasing. Nothing is uncovered, and the pressed look follows the pointer.
- **Flag a square:** right-click, or long-press on touch, a hidden square to place a flag. Repeat the same gesture to remove it.
- **Cycle marks with Marks on:** the same gesture moves a square from hidden to flag, then to question mark, then back to hidden.
- **Chord (uncover around a number):** middle-click, click with both buttons, or tap an uncovered number whose neighbouring flags equal it. All its unflagged hidden neighbours are uncovered at once.
- **Preview a chord:** while chording is held, the number's hidden neighbours show pressed. Releasing does nothing if the flag count does not match the number.
- **New game:** click or tap the face, or choose Game → New, or press F2. A fresh board at the same difficulty appears, with the timer at 000.
- **Change difficulty:** choose Beginner, Intermediate or Expert from the Game menu. A new board of that size starts.
- **Custom board:** choose Custom…, type a height, width and mine count, and press OK to start that board. Cancel keeps the current game.
- **Toggle question marks:** choose Marks (?) to turn question marks on or off.

## 4. Scope

One round of Minesweeper, from board to win or loss, then replay.

- **Difficulty choices:**
  - Beginner: 9×9 with 10 mines.
  - Intermediate: 16×16 with 40 mines.
  - Expert: 30 wide by 16 high with 99 mines.
  - Custom.
- **Option:** question marks on or off.
- **Remembered between visits on the device:** the last difficulty chosen and the Marks setting.
- **Left out:** accounts, leaderboards and best-times lists, multiplayer, payments and admin.

## 5. Things and their states

- **Board:** width, height, mine count and its squares.
  - Moves from **unseeded** to **seeded** when mines are placed on the first uncover.
- **Square:** whether it holds a mine, its neighbouring-mine count, and its mark.
  - Moves from **hidden** to **flagged** to **question-marked** (with Marks on) and back to **hidden**.
  - Moves from **hidden** to **uncovered**.
  - A mine square moves to **exploded** when uncovered.
- **Round:** elapsed seconds, flags placed and outcome.
  - Moves from **ready** to **in progress** on the first uncover.
  - Moves from **in progress** to **won** when every safe square is uncovered.
  - Moves from **in progress** to **lost** when a mine is uncovered.
  - Returns to **ready** from any state on new game.

## 6. Rules

- **Board sizes:** Beginner is 9×9 with 10 mines, Intermediate is 16×16 with 40 mines, and Expert is 30×16 with 99 mines.
- **Custom limits:** height is 9–24 and width is 9–30. Mines are 10 up to (height−1)×(width−1). Out-of-range values are clamped to the nearest limit.
- **Mine placement:** mines are placed at random, one per square at most.
- **Safe first click:** mines are placed after the first uncover, never on that square.
- **Neighbours:** each square's neighbours are the up to eight squares touching it, including diagonals.
- **Numbers:** an uncovered safe square shows how many of its neighbours are mines. Zero shows blank.
- **Flood opening:** uncovering a zero square uncovers all its non-flagged neighbours, repeating for any zeros found.
- **Flags are protected:** clicking a flagged square does nothing. Flood opening and chording skip flagged squares.
- **Question marks are not protected:** a question-marked square can be uncovered by click or chord.
- **Flags are unlimited:** the player may place more flags than mines, and the counter then goes negative.
- **Flags are not checked during play:** a flag's correctness is revealed only on loss.
- **Chording:** this works only on an uncovered number whose neighbouring flags equal it. Otherwise it is ignored and nothing changes.
- **Chording into a mine:** if a chord uncovers a mine because a flag was wrong, the game is lost.
- **Ignored gestures:** clicks or right-clicks on uncovered squares do nothing, except for chording.
- **Timer start:** the timer starts at the first uncover and counts whole seconds.
- **Timer stop:** the timer stops at win, at loss, or at 999.
- **Flagging before the first uncover:** this is allowed and does not start the timer.
- **Win:** every non-mine square is uncovered. Mines are auto-flagged, the face wears sunglasses and the timer stops.
- **Loss:** a mine is uncovered. All mines and wrong flags are revealed, the face shows X eyes and the timer stops.
- **After the end:** once a round is won or lost, the board ignores all square input until a new game starts.
- **Ending a round yourself:** the player ends a round at any time by starting a new game or changing difficulty. That round is simply discarded.