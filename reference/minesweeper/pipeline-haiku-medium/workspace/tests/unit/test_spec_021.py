from src.domain.game_session import GameSession


def _cell_at(session, row, column):
    matches = [c for c in session.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


def _new_session():
    # Beginner preset: 9 rows, 9 columns, 10 mines.
    # Constructed as the class creates a new game: 81 cells, each hidden,
    # has_mine false, adjacent_mine_count 0, status ready, no mines placed yet.
    return GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )


def test_flagging_hidden_cell_changes_only_that_cell():
    # Given: a ready session with no mines placed, so every cell has
    # adjacent_mine_count 0 and state hidden.
    # The hidden cell at (4, 4) is next to the zero-count cell at (4, 5).
    # No reveal has happened, so no cell is revealed and no spread can occur.
    session = _new_session()
    before = [dict(c) for c in session.cells]
    target = _cell_at(session, 4, 4)
    neighbour = _cell_at(session, 4, 5)
    assert target["state"] == "hidden"
    assert neighbour["state"] == "hidden"
    assert neighbour["adjacent_mine_count"] == 0

    # When: the player flags the hidden cell at (4, 4).
    session.toggle_flag(row=4, column=4)

    # Then: the flagged cell is the only one whose state changes.
    # Its state goes from hidden to flagged.
    assert _cell_at(session, 4, 4)["state"] == "flagged"

    # Then: every other cell, including the zero-count neighbour at (4, 5),
    # is identical to its state before the flag. It stays hidden and nothing spreads.
    assert len(session.cells) == len(before)
    for old, new in zip(before, session.cells):
        if old["row"] == 4 and old["column"] == 4:
            continue
        assert new == old
    assert _cell_at(session, 4, 5)["state"] == "hidden"

    # Then: the flag counter rises by one, and the session stays ready
    # because flagging does not start the game.
    assert session.flag_count == 1
    assert session.status == "ready"
