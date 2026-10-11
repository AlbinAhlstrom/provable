from src.domain.game import Game

WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Mines at row 0 columns 0..8 and at row 1 column 0 (10 mines in total).
MINE_POSITIONS = {(0, c) for c in range(9)} | {(1, 0)}


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _build_cells():
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in MINE_POSITIONS,
                    "adjacent_mine_count": sum(
                        1 for n in _neighbours(row, column) if n in MINE_POSITIONS
                    ),
                    "state": "Hidden",
                }
            )
    # One safe cell already opened (the first open), so the game is Playing
    # but far from won: many safe cells remain Hidden.
    for cell in cells:
        if cell["row"] == 8 and cell["column"] == 8:
            cell["state"] = "Opened"
    return cells


def _playing_game(elapsed_seconds):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00Z",
    )
    game.cells = _build_cells()
    game.status = "Playing"
    game.mines_laid = True
    game.flags_placed = 0
    game.remaining_mines = MINE_COUNT
    game.started_at = "2024-01-01T10:00:05Z"
    game.ended_at = None
    game.struck_cell_id = None
    game.elapsed_seconds = elapsed_seconds
    return game


def _cell_snapshot(game):
    return [dict(cell) for cell in game.cells]


def test_tick_reaches_exactly_999_from_998():
    game = _playing_game(998)
    cells_before = _cell_snapshot(game)

    game.tick()

    # Status Playing, elapsed 998: tick adds 1 -> 999, which equals the cap,
    # so the increment is allowed in full.
    assert game.elapsed_seconds == 999
    # Ticking never opens, flags or ends anything: status stays Playing.
    assert game.status == "Playing"
    assert game.ended_at is None
    assert _cell_snapshot(game) == cells_before


def test_tick_beyond_999_stays_at_999():
    game = _playing_game(999)
    cells_before = _cell_snapshot(game)

    game.tick()

    # Status Playing, elapsed 999: tick would give 1000, which is beyond the
    # cap, so elapsed seconds stays at 999.
    assert game.elapsed_seconds == 999
    # The cap does not end the game: still Playing, board untouched.
    assert game.status == "Playing"
    assert game.ended_at is None
    assert _cell_snapshot(game) == cells_before


def test_repeated_ticks_at_999_never_exceed_cap():
    game = _playing_game(999)

    for _ in range(5):
        game.tick()

    # Every tick from 999 is capped, so after 5 more seconds it is still 999.
    assert game.elapsed_seconds == 999
    assert game.status == "Playing"
