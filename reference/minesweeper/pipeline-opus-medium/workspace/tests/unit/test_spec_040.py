import copy

import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Exactly MINE_COUNT mines: the whole bottom row (9 mines) plus (7, 0).
MINES = {(8, c) for c in range(WIDTH)} | {(7, 0)}


def _count_adjacent(row, column):
    total = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH and (r, c) in MINES:
                total += 1
    return total


def _make_playing_game(opened_cells):
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
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in MINES,
                    "adjacent_mine_count": _count_adjacent(row, column),
                    "state": "Opened" if (row, column) in opened_cells else "Hidden",
                }
            )
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    game.flags_placed = 0
    game.remaining_mines = MINE_COUNT
    game.elapsed_seconds = 12
    game.started_at = "2024-01-01T10:00:05"
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


@pytest.mark.parametrize(
    "row, column, expected_count",
    [
        # (7, 4): neighbours (8,3), (8,4), (8,5) are mines -> numbered cell with 3.
        (7, 4, 3),
        # (2, 2): no mine anywhere near rows 1-3 -> zero cell whose neighbours are Hidden.
        (2, 2, 0),
    ],
)
def test_opening_an_opened_cell_changes_nothing(row, column, expected_count):
    game = _make_playing_game(opened_cells={(row, column)})
    assert _cell(game, row, column)["adjacent_mine_count"] == expected_count
    cells_before = copy.deepcopy(game.cells)
    events_before = copy.deepcopy(game.events)

    # No exception must be raised: the action is silently ignored.
    game.open_cell(row=row, column=column)

    # The target cell was already Opened; Opened is a terminal cell state, so it stays Opened.
    assert _cell(game, row, column)["state"] == "Opened"
    # Ignoring the action means no cascade (even for the zero cell with Hidden neighbours),
    # no cell changes at all: every cell dict is identical to before.
    assert game.cells == cells_before
    # Status stays Playing: 70 non-mine cells, only 1 Opened, so no win; no mine opened, no loss.
    assert game.status == "Playing"
    # Counters, timer and end markers are untouched.
    assert game.flags_placed == 0
    assert game.remaining_mines == MINE_COUNT
    assert game.elapsed_seconds == 12
    assert game.mines_laid is True
    assert game.started_at == "2024-01-01T10:00:05"
    assert game.ended_at is None
    assert game.struck_cell_id is None
    # No message / event is produced.
    assert game.events == events_before


def test_opening_a_hidden_cell_does_change_it_for_contrast():
    # Same board, same already-opened cell (7, 4); this time the player opens Hidden (7, 5).
    game = _make_playing_game(opened_cells={(7, 4)})
    assert _cell(game, 7, 5)["state"] == "Hidden"

    game.open_cell(row=7, column=5)

    # (7, 5) is safe with neighbours (8,4), (8,5), (8,6) mined -> count 3, so it becomes Opened
    # and does not cascade.
    assert _cell(game, 7, 5)["state"] == "Opened"
    assert _cell(game, 7, 5)["adjacent_mine_count"] == 3
    # Its Hidden neighbours, e.g. (6, 5), are not opened because it is a numbered cell.
    assert _cell(game, 6, 5)["state"] == "Hidden"
    # 2 of 71 safe cells opened: still Playing, no mine struck.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
