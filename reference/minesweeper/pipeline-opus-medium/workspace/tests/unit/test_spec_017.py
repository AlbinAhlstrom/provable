from src.domain.game import Game

import pytest


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _make_playing_game(mines):
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
            count = sum(1 for n in _neighbours(row, column) if n in mines)
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in mines,
                    "adjacent_mine_count": count,
                    "state": "Hidden",
                }
            )
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.flags_placed = 0
    game.remaining_mines = MINE_COUNT
    return game


def _cell(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"cell {row}-{column} missing")


@pytest.mark.parametrize(
    "gap_column, extra_mines",
    [
        (0, [(8, 7), (8, 8)]),
        (8, [(8, 0), (8, 1)]),
    ],
)
def test_cascade_opens_numbered_cells_but_does_not_propagate_from_them(gap_column, extra_mines):
    # Wall of mines across row 4 except one safe "gap" cell, plus two far mines on row 8.
    mines = {(4, c) for c in range(WIDTH) if c != gap_column}
    mines.update(extra_mines)
    assert len(mines) == MINE_COUNT
    game = _make_playing_game(mines)

    # (0,4): no mine in rows 0-1 around it, count 0 -> starts a cascade.
    game.open_cell(row=0, column=4)

    # Rows 0..2: no mine neighbours (nearest mines are on row 4), all count 0,
    # so the cascade opens all of them and keeps spreading into row 3.
    for row in range(0, 3):
        for column in range(WIDTH):
            cell = _cell(game, row, column)
            assert cell["adjacent_mine_count"] == 0
            assert cell["state"] == "Opened"

    # Row 3: every cell touches at least one row-4 mine (the gap-adjacent corner
    # cell touches the neighbouring wall mine), so each is numbered (>=1).
    # They are opened by the cascade because a zero cell in row 2 touches them.
    for column in range(WIDTH):
        cell = _cell(game, 3, column)
        assert cell["adjacent_mine_count"] >= 1
        assert cell["state"] == "Opened"

    # The gap cell (4, gap_column) is safe with count >= 1; its only opened
    # neighbours are row-3 numbered cells, which must not propagate the cascade,
    # so it stays Hidden.
    gap = _cell(game, 4, gap_column)
    assert gap["has_mine"] is False
    assert _cell(game, 3, gap_column)["adjacent_mine_count"] == 1
    assert gap["state"] == "Hidden"

    # Everything at row 4 and below is reachable only through numbered cells
    # (or is a mine), so nothing there is opened or detonated.
    for row in range(4, HEIGHT):
        for column in range(WIDTH):
            assert _cell(game, row, column)["state"] == "Hidden"

    # Safe cells remain hidden (gap + rows 5..8 non-mines), so no win; no mine
    # was opened, so no loss. No flags involved.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    assert game.flags_placed == 0
    assert game.remaining_mines == MINE_COUNT
