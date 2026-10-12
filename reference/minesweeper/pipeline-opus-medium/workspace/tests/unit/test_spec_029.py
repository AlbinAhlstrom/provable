from src.domain.game import Game

import pytest


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10

# Ten mines: the whole bottom row (row 8, columns 0..8) plus one interior mine at (4, 4).
MINES = {(8, c) for c in range(WIDTH)} | {(4, 4)}


def _neighbour_mines(row, column):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH and (r, c) in MINES:
                count += 1
    return count


def _playing_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    # Keep the full row-major grid shape, only changing what the cells hold.
    game.cells = [
        {
            "id": f"{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": (r, c) in MINES,
            "adjacent_mine_count": _neighbour_mines(r, c),
            "state": "Hidden",
        }
        for r in range(HEIGHT)
        for c in range(WIDTH)
    ]
    # Mines already laid: the game is in Playing status with the clock running.
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 42
    game.flags_placed = 0
    game.remaining_mines = MINE_COUNT
    game.ended_at = None
    game.struck_cell_id = None
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


@pytest.mark.parametrize(
    "row, column",
    [
        (8, 4),  # mine on the bottom edge
        (4, 4),  # interior mine
    ],
)
def test_opening_a_hidden_mine_in_playing_game_loses(row, column):
    game = _playing_game()
    assert _cell(game, row, column)["has_mine"] is True
    assert _cell(game, row, column)["state"] == "Hidden"

    game.open_cell(row=row, column=column)

    # The opened cell holds a mine and was Hidden: Hidden -> Detonated is allowed,
    # so the cell becomes Detonated.
    assert _cell(game, row, column)["state"] == "Detonated"

    # The struck cell is recorded by its id f"{row}-{column}".
    assert game.struck_cell_id == f"{row}-{column}"

    # Playing -> Lost is an allowed transition; opening a mine ends the game in a loss.
    # No win can interfere: 71 safe cells are all still Hidden.
    assert game.status == "Lost"

    # The end of the game is timestamped.
    assert game.ended_at is not None

    # Only the opened mine is Detonated; no other cell became Detonated.
    detonated = [c["id"] for c in game.cells if c["state"] == "Detonated"]
    assert detonated == [f"{row}-{column}"]

    # No safe cell was opened by opening the mine (no cascade from a mine).
    assert all(c["state"] == "Hidden" for c in game.cells if c["id"] != f"{row}-{column}")

    # Flags and counter untouched: no flags were placed, counter stays M - 0 = 10.
    assert game.flags_placed == 0
    assert game.remaining_mines == MINE_COUNT

    # Timer froze at its value at the moment of the loss (42).
    assert game.elapsed_seconds == 42

    # The clock advancing after the loss changes nothing: tick only counts while Playing.
    game.tick()
    assert game.elapsed_seconds == 42
    assert game.status == "Lost"
