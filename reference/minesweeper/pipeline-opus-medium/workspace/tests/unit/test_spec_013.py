import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINES = 10
# Mines: the whole bottom row (row 8, columns 0..8) plus (7, 8) -> exactly 10 mines.
MINE_POSITIONS = {(8, c) for c in range(9)} | {(7, 8)}


def _new_game() -> Game:
    return Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINES,
        remaining_mines=MINES,
        created_at="2024-01-01T10:00:00",
    )


def _cell(game: Game, row: int, column: int) -> dict:
    return game.cells[row * game.width + column]


def _fresh_cells(width: int, height: int) -> list:
    return [
        {
            "id": f"{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for r in range(height)
        for c in range(width)
    ]


def _playing_game() -> Game:
    game = _new_game()
    cells = _fresh_cells(WIDTH, HEIGHT)
    for cell in cells:
        r, c = cell["row"], cell["column"]
        cell["has_mine"] = (r, c) in MINE_POSITIONS
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                if (r + dr, c + dc) in MINE_POSITIONS:
                    count += 1
        cell["adjacent_mine_count"] = count
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    game.flags_placed = 0
    game.remaining_mines = MINES
    game.elapsed_seconds = 5
    game.started_at = "2024-01-01T10:00:00"
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    return game


def _ready_game() -> Game:
    game = _new_game()
    game.cells = _fresh_cells(WIDTH, HEIGHT)
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.remaining_mines = MINES
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    return game


def test_open_hidden_safe_numbered_cell_in_playing_game_becomes_opened():
    game = _playing_game()
    before = {cell["id"]: cell["state"] for cell in game.cells}

    game.open_cell(row=7, column=4)

    # (7,4) is safe; its neighbours (8,3), (8,4), (8,5) are mines -> count 3,
    # so it is a numbered cell: it becomes Opened and no cascade happens.
    assert _cell(game, 7, 4)["state"] == "Opened"
    assert _cell(game, 7, 4)["adjacent_mine_count"] == 3
    # Many other safe cells remain Hidden, so the game is not Won; no mine opened, not Lost.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    # No cascade (numbered cell): every other cell keeps its previous state.
    for cell in game.cells:
        if cell["id"] != "7-4":
            assert cell["state"] == before[cell["id"]]


def test_open_hidden_mine_cell_in_playing_game_becomes_detonated():
    game = _playing_game()

    game.open_cell(row=8, column=4)

    # (8,4) holds a mine: it becomes Detonated, is the struck cell and the game is Lost.
    assert _cell(game, 8, 4)["state"] == "Detonated"
    assert game.struck_cell_id == "8-4"
    assert game.status == "Lost"


@pytest.mark.parametrize("row,column", [(4, 4), (0, 0)])
def test_open_hidden_cell_in_ready_game_becomes_opened(row, column):
    game = _ready_game()

    game.open_cell(row=row, column=column)

    # First open is always safe (mines are placed elsewhere), so the cell becomes Opened,
    # never Detonated, and the game moves from Ready to Playing.
    cell = _cell(game, row, column)
    assert cell["has_mine"] is False
    assert cell["state"] == "Opened"
    assert game.status == "Playing"


def test_open_flagged_cell_is_not_opened():
    game = _playing_game()
    _cell(game, 7, 4)["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = MINES - 1

    game.open_cell(row=7, column=4)

    # A Flagged cell cannot be opened: it stays Flagged, counters unchanged, game still Playing.
    assert _cell(game, 7, 4)["state"] == "Flagged"
    assert game.flags_placed == 1
    assert game.remaining_mines == MINES - 1
    assert game.status == "Playing"


def test_open_hidden_cell_in_lost_game_changes_nothing():
    game = _playing_game()
    _cell(game, 8, 0)["state"] = "Detonated"
    game.status = "Lost"
    game.struck_cell_id = "8-0"
    game.ended_at = "2024-01-01T10:00:05"

    game.open_cell(row=7, column=4)

    # The game is Lost (not Ready or Playing): the board is locked, (7,4) stays Hidden.
    assert _cell(game, 7, 4)["state"] == "Hidden"
    assert game.status == "Lost"
    assert game.struck_cell_id == "8-0"
    assert game.elapsed_seconds == 5
