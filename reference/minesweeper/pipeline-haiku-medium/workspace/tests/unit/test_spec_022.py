from src.domain.game_session import GameSession


def build_hidden_board(rows, columns):
    """Return the cell records a newly created session holds: one per position, all hidden."""
    return [
        {
            "id": f"{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "hidden",
        }
        for r in range(rows)
        for c in range(columns)
    ]


def find_cell(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def test_flagging_hidden_cell_before_first_reveal_keeps_session_ready():
    # Given a session in Ready state (beginner-sized board, 9 x 9, 10 mines).
    session = GameSession(
        id="session-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )
    # Shape of a newly created session: one hidden record per position, no mines placed.
    session.cells = build_hidden_board(9, 9)
    # Status is ready, elapsed_seconds is 0, started_at is None (newly created state).

    # When the player flags the hidden cell at (4, 4).
    session.toggle_flag(row=4, column=4)

    # Then the session status remains ready.
    # Working: the cell was hidden and unflagged, so the flag is allowed in Ready;
    # a flag neither reveals (no reveal, so no first-reveal transition) nor starts the timer.
    assert session.status == "ready"

    # And elapsed_seconds stays 0.
    # Working: the timer only starts at the first reveal; a flag does not start it.
    assert session.elapsed_seconds == 0

    # Supporting checks that the flag actually happened on the hidden cell:
    # the cell at (4, 4) was hidden, so toggling makes it flagged and raises flag_count from 0 to 1.
    assert find_cell(session, 4, 4)["state"] == "flagged"
    assert session.flag_count == 1
    # No reveal happened, so no mines were placed and the start time is still unset.
    assert session.started_at is None
