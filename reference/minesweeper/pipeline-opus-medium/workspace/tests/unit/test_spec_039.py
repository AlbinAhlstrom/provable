import copy

import pytest

from src.domain.game import Game

WIDTH = 9
HEIGHT = 9
MINES = {(0, 0), (0, 2)} | {(8, c) for c in range(1, 9)}  # exactly 10 mines


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _build_cells():
    cells = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            count = sum(1 for n in _neighbours(r, c) if n in MINES)
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": (r, c) in MINES,
                    "adjacent_mine_count": count,
                    "state": "Hidden",
                }
            )
    return cells


def _cell(game, row, column):
    return game.cells[row * WIDTH + column]


def _new_game():
    return Game(
        id="g1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=10,
        remaining_mines=10,
        created_at="2024-01-01T10:00:00",
    )


def _arrange_lost_like(game):
    # Mines at (0,0), (0,2) and (8,1..8). (0,0) and (0,2) Flagged,
    # (1,1) Opened with count 2 (its mine neighbours are exactly (0,0), (0,2)).
    # Every other cell Hidden.
    game.cells = _build_cells()
    game.mines_laid = True
    _cell(game, 0, 0)["state"] = "Flagged"
    _cell(game, 0, 2)["state"] = "Flagged"
    _cell(game, 1, 1)["state"] = "Opened"
    game.flags_placed = 2
    game.remaining_mines = 8
    game.elapsed_seconds = 42
    game.started_at = "2024-01-01T10:00:05"


def _arrange_lost(game):
    _arrange_lost_like(game)
    # The struck mine (8,8) is Detonated.
    _cell(game, 8, 8)["state"] = "Detonated"
    game.struck_cell_id = "8-8"
    game.status = "Lost"
    game.ended_at = "2024-01-01T10:00:47"


def _arrange_won(game):
    game.cells = _build_cells()
    game.mines_laid = True
    # Every non-mine cell Opened, every mine Flagged (auto-flag on win).
    for cell in game.cells:
        cell["state"] = "Flagged" if cell["has_mine"] else "Opened"
    game.flags_placed = 10
    game.remaining_mines = 0
    game.elapsed_seconds = 42
    game.started_at = "2024-01-01T10:00:05"
    game.ended_at = "2024-01-01T10:00:47"
    game.status = "Won"


def _snapshot(game):
    return (
        copy.deepcopy(game.cells),
        game.status,
        game.mines_laid,
        game.mine_count,
        game.flags_placed,
        game.remaining_mines,
        game.elapsed_seconds,
        game.started_at,
        game.ended_at,
        game.struck_cell_id,
        game.id,
        game.difficulty_id,
        game.width,
        game.height,
    )


@pytest.mark.parametrize(
    "arrange, status",
    [(_arrange_won, "Won"), (_arrange_lost, "Lost")],
)
def test_finished_board_ignores_open_flag_chord_and_tick(arrange, status):
    game = _new_game()
    arrange(game)
    before = _snapshot(game)

    # (4,4): safe cell (no mine among (3..5,3..5)); in Lost it is Hidden and an
    #   open would reveal it; in Won it is Opened. Board locked -> ignored.
    game.open_cell(row=4, column=4)
    # (8,1): mine; Hidden in Lost (would detonate), Flagged in Won. Locked -> ignored.
    game.open_cell(row=8, column=1)
    # (4,4) toggle: Hidden in Lost (would flag). Locked -> ignored.
    game.toggle_flag(row=4, column=4)
    # (0,0) toggle: Flagged in both (would unflag). Locked -> ignored.
    game.toggle_flag(row=0, column=0)
    # (1,1): Opened, count 2, exactly 2 flagged neighbours (0,0),(0,2); in Lost
    #   its 6 Hidden safe neighbours would be opened. Not Playing -> ignored.
    game.chord_cell(row=1, column=1)
    # tick: status is not Playing -> elapsed_seconds stays 42.
    game.tick()

    # Nothing changed: every cell, counter, timer and status identical to before.
    assert _snapshot(game) == before
    assert game.status == status
    assert game.elapsed_seconds == 42
    assert game.flags_placed == before[4]
    assert game.remaining_mines == before[5]
    assert _cell(game, 4, 4)["state"] == before[0][4 * WIDTH + 4]["state"]
    assert _cell(game, 0, 0)["state"] == "Flagged"


@pytest.mark.parametrize(
    "arrange, status",
    [(_arrange_won, "Won"), (_arrange_lost, "Lost")],
)
def test_finished_board_accepts_new_game(arrange, status):
    game = _new_game()
    arrange(game)

    new_game = game.restart_game()

    # The finished game keeps its outcome.
    assert game.status == status
    # The new game is accepted: a fresh Ready game of the same configuration.
    assert new_game.id != "g1"
    assert new_game.status == "Ready"
    assert new_game.difficulty_id == "beginner"
    assert new_game.width == 9
    assert new_game.height == 9
    assert new_game.mine_count == 10
    assert new_game.remaining_mines == 10
    assert new_game.flags_placed == 0
    assert new_game.elapsed_seconds == 0
    assert new_game.mines_laid is False
    assert new_game.ended_at is None
    assert new_game.struck_cell_id is None
    assert len(new_game.cells) == 81
    assert all(c["state"] == "Hidden" for c in new_game.cells)
    assert all(c["has_mine"] is False for c in new_game.cells)

    # The new game takes player actions: first open is safe and starts play.
    new_game.open_cell(row=4, column=4)
    assert new_game.status == "Playing"
    assert new_game.cells[4 * 9 + 4]["state"] == "Opened"


def test_same_board_while_playing_accepts_flag():
    # Contrast: identical board to the Lost case but (8,8) still Hidden and
    # status Playing, so only the status differs from the locked case.
    game = _new_game()
    _arrange_lost_like(game)
    game.status = "Playing"

    game.toggle_flag(row=4, column=4)

    # (4,4) Hidden -> Flagged; flags 2 -> 3; remaining 10 - 3 = 7.
    assert _cell(game, 4, 4)["state"] == "Flagged"
    assert game.flags_placed == 3
    assert game.remaining_mines == 7
    assert game.status == "Playing"
