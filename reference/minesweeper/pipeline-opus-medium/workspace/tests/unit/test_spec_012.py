from src.domain.game import Game

WIDTH = 9
HEIGHT = 9
# Highest mine count allowed for a 9x9 custom board, (9-1)*(9-1) = 64.
# With only 17 safe cells, the first open cannot realistically cascade
# through every safe cell. So the game ends in Playing and not in Won.
MINE_COUNT = 64


def _fresh_cells():
    return [
        {
            "id": f"{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for row in range(HEIGHT)
        for column in range(WIDTH)
    ]


def _ready_game():
    game = Game(
        id="game-1",
        difficulty_id="custom",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00Z",
    )
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.cells = _fresh_cells()
    game.events = []
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


def test_first_open_of_hidden_unflagged_cell_moves_ready_game_to_playing():
    game = _ready_game()

    game.open_cell(row=4, column=4)

    # Cell (4,4) is Hidden and unflagged, and the game is Ready.
    # The first open lays 64 mines on the cells other than (4,4), so (4,4) is safe.
    # A safe cell cannot cause a loss.
    # 16 other safe cells exist, and they are not all opened by this one click.
    # So the game cannot be Won. The Ready->Playing rule alone decides the status.
    assert game.status == "Playing"
    # The opened cell is safe (first click is safe), so its state is Opened.
    assert _cell(game, 4, 4)["state"] == "Opened"


def test_opening_a_flagged_cell_in_ready_game_keeps_it_ready():
    game = _ready_game()
    # The accepted case changed in one way only: the target cell is Flagged.
    _cell(game, 4, 4)["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = MINE_COUNT - 1

    game.open_cell(row=4, column=4)

    # Opening a Flagged cell changes nothing and raises no error.
    # This open does not count as the first open: no mines are laid.
    # The status does not move from Ready to Playing.
    assert game.status == "Ready"
    # The cell stays Flagged and no mine has been laid anywhere.
    assert _cell(game, 4, 4)["state"] == "Flagged"
    assert game.mines_laid is False
    assert all(c["has_mine"] is False for c in game.cells)
