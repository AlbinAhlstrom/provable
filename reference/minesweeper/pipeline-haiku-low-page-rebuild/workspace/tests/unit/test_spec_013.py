import pytest

from src.domain.game import Game

STARTED_AT = "2024-01-01T10:00:00"
MINES = {(0, c) for c in range(9)} | {(1, 0)}  # 10 mines, Beginner count


def _adjacent_mine_count(row, column):
    # Count mines among the up-to-eight neighbours that lie on the 9x9 board.
    return sum(
        1
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
        if (dr, dc) != (0, 0) and (row + dr, column + dc) in MINES
    )


def _make_in_progress_game(revealed):
    game = Game(id="game-1")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = STARTED_AT
    game.ended_at = None
    game.elapsed_seconds = 0
    game.mine_count = 10
    game.flag_count = 0
    game.cells = [
        {
            "id": f"{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": (r, c) in MINES,
            "adjacent_mine_count": _adjacent_mine_count(r, c),
            "state": "revealed" if (r, c) in revealed else "hidden",
        }
        for r in range(9)
        for c in range(9)
    ]
    return game


def test_timer_stops_when_game_is_lost():
    # Given an in-progress game with 10 mines, no cell revealed yet,
    # started at 10:00:00 and elapsed_seconds 0.
    game = _make_in_progress_game(revealed=set())

    # When the player reveals the mine at (0,0) at 10:00:42 (42 seconds in).
    game.reveal_cell(row=0, column=0, now="2024-01-01T10:00:42")

    # Then the game is lost: (0,0) is a mine and the game is terminal.
    assert game.status == "lost"
    # And elapsed_seconds is fixed at 42, the time from 10:00:00 to 10:00:42.
    assert game.elapsed_seconds == 42
    # And ended_at records the moment the game ended.
    assert game.ended_at == "2024-01-01T10:00:42"

    # When the player tries to reveal the hidden safe cell (4,4) at 10:05:00.
    # The game is lost, so the action is refused and nothing changes.
    with pytest.raises(Exception) as exc_info:
        game.reveal_cell(row=4, column=4, now="2024-01-01T10:05:00")
    assert type(exc_info.value).__name__ == "InvalidActionError"

    # Then elapsed_seconds still reads 42: the timer no longer increases.
    assert game.elapsed_seconds == 42
    assert game.ended_at == "2024-01-01T10:00:42"


def test_timer_stops_when_game_is_won():
    # Given an in-progress game where every safe cell is revealed except (8,8).
    # (8,8) has no mine neighbours, so its adjacent_mine_count is 0.
    safe_cells = {(r, c) for r in range(9) for c in range(9)} - MINES
    revealed = safe_cells - {(8, 8)}
    game = _make_in_progress_game(revealed=revealed)

    # When the player reveals (8,8) at 10:00:42 (42 seconds in), the last safe cell.
    game.reveal_cell(row=8, column=8, now="2024-01-01T10:00:42")

    # Then the game is won: all safe cells are now revealed.
    assert game.status == "won"
    # And elapsed_seconds is fixed at 42, the time from 10:00:00 to 10:00:42.
    assert game.elapsed_seconds == 42
    # And ended_at records the moment the game ended.
    assert game.ended_at == "2024-01-01T10:00:42"

    # When the player tries to flag the cell (4,4) at 10:05:00.
    # The game is won, so the action is refused and nothing changes.
    with pytest.raises(Exception) as exc_info:
        game.toggle_flag(row=4, column=4, now="2024-01-01T10:05:00")
    assert type(exc_info.value).__name__ == "InvalidActionError"

    # Then elapsed_seconds still reads 42: the timer no longer increases.
    assert game.elapsed_seconds == 42
    assert game.ended_at == "2024-01-01T10:00:42"
