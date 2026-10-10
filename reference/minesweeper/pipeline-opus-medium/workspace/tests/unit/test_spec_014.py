from src.domain.game import Game


CREATED_AT = "2024-01-01T10:00:00Z"
STARTED_AT = "2024-01-01T10:00:05Z"


def _new_game(width=9, height=9, mine_count=10):
    return Game(
        id="game-1",
        difficulty_id="beginner" if (width, height, mine_count) == (9, 9, 10) else "custom",
        width=width,
        height=height,
        mine_count=mine_count,
        remaining_mines=mine_count,
        created_at=CREATED_AT,
    )


def _cell(game, row, column):
    return game.cells[row * game.width + column]


def _neighbours(game, row, column):
    result = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < game.height and 0 <= c < game.width:
                result.append(_cell(game, r, c))
    return result


def _mines_around(game, row, column):
    return sum(1 for n in _neighbours(game, row, column) if n["has_mine"])


def _arrange_playing(game, mine_positions):
    """Put the game into Playing with mines laid at the given positions and
    every cell's adjacent_mine_count consistent with that layout (as the
    product leaves the board right after laying mines)."""
    mines = set(mine_positions)
    for cell in game.cells:
        cell["has_mine"] = (cell["row"], cell["column"]) in mines
        cell["state"] = "Hidden"
    for cell in game.cells:
        cell["adjacent_mine_count"] = _mines_around(game, cell["row"], cell["column"])
    game.mine_count = len(mines)
    game.remaining_mines = len(mines)
    game.flags_placed = 0
    game.mines_laid = True
    game.status = "Playing"
    game.started_at = STARTED_AT


def _ring_at_distance_two(row, column):
    return [
        (r, c)
        for r in range(row - 2, row + 3)
        for c in range(column - 2, column + 3)
        if max(abs(r - row), abs(c - column)) == 2
    ]


def _ring_at_distance_one(row, column):
    return [
        (r, c)
        for r in range(row - 1, row + 2)
        for c in range(column - 1, column + 2)
        if (r, c) != (row, column)
    ]


def test_interior_cell_with_all_eight_neighbours_mined_shows_eight():
    game = _new_game()
    # Mines on all 8 neighbours of (4,4) and also on the 16 cells just beyond
    # them (distance 2): 24 mines on a 9x9 board.
    _arrange_playing(game, _ring_at_distance_one(4, 4) + _ring_at_distance_two(4, 4))

    game.open_cell(row=4, column=4)

    target = _cell(game, 4, 4)
    # (4,4) is safe and Hidden in a Playing game -> it becomes Opened.
    assert target["state"] == "Opened"
    # Its 8 neighbours (3..5, 3..5 minus itself) all hold mines -> K = 8, the
    # upper limit; the 16 mines at distance 2 are not neighbours and add nothing.
    assert target["adjacent_mine_count"] == 8
    # Count is 8 (non-zero) so no cascade; 57 safe cells remain Hidden -> not Won.
    assert game.status == "Playing"


def test_interior_cell_with_mines_only_just_beyond_its_neighbours_shows_zero():
    game = _new_game()
    # Mines only on the 16 cells at distance 2 from (4,4); none of its
    # 8 neighbours holds a mine.
    _arrange_playing(game, _ring_at_distance_two(4, 4))

    game.open_cell(row=4, column=4)

    target = _cell(game, 4, 4)
    # (4,4) is safe and Hidden in a Playing game -> Opened.
    assert target["state"] == "Opened"
    # None of its 8 neighbours holds a mine; the mines one step further out are
    # not neighbours -> K = 0, the lower limit.
    assert target["adjacent_mine_count"] == 0
    # The cascade opens the 8 neighbours, each touching the distance-2 ring
    # (count >= 1) so it stops there; the cells outside the ring stay Hidden,
    # so the game is still Playing and not Won.
    assert game.status == "Playing"
    for r, c in _ring_at_distance_one(4, 4):
        assert _cell(game, r, c)["state"] == "Opened"
        assert _cell(game, r, c)["adjacent_mine_count"] >= 1


def test_interior_cell_with_three_mined_neighbours_shows_three():
    game = _new_game()
    # Three of (4,4)'s neighbours hold mines; one more mine far away at (0,8).
    _arrange_playing(game, [(3, 3), (3, 5), (5, 4), (0, 8)])

    game.open_cell(row=4, column=4)

    target = _cell(game, 4, 4)
    # Mines among neighbours of (4,4): (3,3), (3,5), (5,4) -> K = 3;
    # (0,8) is not a neighbour.
    assert target["state"] == "Opened"
    assert target["adjacent_mine_count"] == 3
    # Non-zero count: no cascade, many safe cells still Hidden -> Playing.
    assert game.status == "Playing"


def test_counts_computed_on_first_open_match_mines_among_neighbours():
    # Dense custom board (64 mines on 9x9, the maximum) so that interior counts
    # span a wide range; repeated because the layout is random.
    for attempt in range(20):
        game = _new_game(width=9, height=9, mine_count=64)

        game.open_cell(row=4, column=4)

        # First open is safe; mines are laid and the game is Playing (or Won if
        # the cascade happened to open every safe cell, never Lost).
        assert game.status in ("Playing", "Won")
        assert sum(1 for c in game.cells if c["has_mine"]) == 64
        target = _cell(game, 4, 4)
        assert target["has_mine"] is False
        assert target["state"] == "Opened"
        # The opened interior cell's number is K, the mines among its 8
        # neighbours, which is between 0 and 8.
        expected = _mines_around(game, 4, 4)
        assert 0 <= expected <= 8
        assert target["adjacent_mine_count"] == expected
        # Every interior cell's number equals the mines among its 8 neighbours.
        for cell in game.cells:
            r, c = cell["row"], cell["column"]
            if 0 < r < game.height - 1 and 0 < c < game.width - 1:
                assert cell["adjacent_mine_count"] == _mines_around(game, r, c)
