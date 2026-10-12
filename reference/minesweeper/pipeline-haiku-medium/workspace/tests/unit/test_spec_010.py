from src.domain.game_session import GameSession


def make_session(rows, columns, mine_count):
    return GameSession(
        id="session-1",
        difficulty_id="custom",
        rows=rows,
        columns=columns,
        mine_count=mine_count,
    )


def cell_at(session, row, column):
    matches = [c for c in session.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


def test_corner_cell_with_two_mine_neighbours_and_one_safe_neighbour_counts_two():
    # Given a 2x2 board with 2 mines.
    # The corner (0,0) has exactly 3 existing neighbours: (0,1), (1,0), (1,1).
    # Those are the only other cells on the board, and the 2 mines sit among them,
    # so exactly 2 neighbours are mines and 1 is safe, whichever placement is random.
    session = make_session(rows=2, columns=2, mine_count=2)

    # When the first cell (0,0) is revealed. Mines are placed avoiding (0,0),
    # and adjacency is computed for every cell.
    session.reveal_cell(row=0, column=0)

    corner = cell_at(session, 0, 0)
    # Expected: the first reveal is a safe cell, so it is revealed (hidden and unflagged).
    assert corner["state"] == "revealed"
    # Expected: 2 existing neighbours are mines (the 2 mines are all among its 3 neighbours),
    # so adjacent_mine_count is 2. The count is not 3 because one neighbour is safe.
    assert corner["adjacent_mine_count"] == 2


def test_corner_cell_at_its_limit_counts_all_three_existing_neighbours():
    # Given a 2x2 board with 3 mines.
    # The corner (0,0) has exactly 3 existing neighbours, and the 3 mines fill all
    # other cells, so all 3 existing neighbours are mines (exactly at the limit).
    session = make_session(rows=2, columns=2, mine_count=3)

    # When the corner (0,0) is revealed first, mines are placed avoiding it.
    session.reveal_cell(row=0, column=0)

    corner = cell_at(session, 0, 0)
    # Expected: the 3 existing neighbours are all mines, so adjacent_mine_count is 3.
    # (The session may be won afterwards since (0,0) is the only safe cell; that does
    # not change the neighbour count.)
    assert corner["adjacent_mine_count"] == 3


def test_corner_cell_just_beyond_its_limit_ignores_non_neighbour_mines():
    # Given a 3x3 board with 8 mines.
    # The corner (0,0) has exactly 3 existing neighbours: (0,1), (1,0), (1,1).
    # Every cell except (0,0) is a mine, so the 3 neighbours are mines and the
    # other 5 cells, (0,2), (1,2), (2,0), (2,1), (2,2), are mines that are NOT
    # neighbours of (0,0) and must not be counted.
    session = make_session(rows=3, columns=3, mine_count=8)

    # When the corner (0,0) is revealed first, mines are placed avoiding it.
    session.reveal_cell(row=0, column=0)

    corner = cell_at(session, 0, 0)
    # Expected: only the 3 existing neighbours count, so adjacent_mine_count is 3,
    # not 8 (which a wrap-around or padded neighbourhood would give).
    assert corner["adjacent_mine_count"] == 3
