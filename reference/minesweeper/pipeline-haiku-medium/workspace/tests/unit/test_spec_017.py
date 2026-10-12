from src.domain.game_session import GameSession


def _session_with_board():
    """Build a 3x5 in-progress board with two mines in column 0.

    Layout (M = mine, numbers = adjacent_mine_count, . = zero):
        row 0:  M 1 . . .
        row 1:  2 2 . . .
        row 2:  M 1 . . .
    The zero region is columns 2-4. Its numbered borders are (0,1), (1,1), (2,1).
    Cell (1,0) is numbered (2) and lies beyond the border, so it must stay hidden.
    """
    session = GameSession(
        id="game-spread",
        difficulty_id="beginner",
        rows=3,
        columns=5,
        mine_count=2,
    )
    # Keep the 15 hidden records created by the constructor; only change their contents.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    mines = {(0, 0), (2, 0)}
    counts = {
        (0, 0): 0, (0, 1): 1, (0, 2): 0, (0, 3): 0, (0, 4): 0,
        (1, 0): 2, (1, 1): 2, (1, 2): 0, (1, 3): 0, (1, 4): 0,
        (2, 0): 0, (2, 1): 1, (2, 2): 0, (2, 3): 0, (2, 4): 0,
    }
    for cell in session.cells:
        position = (cell["row"], cell["column"])
        cell["has_mine"] = position in mines
        cell["adjacent_mine_count"] = counts[position]
        cell["state"] = "hidden"
    return session


def _cell(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def test_zero_spread_reveals_connected_zeros_and_bordering_numbers_only():
    session = _session_with_board()

    session.reveal_cell(row=1, column=3)

    # The reveal starts at zero cell (1,3). Its connected zeros are all of
    # columns 2, 3 and 4 (9 cells). Each zero spreads to its neighbours, so
    # every zero is reached. Their numbered borders (0,1), (1,1) and (2,1)
    # are revealed as well, but they do not spread further.
    # Expected: revealed.
    assert _cell(session, 0, 2)["state"] == "revealed"  # zero, reached from (1,3)
    assert _cell(session, 1, 2)["state"] == "revealed"  # zero, connected to (1,3)
    assert _cell(session, 2, 2)["state"] == "revealed"  # zero, connected to (1,3)
    assert _cell(session, 0, 3)["state"] == "revealed"  # zero, neighbour of (1,3)
    assert _cell(session, 1, 3)["state"] == "revealed"  # the cell revealed by the player
    assert _cell(session, 2, 3)["state"] == "revealed"  # zero, neighbour of (1,3)
    assert _cell(session, 0, 4)["state"] == "revealed"  # zero, corner of the region
    assert _cell(session, 1, 4)["state"] == "revealed"  # zero, neighbour of (1,3)
    assert _cell(session, 2, 4)["state"] == "revealed"  # zero, corner of the region

    # Numbered cells bordering the zero region are revealed, adjacent to zero (1,2) or (0,2)/(2,2).
    # (0,1) has count 1, adjacent to zero (0,2): revealed.
    assert _cell(session, 0, 1)["state"] == "revealed"
    # (1,1) has count 2, adjacent to zero (1,2): revealed.
    assert _cell(session, 1, 1)["state"] == "revealed"
    # (2,1) has count 1, adjacent to zero (2,2): revealed.
    assert _cell(session, 2, 1)["state"] == "revealed"

    # (1,0) is numbered (2) and lies beyond the border. Numbers do not spread,
    # and no zero touches it, so it stays hidden.
    assert _cell(session, 1, 0)["state"] == "hidden"

    # The two mines in column 0 are never revealed by a spread.
    # Expected: hidden.
    assert _cell(session, 0, 0)["state"] == "hidden"
    assert _cell(session, 2, 0)["state"] == "hidden"

    # One safe cell, (1,0), is still hidden, so the win condition is not met
    # and the game continues. Expected: in_progress, with no ended_at.
    assert session.status == "in_progress"
    assert session.ended_at is None
