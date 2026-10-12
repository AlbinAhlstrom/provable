from src.domain.game_session import GameSession

ROWS = 9
COLUMNS = 9
CENTRE = (4, 4)
# Ten mines. The four orthogonal cells at distance 2 from the centre make every
# ring neighbour of the centre a numbered cell, so the spread stops at the ring.
# The remaining mines sit outside the rows 2-6 / columns 2-6 band, so they do not
# touch the centre or any ring neighbour.
MINES = {
    (2, 4), (4, 2), (4, 6), (6, 4),
    (0, 0), (0, 4), (0, 8), (8, 0), (8, 4), (8, 8),
}
NEIGHBOURS = [
    (3, 3), (3, 4), (3, 5),
    (4, 3), (4, 5),
    (5, 3), (5, 4), (5, 5),
]


def _cell(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def _fill_adjacency(session):
    # Test arrangement only: compute each cell's count from the mines we placed,
    # so the board is internally consistent.
    for cell in session.cells:
        count = 0
        for other in session.cells:
            dr = abs(other["row"] - cell["row"])
            dc = abs(other["column"] - cell["column"])
            if (dr, dc) != (0, 0) and dr <= 1 and dc <= 1 and other["has_mine"]:
                count += 1
        cell["adjacent_mine_count"] = count


def _spread_session():
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=ROWS,
        columns=COLUMNS,
        mine_count=10,
    )
    # Given a game already in progress, so no random mine placement happens on reveal.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    for cell in session.cells:
        cell["has_mine"] = (cell["row"], cell["column"]) in MINES
    _fill_adjacency(session)

    # Given the centre is hidden, unflagged, safe, and has adjacent_mine_count 0.
    centre = _cell(session, *CENTRE)
    assert centre["state"] == "hidden"
    assert centre["has_mine"] is False
    assert centre["adjacent_mine_count"] == 0

    # When the player reveals the centre cell.
    session.reveal_cell(row=CENTRE[0], column=CENTRE[1])
    return session


def test_zero_count_centre_is_revealed():
    session = _spread_session()
    # The centre was hidden, unflagged, safe and zero-count, so it is revealed.
    assert _cell(session, *CENTRE)["state"] == "revealed"


def test_zero_count_reveal_leaves_outer_cells_hidden():
    session = _spread_session()
    # Only the centre and its eight neighbours are opened: every neighbour has a
    # nonzero count, so the spread stops at them. The cell (2, 2) is two steps
    # away and is not a neighbour, so it must remain hidden.
    assert _cell(session, 2, 2)["state"] == "hidden"


def test_spread_reveals_neighbour_of_zero_centre_at_row_3_column_3():
    session = _spread_session()
    # Neighbour (3, 3) is diagonal to the centre; it exists and is safe, and the
    # centre has count 0, so (3, 3) becomes revealed.
    assert _cell(session, 3, 3)["state"] == "revealed"


def test_spread_reveals_neighbour_directly_above_centre():
    session = _spread_session()
    # Neighbour (3, 4) is directly above the centre; it exists and is safe, so it
    # becomes revealed.
    assert _cell(session, 3, 4)["state"] == "revealed"


def test_spread_reveals_neighbour_directly_below_centre():
    session = _spread_session()
    # Neighbour (5, 4) is directly below the centre; it exists and is safe, so it
    # becomes revealed.
    assert _cell(session, 5, 4)["state"] == "revealed"


def test_spread_reveals_neighbour_directly_left_of_centre():
    session = _spread_session()
    # Neighbour (4, 3) is directly left of the centre; it exists and is safe, so it
    # becomes revealed.
    assert _cell(session, 4, 3)["state"] == "revealed"


def test_spread_reveals_neighbour_directly_right_of_centre():
    session = _spread_session()
    # Neighbour (4, 5) is directly right of the centre; it exists and is safe, so it
    # becomes revealed.
    assert _cell(session, 4, 5)["state"] == "revealed"


def test_all_eight_neighbours_are_revealed():
    session = _spread_session()
    # All eight neighbours exist (centre is not on the edge), are safe, and have
    # nonzero counts, so each one becomes revealed.
    for row, column in NEIGHBOURS:
        assert _cell(session, row, column)["state"] == "revealed", (row, column)
