from src.domain.game import Game


STARTED = "2024-01-01T10:00:00+00:00"
WON_AT = "2024-01-01T10:05:00+00:00"


def make_cell(row, column, has_mine, adjacent_mine_count, state):
    return {
        "id": f"r{row}c{column}",
        "row": row,
        "column": column,
        "has_mine": has_mine,
        "adjacent_mine_count": adjacent_mine_count,
        "state": state,
    }


def build_in_progress_game_one_safe_cell_left():
    # 2x2 region of the board. Mine at (0,0). Safe cells (0,1), (1,0), (1,1).
    # Each safe cell touches the mine at (0,0) (edge-adjacent or diagonal),
    # so each has adjacent_mine_count 1, which means no zero-count expansion.
    # (0,1) and (1,0) are already revealed; (1,1) is still hidden.
    # No flags are placed, so flag_count is 0.
    # started_at is an ISO timestamp with an explicit offset, matching the
    # offset-aware reference time passed to reveal_cell.
    game = Game(id="game-1")
    game.status = "in_progress"
    game.started_at = STARTED
    game.ended_at = None
    game.elapsed_seconds = 0
    game.mine_count = 1
    game.flag_count = 0
    game.cells = [
        make_cell(0, 0, True, 0, "hidden"),
        make_cell(0, 1, False, 1, "revealed"),
        make_cell(1, 0, False, 1, "revealed"),
        make_cell(1, 1, False, 1, "hidden"),
    ]
    return game


def get_cell(game, row, column):
    matches = [c for c in game.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


def test_revealing_last_safe_cell_wins_and_flags_remaining_mines():
    # Given an in-progress game where the only hidden safe cell is (1,1),
    # the mine at (0,0) is still hidden, and the session started at STARTED.
    game = build_in_progress_game_one_safe_cell_left()

    # When the last non-mine cell (1,1) is revealed at the moment WON_AT.
    # Revealing (1,1) is a hidden, unflagged, safe cell on an in-progress game,
    # so the reveal is accepted. Once it is opened, every non-mine cell
    # (0,1), (1,0), (1,1) is revealed, so the session is won.
    game.reveal_cell(row=1, column=1, now=WON_AT)

    # Then the status becomes "won", because every non-mine cell is revealed.
    assert game.status == "won"

    # And ended_at is set to the moment the session ended.
    assert game.ended_at == WON_AT

    # And the timer stops at the win: 5 minutes after STARTED is 300 seconds.
    assert game.elapsed_seconds == 300

    # And the unrevealed mine at (0,0) becomes flagged on the win,
    # since it was hidden when the session was won.
    assert get_cell(game, 0, 0)["state"] == "flagged"

    # And the safe cells keep their revealed state.
    assert get_cell(game, 0, 1)["state"] == "revealed"
    assert get_cell(game, 1, 0)["state"] == "revealed"
    assert get_cell(game, 1, 1)["state"] == "revealed"
