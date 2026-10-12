from src.domain.game import Game

import pytest


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
TARGET = (4, 4)
# Nine mines far away from the target cell, along the bottom row.
FAR_MINES = [(8, c) for c in range(WIDTH)]


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield (r, c)


def _cell(game, row, column):
    return game.cells[row * WIDTH + column]


def _arrange_game(mine_pos, wrong_flag_pos):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    mines = set(FAR_MINES) | {mine_pos}
    assert len(mines) == MINE_COUNT

    cells = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": (r, c) in mines,
                    "adjacent_mine_count": sum(
                        1 for n in _neighbours(r, c) if n in mines
                    ),
                    "state": "Hidden",
                }
            )
    game.cells = cells

    # The target cell is Opened; every neighbour except the mine and the
    # wrongly flagged safe cell is already Opened too.
    _cell(game, *TARGET)["state"] = "Opened"
    for n in _neighbours(*TARGET):
        if n == mine_pos:
            continue
        if n == wrong_flag_pos:
            _cell(game, *n)["state"] = "Flagged"
        else:
            _cell(game, *n)["state"] = "Opened"

    game.status = "Playing"
    game.mines_laid = True
    game.flags_placed = 1
    game.remaining_mines = MINE_COUNT - 1
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 12
    game.ended_at = None
    game.struck_cell_id = None
    return game


@pytest.mark.parametrize(
    "mine_pos, wrong_flag_pos",
    [
        ((3, 3), (5, 5)),
        ((5, 5), (3, 3)),
    ],
)
def test_chord_with_wrong_flag_detonates_unflagged_mine_and_loses(
    mine_pos, wrong_flag_pos
):
    game = _arrange_game(mine_pos, wrong_flag_pos)

    # Target (4,4): among its 8 neighbours only mine_pos holds a mine
    # (the other mines are on row 8, out of reach), so N = 1.
    assert _cell(game, *TARGET)["adjacent_mine_count"] == 1
    # The wrongly flagged cell is a safe cell.
    assert _cell(game, *wrong_flag_pos)["has_mine"] is False

    game.chord_cell(row=TARGET[0], column=TARGET[1])

    # Flagged neighbours: exactly one (wrong_flag_pos) == N = 1, so the chord
    # applies. The only Hidden neighbour is mine_pos, which holds a mine, so
    # opening it makes it Detonated.
    mine_cell = _cell(game, *mine_pos)
    assert mine_cell["state"] == "Detonated"
    # The detonated cell is recorded as the struck cell.
    assert game.struck_cell_id == f"{mine_pos[0]}-{mine_pos[1]}"
    # Opening a mine while Playing makes the game Lost (Playing->Lost allowed).
    # No win is possible: the flagged safe cell is never opened.
    assert game.status == "Lost"
    # Ending the game sets ended_at.
    assert game.ended_at is not None
    # The timer freezes at its value when the loss happened.
    assert game.elapsed_seconds == 12
    # The wrongly placed flag stays Flagged: chording never opens flagged cells.
    assert _cell(game, *wrong_flag_pos)["state"] == "Flagged"
    # The chorded cell itself stays Opened.
    assert _cell(game, *TARGET)["state"] == "Opened"
    # Flag counters are untouched by a loss.
    assert game.flags_placed == 1
    assert game.remaining_mines == MINE_COUNT - 1
    # The far mines on row 8 were not neighbours of the target and stay Hidden.
    for pos in FAR_MINES:
        assert _cell(game, *pos)["state"] == "Hidden"
