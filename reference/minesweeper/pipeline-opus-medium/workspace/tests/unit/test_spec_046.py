import copy

import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINES = 10
# Ten mines: the whole bottom row (row 8) plus the cell (7, 8).
MINE_POSITIONS = {(8, c) for c in range(WIDTH)} | {(7, 8)}


def _blank_cells():
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
    cells = _blank_cells()
    for cell in cells:
        cell["has_mine"] = (cell["row"], cell["column"]) in MINE_POSITIONS
    for cell in cells:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                if (cell["row"] + dr, cell["column"] + dc) in MINE_POSITIONS:
                    count += 1
        cell["adjacent_mine_count"] = count
    return cells


def _new_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINES,
        remaining_mines=MINES,
        created_at="2024-01-01T10:00:00",
    )
    return game


def _ready_game():
    game = _new_game()
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.remaining_mines = MINES
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.cells = _blank_cells()
    game.events = []
    return game


def _playing_game():
    game = _new_game()
    game.status = "Playing"
    game.mines_laid = True
    game.cells = _mined_cells()
    # One safe cell opened (0-0 has no mine nearby) and one flag on a mine.
    game.cells[0]["state"] = "Opened"
    game.cells[8 * WIDTH + 0]["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = MINES - 1
    game.elapsed_seconds = 42
    game.started_at = "2024-01-01T10:00:05"
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    return game


def _won_game():
    game = _new_game()
    game.status = "Won"
    game.mines_laid = True
    game.cells = _mined_cells()
    for cell in game.cells:
        cell["state"] = "Flagged" if cell["has_mine"] else "Opened"
    game.flags_placed = MINES
    game.remaining_mines = 0
    game.elapsed_seconds = 77
    game.started_at = "2024-01-01T10:00:05"
    game.ended_at = "2024-01-01T10:01:22"
    game.struck_cell_id = None
    game.events = []
    return game


def _lost_game():
    game = _new_game()
    game.status = "Lost"
    game.mines_laid = True
    game.cells = _mined_cells()
    game.cells[0]["state"] = "Opened"
    game.cells[8 * WIDTH + 4]["state"] = "Detonated"
    game.struck_cell_id = "8-4"
    game.flags_placed = 0
    game.remaining_mines = MINES
    game.elapsed_seconds = 13
    game.started_at = "2024-01-01T10:00:05"
    game.ended_at = "2024-01-01T10:00:18"
    game.events = []
    return game


@pytest.mark.parametrize("make_game", [_ready_game, _playing_game], ids=["Ready", "Playing"])
def test_closing_a_game_in_progress_abandons_it_and_records_nothing(make_game):
    game = make_game()
    cells_before = copy.deepcopy(game.cells)
    elapsed_before = game.elapsed_seconds
    flags_before = game.flags_placed
    remaining_before = game.remaining_mines

    game.abandon_game()

    # Status was Ready/Playing; Ready/Playing -> Abandoned is an allowed transition.
    assert game.status == "Abandoned"
    # Abandoning sets ended_at (it was None before).
    assert game.ended_at is not None
    # Timer freezes at the value it had (0 for Ready, 42 for Playing).
    assert game.elapsed_seconds == elapsed_before
    # Closing touches no cell, flag or counter.
    assert game.cells == cells_before
    assert game.flags_placed == flags_before
    assert game.remaining_mines == remaining_before
    # Nothing is scored: no best-time record among the events.
    assert all("best" not in repr(e).lower() for e in game.events)


@pytest.mark.parametrize("make_game", [_ready_game, _playing_game], ids=["Ready", "Playing"])
def test_abandoned_game_timer_stays_frozen(make_game):
    game = make_game()
    elapsed_before = game.elapsed_seconds

    game.abandon_game()
    game.tick()

    # tick only advances while Playing; the game is now Abandoned, so the
    # elapsed time stays at the value it had when it was closed.
    assert game.status == "Abandoned"
    assert game.elapsed_seconds == elapsed_before


@pytest.mark.parametrize("make_game,status", [(_won_game, "Won"), (_lost_game, "Lost")], ids=["Won", "Lost"])
def test_closing_a_finished_game_keeps_its_outcome(make_game, status):
    game = make_game()
    snapshot = copy.deepcopy(game.to_dict()) if False else None  # to_dict not relied on
    cells_before = copy.deepcopy(game.cells)
    ended_before = game.ended_at
    elapsed_before = game.elapsed_seconds
    struck_before = game.struck_cell_id
    flags_before = game.flags_placed
    remaining_before = game.remaining_mines

    # Won/Lost -> Abandoned is not an allowed transition, but closing is an
    # ignored player action here: no error is raised.
    game.abandon_game()

    assert snapshot is None
    # Outcome kept.
    assert game.status == status
    assert game.ended_at == ended_before
    assert game.elapsed_seconds == elapsed_before
    assert game.struck_cell_id == struck_before
    assert game.cells == cells_before
    assert game.flags_placed == flags_before
    assert game.remaining_mines == remaining_before


def test_closing_an_already_abandoned_game_changes_nothing():
    game = _playing_game()
    game.abandon_game()
    ended_first = game.ended_at
    elapsed_first = game.elapsed_seconds
    cells_first = copy.deepcopy(game.cells)

    # Abandoned is terminal; closing again is ignored without error.
    game.abandon_game()

    assert game.status == "Abandoned"
    assert game.ended_at == ended_first
    assert game.elapsed_seconds == elapsed_first
    assert game.cells == cells_first
