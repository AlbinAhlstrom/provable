import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
# Densest board the custom limits allow: (9-1)*(9-1) = 64 mines on 81 cells.
# A placement that ignored the first cell would put a mine on it with
# probability 64/81 per game, so repeated games expose an unsafe first click.
MINE_COUNT = 64
REPEATS = 25


def _fresh_cells(width, height):
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


def _ready_game(index):
    game = Game(
        id=f"game-{index}",
        difficulty_id="custom",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00Z",
    )
    # Put the game in its starting Ready state: no mines laid, all cells Hidden.
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.cells = _fresh_cells(WIDTH, HEIGHT)
    game.events = []
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


@pytest.mark.parametrize(
    "row, column",
    [
        (0, 0),  # corner
        (4, 4),  # interior
        (0, 5),  # top edge
        (8, 8),  # opposite corner
        (6, 0),  # left edge
    ],
)
def test_first_opened_cell_never_holds_a_mine(row, column):
    for i in range(REPEATS):
        game = _ready_game(i)

        game.open_cell(row=row, column=column)

        opened = _cell(game, row, column)
        # First open of a Ready game: mines are placed only on cells other than
        # the opened one, so the opened cell holds no mine.
        assert opened["has_mine"] is False
        # It is a safe Hidden cell, so it becomes Opened (not Detonated).
        assert opened["state"] == "Opened"
        # Exactly mine_count mines were laid, all elsewhere (64 of the 80 other cells).
        assert sum(1 for c in game.cells if c["has_mine"]) == MINE_COUNT
        assert game.mines_laid is True
        # No mine was opened, so no struck cell and no loss. With 17 safe cells
        # a cascade could in a rare layout reveal all of them (Won), otherwise
        # the game is Playing; either way it is not Lost.
        assert game.struck_cell_id is None
        assert game.status != "Lost"
        assert game.status in ("Playing", "Won")
        # No Detonated cell anywhere on the board.
        assert all(c["state"] != "Detonated" for c in game.cells)
