from src.domain.game import Game


ROWS = 9
COLS = 9

# Mine layout: a full wall of mines down column 2 (9 mines) plus one more
# mine far away at (8, 8). Total = 10 = mine_count, as the fixed-mine-count rule requires.
MINES = {(r, 2) for r in range(ROWS)} | {(8, 8)}


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                yield r, c


def _make_playing_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=COLS,
        height=ROWS,
        mine_count=10,
        remaining_mines=10,
        created_at="2024-01-01T10:00:00",
    )
    # Put the game straight into Playing with mines already laid.
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.flags_placed = 0
    game.remaining_mines = 10
    game.elapsed_seconds = 3
    for cell in game.cells:
        r, c = cell["row"], cell["column"]
        cell["has_mine"] = (r, c) in MINES
        cell["adjacent_mine_count"] = sum(1 for n in _neighbours(r, c) if n in MINES)
        cell["state"] = "Hidden"
    return game


def _cell(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"cell {row},{column} missing")


def test_arranged_counts_are_as_expected():
    game = _make_playing_game()
    # Column 0 never touches column 2, so every column-0 cell has count 0.
    for r in range(ROWS):
        assert _cell(game, r, 0)["adjacent_mine_count"] == 0
    # Column 1 touches the wall: corners of the column see 2 mines, others 3.
    assert _cell(game, 0, 1)["adjacent_mine_count"] == 2
    assert _cell(game, 4, 1)["adjacent_mine_count"] == 3
    assert _cell(game, 8, 1)["adjacent_mine_count"] == 2


import pytest


@pytest.mark.parametrize("start_row", [0, 4])
def test_opening_a_zero_cell_cascades_through_zeros_to_numbered_border(start_row):
    game = _make_playing_game()

    game.open_cell(row=start_row, column=0)

    # The opened cell (start_row, 0) is safe with count 0 -> Opened.
    # Its hidden neighbours in column 0 (rows start_row±1) are zeros, so each
    # opens its own neighbours in turn; the chain runs the whole length of
    # column 0 (rows 0..8), all of which have count 0.
    for r in range(ROWS):
        assert _cell(game, r, 0)["state"] == "Opened", f"cell {r}-0 should be opened"

    # Every column-1 cell is a neighbour of some opened zero in column 0,
    # so each is opened. They are numbered (2 or 3), so they do not cascade further.
    for r in range(ROWS):
        assert _cell(game, r, 1)["state"] == "Opened", f"cell {r}-1 should be opened"

    # Column 2 holds mines; they are only reachable via numbered column-1 cells,
    # which do not cascade, so they stay Hidden (none Detonated).
    for r in range(ROWS):
        assert _cell(game, r, 2)["state"] == "Hidden"

    # Columns 3..8 lie beyond the mine wall: nothing opened reaches them.
    for r in range(ROWS):
        for c in range(3, COLS):
            assert _cell(game, r, c)["state"] == "Hidden", f"cell {r}-{c} should stay hidden"

    # Safe cells in columns 3..8 remain unopened, so the game is not Won;
    # no mine was opened, so it is not Lost either.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    assert game.flags_placed == 0
    assert game.remaining_mines == 10
