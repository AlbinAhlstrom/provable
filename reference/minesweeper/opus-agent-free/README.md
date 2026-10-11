# Minesweeper

Classic Minesweeper in plain HTML, CSS and JavaScript. No dependencies, no build step, works offline.

## Run it

Either:

- Double-click `index.html`, or
- Serve the folder and open http://localhost:5182/

      python -m http.server 5182

## Play

- **Mouse:** left-click digs, right-click flags. Click (or middle-click) a number that has that many flags around it to dig the rest of its neighbours.
- **Touch:** tap digs, press and hold flags. The Dig / Flag switch under the board swaps the two.
- **Keyboard:** arrows move, Enter or Space digs, F flags, R or F2 starts a new game.
- Your first dig is always safe and always opens an area.
- Levels: Beginner (9x9, 10 mines), Intermediate (16x16, 40), Expert (30x16, 99), or Custom.
- Best time and win count are kept per board size in the browser. A game in progress survives a reload.
- Add `?seed=123` to the address to get the same board every time.

## Test it

    node --test tests/        # rules engine, 21 tests, no dependencies
    python tests/e2e.py       # plays the game in headless Chrome (needs Chrome and `pip install selenium`)

The browser test writes screenshots to `tests/screenshots/`.

## Layout

- `src/engine.js`: the rules (pure logic, no DOM).
- `src/app.js`: drawing, input, timer, stats, saving.
- `index.html`, `styles.css`: the page.
- `STEPS.md`: how it was built, step by step.
