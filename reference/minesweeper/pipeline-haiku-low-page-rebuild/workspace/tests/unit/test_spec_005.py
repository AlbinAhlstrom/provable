import copy

from src.domain.game import Game


def make_in_progress_game(target_state: str) -> Game:
    """Build an in-progress 9x9 Beginner board with a full 81-cell grid.

    Every cell is safe with adjacent_mine_count 0, so no rule about mines,
    expansion, or winning is in play. Only the state of cell (4, 4) differs
    between the two scenarios.
    """
    game = Game(id="game-flag-1")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = "2024-01-01T10:00:00"
    game.elapsed_seconds = 0
    game.mine_count = 10
    game.flag_count = 0
    game.cells = [
        {
            "id": f"r{row}c{col}",
            "row": row,
            "column": col,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "hidden",
        }
        for row in range(9)
        for col in range(9)
    ]
    for cell in game.cells:
        if cell["row"] == 4 and cell["column"] == 4:
            cell["state"] = target_state
    return game


def find_cell(game: Game, row: int, column: int) -> dict:
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def test_flagging_a_hidden_cell_sets_state_to_flagged_and_increments_flag_count():
    # Given an in-progress 9x9 board, all cells safe with count 0,
    # and cell (4, 4) is hidden. flag_count starts at 0.
    game = make_in_progress_game(target_state="hidden")

    # When the player flags cell (4, 4).
    game.toggle_flag(row=4, column=4)

    # Then the cell is hidden -> flagged: its state is "flagged".
    assert find_cell(game, 4, 4)["state"] == "flagged"
    # And flag_count goes from 0 to 1 (one flag placed).
    assert game.flag_count == 1


def test_flagging_a_revealed_cell_leaves_the_board_unchanged():
    # Given the same in-progress 9x9 board, but cell (4, 4) is revealed.
    # The cell is not hidden, so a flag may not be placed on it.
    game = make_in_progress_game(target_state="revealed")
    board_before = copy.deepcopy(game.cells)
    flags_before = game.flag_count

    # When the player tries to flag cell (4, 4).
    # The rule ignores flagging of revealed cells, so no exception is expected.
    game.toggle_flag(row=4, column=4)

    # Then every cell is exactly as it was, including cell (4, 4) still revealed.
    assert game.cells == board_before
    assert find_cell(game, 4, 4)["state"] == "revealed"
    # And flag_count is unchanged at 0.
    assert game.flag_count == flags_before
