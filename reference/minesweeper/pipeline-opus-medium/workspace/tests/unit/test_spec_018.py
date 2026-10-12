import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Ten mines: the whole bottom row (row 8) plus (7, 8).
MINES = {(8, c) for c in range(WIDTH)} | {(7, 8)}


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _build_playing_game(flagged):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            count = sum(1 for n in _neighbours(row, column) if n in MINES)
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in MINES,
                    "adjacent_mine_count": count,
                    "state": "Flagged" if (row, column) == flagged else "Hidden",
                }
            )
    game.cells = cells
    game.mines_laid = True
    game.status = "Playing"
    game.started_at = "2024-01-01T10:00:05"
    game.flags_placed = 1
    game.remaining_mines = MINE_COUNT - 1
    game.elapsed_seconds = 5
    return game


def _cell(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"cell {row}-{column} missing")


@pytest.mark.parametrize(
    "flagged, opened_beyond",
    [
        # Flag on a direct neighbour of the opened zero cell (0,0).
        ((0, 1), (0, 2)),
        # Flag deep inside the zero region, reached only by repeated cascading.
        ((3, 3), (4, 4)),
    ],
)
def test_cascade_skips_flagged_cell(flagged, opened_beyond):
    game = _build_playing_game(flagged)
    fr, fc = flagged

    # Sanity of the arrangement: the flagged cell is safe, has count 0 and
    # sits among zero cells, so an unrestrained cascade would open it.
    assert _cell(game, fr, fc)["has_mine"] is False
    assert _cell(game, fr, fc)["adjacent_mine_count"] == 0
    assert _cell(game, 0, 0)["adjacent_mine_count"] == 0

    game.open_cell(row=0, column=0)

    # (0,0) is a safe Hidden cell with no mines among its neighbours
    # (mines are only in row 8 and at (7,8)), so it becomes Opened.
    assert _cell(game, 0, 0)["state"] == "Opened"

    # Rows 0-6 (except (6,7),(6,8)) have count 0, so the cascade spreads
    # through all of them and reaches every neighbour of the flagged cell.
    # The flagged cell is skipped: it stays Flagged and is not opened.
    assert _cell(game, fr, fc)["state"] == "Flagged"

    # The cascade flows around the flag: a zero cell on the far side of the
    # flagged cell is still opened via other zero cells.
    assert _cell(game, opened_beyond[0], opened_beyond[1])["state"] == "Opened"

    # Every neighbour of the flagged cell is a safe cell reached by the
    # cascade (each touches some zero cell other than the flagged one).
    for r, c in _neighbours(fr, fc):
        assert _cell(game, r, c)["state"] == "Opened"

    # The flag is untouched, so the counters are unchanged: 1 flag, 10 - 1 = 9.
    assert game.flags_placed == 1
    assert game.remaining_mines == MINE_COUNT - 1

    # The flagged safe cell is still unopened, so not every non-mine cell is
    # Opened: the game is not Won, and no mine was opened, so not Lost.
    assert game.status == "Playing"
    assert game.struck_cell_id is None

    # No mine cell was touched by the cascade.
    for (r, c) in MINES:
        assert _cell(game, r, c)["state"] == "Hidden"
