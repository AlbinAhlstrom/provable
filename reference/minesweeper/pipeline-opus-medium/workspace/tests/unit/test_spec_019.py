import copy

import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Mines along the bottom row plus one at (7, 8): exactly 10 mines.
MINE_POSITIONS = {(8, c) for c in range(9)} | {(7, 8)}


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


def _cell(game, row, column):
    return game.cells[row * WIDTH + column]


def _lay_mines(cells):
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


def _new_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    game.cells = _blank_cells()
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.remaining_mines = MINE_COUNT
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    return game


def _ready_game():
    # Ready: no mines laid, every cell Hidden, nothing opened.
    return _new_game()


def _playing_game():
    # Playing: mines laid at MINE_POSITIONS, one numbered cell (7, 0) Opened.
    # Many safe cells remain Hidden, so the game is not Won.
    game = _new_game()
    _lay_mines(game.cells)
    game.mines_laid = True
    game.status = "Playing"
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 12
    _cell(game, 7, 0)["state"] = "Opened"
    return game


def _lost_game():
    # Lost: the mine at (8, 0) was opened and Detonated.
    game = _playing_game()
    game.status = "Lost"
    _cell(game, 8, 0)["state"] = "Detonated"
    game.struck_cell_id = "8-0"
    game.ended_at = "2024-01-01T10:00:17"
    return game


def _won_game():
    # Won: every safe cell Opened, every mine auto-flagged.
    game = _playing_game()
    for cell in game.cells:
        cell["state"] = "Flagged" if cell["has_mine"] else "Opened"
    game.status = "Won"
    game.flags_placed = MINE_COUNT
    game.remaining_mines = 0
    game.ended_at = "2024-01-01T10:00:40"
    return game


@pytest.mark.parametrize("make_game", [_ready_game, _playing_game], ids=["Ready", "Playing"])
def test_flagging_hidden_cell_flags_it_and_flagging_again_unflags_it(make_game):
    game = make_game()
    status_before = game.status
    other_cells_before = [copy.deepcopy(c) for c in game.cells if c["id"] != "0-0"]

    # (0, 0) is Hidden and has no mine; status is Ready or Playing, so the
    # toggle is allowed: Hidden -> Flagged, flags_placed 0 -> 1.
    game.toggle_flag(row=0, column=0)

    # Hidden -> Flagged.
    assert _cell(game, 0, 0)["state"] == "Flagged"
    # flags_placed 0 + 1 = 1.
    assert game.flags_placed == 1
    # remaining_mines = mine_count - flags_placed = 10 - 1 = 9.
    assert game.remaining_mines == 9
    # Flagging opens nothing and does not change status.
    assert game.status == status_before
    assert [c for c in game.cells if c["id"] != "0-0"] == other_cells_before

    # (0, 0) is now Flagged: toggling again returns it to Hidden, flags 1 -> 0.
    game.toggle_flag(row=0, column=0)

    # Flagged -> Hidden.
    assert _cell(game, 0, 0)["state"] == "Hidden"
    # flags_placed 1 - 1 = 0.
    assert game.flags_placed == 0
    # remaining_mines = 10 - 0 = 10.
    assert game.remaining_mines == 10
    assert game.status == status_before
    assert [c for c in game.cells if c["id"] != "0-0"] == other_cells_before


def test_flagging_opened_cell_in_playing_game_changes_nothing():
    game = _playing_game()
    before = game.to_dict()

    # (7, 0) is Opened (count 2); Opened -> Flagged is not an allowed cell
    # change, so the toggle is ignored without error.
    game.toggle_flag(row=7, column=0)

    # Cell stays Opened, flags_placed stays 0, remaining_mines stays 10.
    assert _cell(game, 7, 0)["state"] == "Opened"
    assert game.flags_placed == 0
    assert game.remaining_mines == 10
    assert game.to_dict() == before


@pytest.mark.parametrize("make_game", [_lost_game, _won_game], ids=["Lost", "Won"])
def test_flagging_in_finished_game_changes_nothing(make_game):
    game = make_game()
    target = _cell(game, 0, 0)
    state_before = target["state"]
    flags_before = game.flags_placed
    remaining_before = game.remaining_mines
    before = game.to_dict()

    # Status is Lost/Won (not Ready or Playing): the board is locked, so
    # toggling (0, 0) (Hidden in Lost, Opened in Won) is ignored without error.
    game.toggle_flag(row=0, column=0)

    # Cell, flag counter and remaining-mines counter are unchanged.
    assert _cell(game, 0, 0)["state"] == state_before
    assert game.flags_placed == flags_before
    assert game.remaining_mines == remaining_before
    assert game.to_dict() == before


def test_flagging_hidden_cell_in_lost_game_does_not_flag_it():
    game = _lost_game()

    # Same Hidden cell (0, 0) as the accepted Playing case; only status differs
    # (Lost). The toggle is ignored: it stays Hidden and flags stay 0.
    game.toggle_flag(row=0, column=0)

    assert _cell(game, 0, 0)["state"] == "Hidden"
    assert game.flags_placed == 0
    assert game.remaining_mines == 10
    assert game.status == "Lost"
