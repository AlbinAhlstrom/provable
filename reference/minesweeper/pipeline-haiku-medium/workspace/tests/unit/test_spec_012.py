from src.domain.game_session import GameSession


MINE_POSITIONS = [
    (0, 1),
    (8, 0), (8, 1), (8, 2), (8, 3), (8, 4),
    (8, 5), (8, 6), (8, 7), (8, 8),
]


def _cell(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def _in_progress_beginner_session():
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )
    # Given a session in progress: status in_progress, timer already running.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.elapsed_seconds = 5
    # Given mines already placed (10 mines, matching mine_count), none at (0, 0).
    for row, column in MINE_POSITIONS:
        _cell(session, row, column)["has_mine"] = True
    # Given the target cell (0, 0) is safe and touches exactly one mine, at (0, 1),
    # so its adjacent_mine_count is 1 and revealing it does not spread.
    _cell(session, 0, 0)["adjacent_mine_count"] = 1
    return session


def test_revealing_hidden_unflagged_cell_makes_it_revealed():
    session = _in_progress_beginner_session()

    session.reveal_cell(row=0, column=0)

    # Target (0, 0) was hidden and unflagged, so the reveal succeeds and its
    # state becomes "revealed".
    assert _cell(session, 0, 0)["state"] == "revealed"


def test_revealing_hidden_cell_keeps_session_in_progress_and_other_cells_hidden():
    session = _in_progress_beginner_session()

    session.reveal_cell(row=0, column=0)

    # The target is safe (has_mine False) and its count is 1, not 0, so no
    # zero-spread happens: neighbour (1, 0) is not a mine-free zero and stays hidden.
    assert _cell(session, 1, 0)["state"] == "hidden"
    # Many safe cells remain hidden, so the board is not won; the revealed
    # cell is not a mine, so the game is not lost: status stays in_progress.
    assert session.status == "in_progress"
    # The timer is untouched by a reveal inside a running game.
    assert session.elapsed_seconds == 5
    assert session.started_at == "2024-01-01T10:00:00"
