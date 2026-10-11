# Minesweeper

Classic Minesweeper. The server owns the rules and the mine positions; the browser shows what it is told.

## Run it

Needs Python 3.11+ and Node 20+. All commands from this folder.

```
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

Development (two terminals):

```
python -m uvicorn src.app:app --port 8101          # API
cd frontend && npm run dev                         # page on http://localhost:5181
```

Or as one process (the API also serves the built page):

```
cd frontend && npm run build && cd ..
python -m uvicorn src.app:app --port 8101          # open http://localhost:8101
```

Games are stored in `data/minesweeper.db` (SQLite, created on first use). Set `MINESWEEPER_DB` to use another file.

## Test it

```
python -m pytest            # 116 tests: domain rules, repository, HTTP layer
cd frontend && npm run build   # strict TypeScript check + production build
```

## Play

- Click reveals. The first click is always safe and opens an area.
- Right-click (or long-press, or turn on Flag mode) flags a cell.
- Click a revealed number to open its neighbours once its flags are placed (chording).
- Keyboard: arrow keys move, Enter or Space reveals, F flags.
- Beginner, Intermediate, Expert or a custom board. Best times, win rate and recent games are kept; a reload resumes your game.

## Layout

| Path | What |
| --- | --- |
| `src/domain/` | The rules, pure Python: `game.py` (Game, GameView, errors), `minefield.py` (neighbours, seeded mine placement), `stats.py` |
| `src/adapters/sqlite_repository.py` | Stores games |
| `src/app.py` | FastAPI: `/api/games` (create, list, get), `/api/games/{id}/reveal|flag|chord`, `/api/stats`, `/api/difficulties` |
| `tests/` | pytest; rule tests are named after the rule ids in `STEPS.md` |
| `frontend/` | React 18 + TypeScript + Vite + Tailwind; `src/api.ts` is the typed client |
| `STEPS.md` | Rule list, data model and the log of how this was built |
