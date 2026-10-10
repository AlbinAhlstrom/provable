import copy

import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINES = 10
# Mines along the whole top row plus the first cell of the second row: 10 mines.
MINE_POSITIONS = {(0, c) for c in range(9)} | {(1, 0)}


def _adjacent(row, column):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH and (r, c) in MINE_POSITIONS:
                count += 1
    return count


def _fresh_cells():
    return [
        {
            "id": f"{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for r in range(HEIGHT)
        for c in range(WIDTH)
    ]


def _mined_cells():
    cells = _fresh_cells()
    for cell in cells:
        pos = (cell["row"], cell["column"])
        cell["has_mine"] = pos in MINE_POSITIONS
        cell["adjacent_mine_count"] = _adjacent(*pos)
    return cells


def _cell(cells, row, column):
    return cells[row * WIDTH + column]


def _game_in(status):
    game = Game(
        id="g1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINES,
        remaining_mines=MINES,
        created_at="2024-01-01T10:00:00Z",
    )
    game.events = []
    if status == "Ready":
        game.status = "Ready"
        game.mines_laid = False
        game.flags_placed = 0
        game.remaining_mines = MINES
        game.elapsed_seconds = 0
        game.started_at = None
        game.ended_at = None
        game.struck_cell_id = None
        game.cells = _fresh_cells()
    elif status == "Playing":
        game.status = "Playing"
        game.mines_laid = True
        cells = _mined_cells()
        _cell(cells, 8, 8)["state"] = "Opened"
        _cell(cells, 0, 0)["state"] = "Flagged"
        game.cells = cells
        game.flags_placed = 1
        game.remaining_mines = MINES - 1
        game.elapsed_seconds = 42
        game.started_at = "2024-01-01T10:01:00Z"
        game.ended_at = None
        game.struck_cell_id = None
    elif status == "Lost":
        game.status = "Lost"
        game.mines_laid = True
        cells = _mined_cells()
        _cell(cells, 8, 8)["state"] = "Opened"
        _cell(cells, 0, 1)["state"] = "Detonated"
        game.cells = cells
        game.flags_placed = 0
        game.remaining_mines = MINES
        game.elapsed_seconds = 17
        game.started_at = "2024-01-01T10:01:00Z"
        game.ended_at = "2024-01-01T10:01:17Z"
        game.struck_cell_id = "0-1"
    elif status == "Won":
        game.status = "Won"
        game.mines_laid = True
        cells = _mined_cells()
        for cell in cells:
            cell["state"] = "Flagged" if cell["has_mine"] else "Opened"
        game.cells = cells
        game.flags_placed = MINES
        game.remaining_mines = 0
        game.elapsed_seconds = 88
        game.started_at = "2024-01-01T10:01:00Z"
        game.ended_at = "2024-01-01T10:02:28Z"
        game.struck_cell_id = None
    elif status == "Abandoned":
        game.status = "Abandoned"
        game.mines_laid = True
        cells = _mined_cells()
        _cell(cells, 8, 8)["state"] = "Opened"
        _cell(cells, 0, 0)["state"] = "Flagged"
        game.cells = cells
        game.flags_placed = 1
        game.remaining_mines = MINES - 1
        game.elapsed_seconds = 30
        game.started_at = "2024-01-01T10:01:00Z"
        game.ended_at = "2024-01-01T10:01:30Z"
        game.struck_cell_id = None
    return game


def _snapshot(game):
    return copy.deepcopy(
        {
            "id": game.id,
            "difficulty_id": game.difficulty_id,
            "width": game.width,
            "height": game.height,
            "mine_count": game.mine_count,
            "remaining_mines": game.remaining_mines,
            "created_at": game.created_at,
            "status": game.status,
            "mines_laid": game.mines_laid,
            "flags_placed": game.flags_placed,
            "elapsed_seconds": game.elapsed_seconds,
            "started_at": game.started_at,
            "ended_at": game.ended_at,
            "struck_cell_id": game.struck_cell_id,
            "cells": game.cells,
            "events": game.events,
        }
    )


# Each refused configuration is paired below with an accepted one differing only
# in the single value that crosses the limit.
REFUSED = [
    pytest.param(8, 9, 10, id="width-below-9"),
    pytest.param(31, 9, 10, id="width-above-30"),
    pytest.param(9, 8, 10, id="height-below-9"),
    pytest.param(9, 25, 10, id="height-above-24"),
    pytest.param(9, 9, 9, id="mines-below-10"),
    pytest.param(9, 9, 65, id="mines-above-(9-1)x(9-1)=64"),
]

ACCEPTED = [
    pytest.param(9, 9, 10, id="width-exactly-9"),
    pytest.param(30, 9, 10, id="width-exactly-30"),
    pytest.param(9, 9, 10, id="height-exactly-9"),
    pytest.param(9, 24, 10, id="height-exactly-24"),
    pytest.param(9, 9, 10, id="mines-exactly-10"),
    pytest.param(9, 9, 64, id="mines-exactly-64"),
]

STATUSES = ["Ready", "Playing", "Won", "Lost", "Abandoned"]


@pytest.mark.parametrize("status", STATUSES)
@pytest.mark.parametrize("width,height,mine_count", REFUSED)
def test_invalid_custom_is_refused_and_leaves_game_unchanged(
    status, width, height, mine_count
):
    game = _game_in(status)
    before = _snapshot(game)

    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="custom",
            width=width,
            height=height,
            mine_count=mine_count,
        )

    # The value lies outside width 9–30, height 9–24 or mines 10–(W−1)×(H−1),
    # so the configuration is refused with InvalidConfigurationError.
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    # A validation message is shown to the player: it is not empty.
    assert str(exc_info.value).strip() != ""

    # A refused configuration does not alter or abandon the game: status,
    # every cell (state, mine, count), timer, flags and counter are exactly
    # as they were before the call.
    after = _snapshot(game)
    assert after["status"] == status
    assert after["cells"] == before["cells"]
    assert after["elapsed_seconds"] == before["elapsed_seconds"]
    assert after["remaining_mines"] == before["remaining_mines"]
    assert after["flags_placed"] == before["flags_placed"]
    assert after == before


@pytest.mark.parametrize("width,height,mine_count", ACCEPTED)
def test_custom_exactly_at_limits_is_accepted(width, height, mine_count):
    game = _game_in("Ready")

    new_game = game.change_difficulty(
        difficulty_id="custom",
        width=width,
        height=height,
        mine_count=mine_count,
    )

    # Every value is within its inclusive limits, so no error is raised and a
    # new game with the chosen configuration is returned in its starting state.
    assert new_game.id != game.id
    assert new_game.difficulty_id == "custom"
    assert new_game.width == width
    assert new_game.height == height
    assert new_game.mine_count == mine_count
    assert new_game.status == "Ready"
    assert new_game.elapsed_seconds == 0
    assert new_game.flags_placed == 0
    assert new_game.remaining_mines == mine_count
    assert len(new_game.cells) == width * height
    assert all(cell["state"] == "Hidden" for cell in new_game.cells)
    # The valid choice abandons the previous Ready game.
    assert game.status == "Abandoned"
