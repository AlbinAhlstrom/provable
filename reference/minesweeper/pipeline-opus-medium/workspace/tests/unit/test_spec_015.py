import pytest

from src.domain.game import Game


WIDTH = 12
HEIGHT = 9
MINE_COUNT = 60
CREATED_AT = "2024-01-01T10:00:00+00:00"
FIRST_OPEN = (4, 6)
RUNS = 15


def _new_game(index):
    return Game(
        id=f"game-{index}",
        difficulty_id="custom",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at=CREATED_AT,
    )


def _cell_at(game, row, column):
    matches = [c for c in game.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


def _existing_neighbours(row, column):
    result = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                result.append((r, c))
    return result


def _expected_count(game, row, column):
    return sum(1 for (r, c) in _existing_neighbours(row, column) if _cell_at(game, r, c)["has_mine"])


@pytest.mark.parametrize(
    "row, column, neighbour_total",
    [
        # corners: exactly 3 existing neighbours
        (0, 0, 3),
        (0, WIDTH - 1, 3),
        (HEIGHT - 1, 0, 3),
        (HEIGHT - 1, WIDTH - 1, 3),
        # edges (one per side): exactly 5 existing neighbours
        (0, 5, 5),
        (HEIGHT - 1, 5, 5),
        (4, 0, 5),
        (4, WIDTH - 1, 5),
        # one step in from the corner / edge: all 8 neighbours exist
        (1, 1, 8),
        (1, 5, 8),
    ],
)
def test_adjacent_count_only_counts_neighbours_inside_the_grid(row, column, neighbour_total):
    # The neighbour-geometry itself: corners have 3, edges 5, the next cell in has 8.
    assert len(_existing_neighbours(row, column)) == neighbour_total

    for index in range(RUNS):
        game = _new_game(index)

        # Ready game, no mines yet; the first open lays 60 mines at random on
        # the 107 other cells and then sets every cell's adjacent_mine_count.
        game.open_cell(row=FIRST_OPEN[0], column=FIRST_OPEN[1])

        # Mines were laid: exactly MINE_COUNT cells hold a mine, the opened one is safe.
        assert len(game.cells) == WIDTH * HEIGHT
        assert sum(1 for c in game.cells if c["has_mine"]) == MINE_COUNT
        assert _cell_at(game, FIRST_OPEN[0], FIRST_OPEN[1])["has_mine"] is False

        cell = _cell_at(game, row, column)
        # Expected: number of mines among only the neighbours that exist in the
        # 12x9 grid (no wrap-around to the opposite side, the cell itself excluded),
        # so it can never exceed the number of existing neighbours.
        expected = _expected_count(game, row, column)
        assert cell["adjacent_mine_count"] == expected
        assert 0 <= cell["adjacent_mine_count"] <= neighbour_total


def test_every_cell_count_matches_mines_among_existing_neighbours():
    for index in range(RUNS):
        game = _new_game(100 + index)

        game.open_cell(row=FIRST_OPEN[0], column=FIRST_OPEN[1])

        for cell in game.cells:
            r, c = cell["row"], cell["column"]
            # For every cell (corner, edge or interior) the count equals the
            # mines among its existing neighbours: 3 for corners, 5 for edges,
            # 8 for interior cells are the only positions considered.
            assert cell["adjacent_mine_count"] == _expected_count(game, r, c)
            assert cell["adjacent_mine_count"] <= len(_existing_neighbours(r, c))
