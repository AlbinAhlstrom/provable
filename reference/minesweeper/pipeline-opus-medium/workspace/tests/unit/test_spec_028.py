import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
# Ten mines: the whole top row (0,0)..(0,8) plus (1,0).
MINE_POSITIONS = {(0, c) for c in range(9)} | {(1, 0)}
MINE_COUNT = len(MINE_POSITIONS)  # 10, matches the board so the fixed-count rule holds


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _make_playing_game(elapsed, opened_safe_except=None, open_all_safe=False):
    """A Playing game with mines laid, consistent adjacent counts and a running timer.

    If open_all_safe is True, every safe cell is Opened except `opened_safe_except`.
    Otherwise every cell is Hidden.
    """
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
            has_mine = (row, column) in MINE_POSITIONS
            count = sum(1 for n in _neighbours(row, column) if n in MINE_POSITIONS)
            state = "Hidden"
            if open_all_safe and not has_mine and (row, column) != opened_safe_except:
                state = "Opened"
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": has_mine,
                    "adjacent_mine_count": count,
                    "state": state,
                }
            )
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    game.flags_placed = 0
    game.remaining_mines = MINE_COUNT
    game.elapsed_seconds = elapsed
    game.started_at = "2024-01-01T10:00:05"
    game.ended_at = None
    game.struck_cell_id = None
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


def test_timer_runs_while_playing_as_control():
    game = _make_playing_game(elapsed=42)
    # Status is Playing and 42 < 999 cap, so one tick adds exactly 1 second.
    game.tick()
    assert game.elapsed_seconds == 43


def test_timer_freezes_when_game_is_lost():
    game = _make_playing_game(elapsed=42)

    # (0,0) holds a mine and is Hidden; the game is Playing (not a first open),
    # so opening it detonates it and the game becomes Lost.
    game.open_cell(row=0, column=0)

    # Opening the mine ends the game: Detonated cell, struck cell recorded, Lost.
    assert _cell(game, 0, 0)["state"] == "Detonated"
    assert game.struck_cell_id == "0-0"
    assert game.status == "Lost"
    # Ending the game freezes the timer at its value at the moment of loss: 42.
    assert game.elapsed_seconds == 42

    # Status is Lost (not Playing), so each tick changes nothing.
    for _ in range(5):
        game.tick()
    assert game.elapsed_seconds == 42
    assert game.status == "Lost"


def test_timer_freezes_when_game_is_won():
    # Every safe cell is Opened except (8,8). (8,8) is far from the mines
    # (rows 0-1), so its count is 0; all its neighbours are already Opened,
    # so the cascade opens nothing more. It is the last non-mine cell.
    game = _make_playing_game(elapsed=42, opened_safe_except=(8, 8), open_all_safe=True)
    assert _cell(game, 8, 8)["adjacent_mine_count"] == 0

    game.open_cell(row=8, column=8)

    # Last non-mine cell opened -> Won, with every mine auto-flagged.
    assert _cell(game, 8, 8)["state"] == "Opened"
    assert game.status == "Won"
    assert game.flags_placed == MINE_COUNT
    assert game.remaining_mines == 0
    # The timer froze at the moment of the win: still 42.
    assert game.elapsed_seconds == 42

    # Status is Won (not Playing), so each tick changes nothing.
    for _ in range(5):
        game.tick()
    assert game.elapsed_seconds == 42
    assert game.status == "Won"
