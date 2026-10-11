from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10

# Mine layout (exactly MINE_COUNT = 10 mines):
#   (3,3), (3,4): the two mines next to the chorded cell (4,4)
#   (6,2)..(6,6): a row of mines that makes the lower neighbours of (4,4) numbered,
#                 so that no cascade happens and the expected result stays simple
#   (0,8), (8,0), (8,8): far corners, filling up the mine count
MINES = {
    (3, 3), (3, 4),
    (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),
    (0, 8), (8, 0), (8, 8),
}

CHORD_CELL = (4, 4)
NEIGHBOURS_OF_CHORD = [
    (3, 3), (3, 4), (3, 5),
    (4, 3), (4, 5),
    (5, 3), (5, 4), (5, 5),
]


def _neighbours(row, column):
    result = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                result.append((r, c))
    return result


def _build_playing_game(flagged):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00Z",
    )
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            count = sum(1 for n in _neighbours(row, column) if n in MINES)
            if (row, column) == CHORD_CELL:
                state = "Opened"
            elif (row, column) in flagged:
                state = "Flagged"
            else:
                state = "Hidden"
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in MINES,
                    "adjacent_mine_count": count,
                    "state": state,
                }
            )
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05Z"
    game.elapsed_seconds = 5
    game.flags_placed = len(flagged)
    game.remaining_mines = MINE_COUNT - len(flagged)
    return game


def _states(game):
    return {(c["row"], c["column"]): c["state"] for c in game.cells}


def _cell(game, row, column):
    for c in game.cells:
        if c["row"] == row and c["column"] == column:
            return c
    raise AssertionError(f"cell {row}-{column} missing")


def test_arranged_board_is_as_worked_out():
    game = _build_playing_game(flagged={(3, 3), (3, 4)})
    # (4,4) neighbours: (3,3)M, (3,4)M, others safe -> N = 2
    assert _cell(game, 4, 4)["adjacent_mine_count"] == 2
    # (3,5): only (3,4) is a mine among its neighbours -> 1
    assert _cell(game, 3, 5)["adjacent_mine_count"] == 1
    # (4,3): (3,3)M, (3,4)M -> 2
    assert _cell(game, 4, 3)["adjacent_mine_count"] == 2
    # (4,5): (3,4)M -> 1
    assert _cell(game, 4, 5)["adjacent_mine_count"] == 1
    # (5,3): (6,2)M, (6,3)M, (6,4)M -> 3
    assert _cell(game, 5, 3)["adjacent_mine_count"] == 3
    # (5,4): (6,3)M, (6,4)M, (6,5)M -> 3
    assert _cell(game, 5, 4)["adjacent_mine_count"] == 3
    # (5,5): (6,4)M, (6,5)M, (6,6)M -> 3
    assert _cell(game, 5, 5)["adjacent_mine_count"] == 3
    assert len(game.cells) == WIDTH * HEIGHT
    assert sum(1 for c in game.cells if c["has_mine"]) == MINE_COUNT


def test_chord_with_exactly_n_flags_opens_all_hidden_unflagged_neighbours():
    # Exactly at the limit: N = 2 and exactly 2 flagged neighbours (the two real mines).
    game = _build_playing_game(flagged={(3, 3), (3, 4)})
    before = _states(game)

    game.chord_cell(row=4, column=4)

    after = _states(game)
    # Hidden unflagged neighbours of (4,4): (3,5), (4,3), (4,5), (5,3), (5,4), (5,5).
    # All are safe and all have adjacent_mine_count >= 1 (1, 2, 1, 3, 3, 3),
    # so each becomes Opened and no cascade spreads beyond them.
    for pos in [(3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)]:
        assert after[pos] == "Opened", pos

    # The flagged neighbours (3,3) and (3,4) stay Flagged (flagged cells are never opened).
    assert after[(3, 3)] == "Flagged"
    assert after[(3, 4)] == "Flagged"

    # The chorded cell itself stays Opened.
    assert after[(4, 4)] == "Opened"

    # Every other cell was Hidden, is not a neighbour of (4,4), and no cascade
    # happened (all newly opened cells are numbered) -> still Hidden.
    opened_now = {(3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)}
    for pos, state in before.items():
        if pos in opened_now:
            continue
        assert after[pos] == state, pos

    # No mine was opened -> no loss; many safe cells remain Hidden
    # (e.g. (0,0)) -> not Won. Status stays Playing.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    assert all(c["state"] != "Detonated" for c in game.cells)

    # Flags were not touched by the chord.
    assert game.flags_placed == 2
    assert game.remaining_mines == MINE_COUNT - 2


def test_chord_with_one_flag_fewer_than_n_changes_nothing():
    # Just beyond the limit (below): N = 2 but only 1 flagged neighbour.
    # Same board, same mines, only the flag on (3,4) is missing.
    game = _build_playing_game(flagged={(3, 3)})
    before = _states(game)

    game.chord_cell(row=4, column=4)

    # Flag count (1) differs from N (2) -> nothing changes; in particular the
    # unflagged mine (3,4) is not opened and nothing is detonated.
    assert _states(game) == before
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    assert game.flags_placed == 1
    assert game.remaining_mines == MINE_COUNT - 1


def test_chord_with_one_flag_more_than_n_changes_nothing():
    # Just beyond the limit (above): N = 2 but 3 flagged neighbours.
    # Same board, same mines, plus an extra flag on the safe neighbour (3,5).
    game = _build_playing_game(flagged={(3, 3), (3, 4), (3, 5)})
    before = _states(game)

    game.chord_cell(row=4, column=4)

    # Flag count (3) differs from N (2) -> nothing changes; the hidden
    # neighbours (4,3), (4,5), (5,3), (5,4), (5,5) stay Hidden.
    assert _states(game) == before
    for pos in [(4, 3), (4, 5), (5, 3), (5, 4), (5, 5)]:
        assert _states(game)[pos] == "Hidden", pos
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    assert game.flags_placed == 3
    assert game.remaining_mines == MINE_COUNT - 3
