import copy

import pytest

from src.domain.game import Game


CREATED_AT = "2024-01-01T10:00:00"
STARTED_AT = "2024-01-01T10:00:05"
ENDED_AT = "2024-01-01T10:01:00"

# Ten mines: the whole bottom row (row 8, columns 0..8) plus (7, 8).
MINE_POSITIONS = {(8, c) for c in range(9)} | {(7, 8)}


def _make_cells(width, height):
    return [
        {
            "id": f"{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for row in range(height)
        for column in range(width)
    ]


def _new_beginner_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at=CREATED_AT,
    )
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.cells = _make_cells(9, 9)
    game.events = []
    return game


def _lay_mines(game):
    game.mines_laid = True
    for cell in game.cells:
        cell["has_mine"] = (cell["row"], cell["column"]) in MINE_POSITIONS
    for cell in game.cells:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                if (cell["row"] + dr, cell["column"] + dc) in MINE_POSITIONS:
                    count += 1
        cell["adjacent_mine_count"] = count


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


def _arrange_ready():
    return _new_beginner_game()


def _arrange_playing():
    game = _new_beginner_game()
    _lay_mines(game)
    # (0,0) is far from every mine: its count is 0; opened as the first cell.
    _cell(game, 0, 0)["state"] = "Opened"
    game.status = "Playing"
    game.started_at = STARTED_AT
    game.elapsed_seconds = 42
    return game


def _arrange_won():
    game = _new_beginner_game()
    _lay_mines(game)
    for cell in game.cells:
        cell["state"] = "Flagged" if cell["has_mine"] else "Opened"
    game.status = "Won"
    game.started_at = STARTED_AT
    game.ended_at = ENDED_AT
    game.elapsed_seconds = 55
    game.flags_placed = 10
    game.remaining_mines = 0
    return game


def _arrange_lost():
    game = _new_beginner_game()
    _lay_mines(game)
    _cell(game, 0, 0)["state"] = "Opened"
    _cell(game, 8, 0)["state"] = "Detonated"
    game.status = "Lost"
    game.struck_cell_id = "8-0"
    game.started_at = STARTED_AT
    game.ended_at = ENDED_AT
    game.elapsed_seconds = 55
    return game


def _arrange_abandoned():
    game = _arrange_playing()
    game.status = "Abandoned"
    game.ended_at = ENDED_AT
    return game


@pytest.mark.parametrize(
    "arrange, elapsed_before",
    [(_arrange_ready, 0), (_arrange_playing, 42)],
    ids=["Ready", "Playing"],
)
def test_abandon_from_ready_or_playing_becomes_abandoned(arrange, elapsed_before):
    game = arrange()
    cells_before = copy.deepcopy(game.cells)

    game.abandon_game()

    # Ready and Playing are the only statuses allowed to go to Abandoned,
    # and the arranged game is in one of them, so it becomes Abandoned.
    assert game.status == "Abandoned"
    # Abandoning records the end of the game: ended_at was None, now set.
    assert game.ended_at is not None
    # Abandoning freezes the timer at its value: 0 for Ready, 42 for Playing.
    assert game.elapsed_seconds == elapsed_before
    # Leaving the game does not open, flag or reveal any cell.
    assert game.cells == cells_before


@pytest.mark.parametrize(
    "arrange", [_arrange_ready, _arrange_playing], ids=["Ready", "Playing"]
)
def test_abandoned_game_timer_stays_frozen(arrange):
    game = arrange()
    game.abandon_game()
    frozen = game.elapsed_seconds

    game.tick()

    # tick only advances while Playing; the game is now Abandoned, so the
    # elapsed seconds stay at the value they had when abandoned.
    assert game.status == "Abandoned"
    assert game.elapsed_seconds == frozen


@pytest.mark.parametrize(
    "arrange, final_status",
    [(_arrange_won, "Won"), (_arrange_lost, "Lost"), (_arrange_abandoned, "Abandoned")],
    ids=["Won", "Lost", "Abandoned"],
)
def test_abandon_from_final_status_changes_nothing(arrange, final_status):
    game = arrange()
    cells_before = copy.deepcopy(game.cells)
    flags_before = game.flags_placed
    remaining_before = game.remaining_mines
    struck_before = game.struck_cell_id

    # Must not raise: an abandon of a finished game is silently ignored.
    game.abandon_game()

    # Won/Lost/Abandoned -> Abandoned is not an allowed transition, so the
    # outcome is kept exactly as it was.
    assert game.status == final_status
    # The end time recorded at the finish is not overwritten.
    assert game.ended_at == ENDED_AT
    # The frozen timer, the counters and the struck cell stay as arranged.
    assert game.elapsed_seconds == (42 if final_status == "Abandoned" else 55)
    assert game.flags_placed == flags_before
    assert game.remaining_mines == remaining_before
    assert game.struck_cell_id == struck_before
    # No cell changes state.
    assert game.cells == cells_before
