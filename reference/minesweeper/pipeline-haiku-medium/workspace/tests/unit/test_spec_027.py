import pytest

from src.domain.game_session import GameSession


BEGINNER_ROWS = 9
BEGINNER_COLUMNS = 9
BEGINNER_MINES = 10

# Ten mines on a 9x9 board, all distinct and none on a row/column edge pair that
# would matter here. Placed only for the in-progress arrangement so that the
# board is consistent with a game that has already started.
MINE_POSITIONS = [
    (0, 0), (0, 8), (1, 4), (2, 2), (3, 6),
    (4, 0), (5, 5), (6, 3), (7, 7), (8, 4),
]


def _place_mines(session, mine_positions):
    """Place mines and compute adjacent_mine_count for every cell."""
    mines = set(mine_positions)
    for cell in session.cells:
        cell["has_mine"] = (cell["row"], cell["column"]) in mines
    for cell in session.cells:
        count = 0
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue
                if (cell["row"] + d_row, cell["column"] + d_col) in mines:
                    count += 1
        cell["adjacent_mine_count"] = count


def _arrange(starting_status):
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=BEGINNER_ROWS,
        columns=BEGINNER_COLUMNS,
        mine_count=BEGINNER_MINES,
    )
    if starting_status == "ready":
        # Ready: no mines placed, timer not started, elapsed 0.
        session.status = "ready"
        session.elapsed_seconds = 0
        session.started_at = None
        session.ended_at = None
    else:
        # In progress: mines already placed, timer running at 42 seconds.
        _place_mines(session, MINE_POSITIONS)
        session.status = "in_progress"
        session.elapsed_seconds = 42
        session.started_at = "2024-03-01T12:00:00"
        session.ended_at = None
    return session


@pytest.mark.parametrize("starting_status", ["ready", "in_progress"])
def test_abandon_game_ends_with_no_result_and_new_board_keeps_difficulty(starting_status):
    # Given a session in Ready or in progress on the beginner difficulty
    session = _arrange(starting_status)
    elapsed_before = session.elapsed_seconds

    # When the player abandons the game
    session.abandon_game()

    # Then the status is "abandoned": the session was ready or in_progress, and
    # abandon_game sets status to abandoned, which is not won or lost.
    assert session.status == "abandoned"

    # And ended_at is recorded: abandon_game records the end of the game.
    assert session.ended_at is not None

    # And elapsed_seconds stops at its current value: the timer was at
    # elapsed_before (0 when ready, 42 when in progress) and must not move.
    assert session.elapsed_seconds == elapsed_before

    # And the difficulty of the abandoned board is unchanged, so the next
    # board is at the same difficulty: 9 rows, 9 columns, 10 mines.
    assert session.difficulty_id == "beginner"
    assert session.rows == BEGINNER_ROWS
    assert session.columns == BEGINNER_COLUMNS
    assert session.mine_count == BEGINNER_MINES

    # When the player starts a new board at the same difficulty
    session.start_new_game(
        difficulty_id="beginner",
        rows=BEGINNER_ROWS,
        columns=BEGINNER_COLUMNS,
        mine_count=BEGINNER_MINES,
    )

    # Then the new board is ready at the same difficulty:
    # status ready (new game, no reveal yet), dimensions and mines as beginner,
    # flag_count 0, elapsed_seconds 0, started_at and ended_at cleared.
    assert session.status == "ready"
    assert session.difficulty_id == "beginner"
    assert session.rows == BEGINNER_ROWS
    assert session.columns == BEGINNER_COLUMNS
    assert session.mine_count == BEGINNER_MINES
    assert session.flag_count == 0
    assert session.elapsed_seconds == 0
    assert session.started_at is None
    assert session.ended_at is None

    # And the new board holds 9 x 9 = 81 hidden cells with no mines placed
    # (mines are placed only after the first reveal).
    assert len(session.cells) == BEGINNER_ROWS * BEGINNER_COLUMNS
    assert all(cell["state"] == "hidden" for cell in session.cells)
    assert all(cell["has_mine"] is False for cell in session.cells)
    assert all(cell["adjacent_mine_count"] == 0 for cell in session.cells)
