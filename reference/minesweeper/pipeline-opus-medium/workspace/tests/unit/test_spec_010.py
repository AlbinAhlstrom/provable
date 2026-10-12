import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINES = 10


def _fresh_cells(width, height):
    # Same shape as a newly created game: one dict per position, row-major,
    # every key the class describes, no mine anywhere, all Hidden.
    return [
        {
            "id": f"{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for row in range(height)
        for column in range(width)
    ]


def _ready_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINES,
        remaining_mines=MINES,
        created_at="2024-01-01T10:00:00",
    )
    # Given: Ready status, no mines laid, untouched board.
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.cells = _fresh_cells(WIDTH, HEIGHT)
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


def test_newly_created_game_has_no_mines_laid():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINES,
        remaining_mines=MINES,
        created_at="2024-01-01T10:00:00",
    )

    # A new game is Ready and has not laid its mines yet.
    assert game.status == "Ready"
    assert game.mines_laid is False
    # The board already has all 9x9 = 81 positions ...
    assert len(game.cells) == WIDTH * HEIGHT
    # ... and none of them holds a mine before the first open.
    assert sum(1 for c in game.cells if c["has_mine"]) == 0


def test_flagging_before_first_open_does_not_lay_mines():
    game = _ready_game()

    game.toggle_flag(row=4, column=4)

    # Flagging is allowed in Ready; cell (4,4) goes Hidden -> Flagged.
    assert _cell(game, 4, 4)["state"] == "Flagged"
    # No cell has been opened yet, so still no mines exist and the game is Ready.
    assert game.mines_laid is False
    assert game.status == "Ready"
    assert sum(1 for c in game.cells if c["has_mine"]) == 0


@pytest.mark.parametrize("row,column", [(0, 0), (4, 4)])
def test_mines_are_laid_when_first_cell_is_opened(row, column):
    game = _ready_game()

    # Before the first open: no cell holds a mine.
    assert game.mines_laid is False
    assert sum(1 for c in game.cells if c["has_mine"]) == 0

    game.open_cell(row=row, column=column)

    # The first open of a Ready game lays the mines at that moment.
    assert game.mines_laid is True
    # The board keeps its 81 cells, and exactly mine_count = 10 of them now hold a mine
    # (laying or auto-flagging never adds or removes has_mine beyond mine_count).
    assert len(game.cells) == WIDTH * HEIGHT
    assert sum(1 for c in game.cells if c["has_mine"]) == MINES
    # First click is safe: the opened cell is never one of the mines, so it is
    # Opened (not Detonated) and the game is not Lost.
    opened = _cell(game, row, column)
    assert opened["has_mine"] is False
    assert opened["state"] == "Opened"
    assert game.status != "Lost"
    assert game.struck_cell_id is None
