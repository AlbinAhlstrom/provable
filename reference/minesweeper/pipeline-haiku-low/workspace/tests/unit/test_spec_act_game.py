import pytest

from src.domain.game import Game


STARTED = "2024-01-01T10:00:00+00:00"


def _blank_board(rows, columns, cell_state="hidden", id_prefix="c"):
    """One hidden cell per position, every key the class describes, no mines."""
    return [
        {
            "id": f"{id_prefix}{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": cell_state,
        }
        for r in range(rows)
        for c in range(columns)
    ]


def _cell_at(game, row, column):
    matches = [c for c in game.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


def test_new_game_has_default_fields():
    # Given: a Game built with only its required field id.
    # When: nothing is called on it.
    game = Game(id="game-1")

    # Then: the documented defaults hold for a newly created game.
    # id was given at construction; defaults come from the class declaration.
    assert game.id == "game-1"
    assert game.difficulty == "Beginner"
    assert game.status == "ready"
    assert game.started_at is None
    assert game.ended_at is None
    assert game.elapsed_seconds == 0
    assert game.mine_count == 10
    assert game.flag_count == 0
    # No reveal has happened, so no board has been laid out yet.
    assert game.cells == []
    assert game.events == []


def test_start_game_discards_old_session_and_sets_up_intermediate_board():
    # Given: an in-progress-looking old session that is actually won, with a
    # timer that ran for 42 seconds, 3 flags placed, and an old board of 81
    # cells where some are revealed and some flagged.
    # The status is "won" (terminal), which start_game is allowed to override
    # because it is allowed in any status.
    game = Game(id="game-2")
    game.difficulty = "Beginner"
    game.status = "won"
    game.started_at = STARTED
    game.ended_at = "2024-01-01T10:00:42+00:00"
    game.elapsed_seconds = 42
    game.mine_count = 10
    game.flag_count = 3
    old_cells = _blank_board(9, 9, id_prefix="old")
    old_cells[0]["state"] = "revealed"
    old_cells[1]["state"] = "flagged"
    game.cells = old_cells

    # When: a new game is started at Intermediate.
    game.start_game(difficulty="Intermediate")

    # Then: the object shows the fresh Intermediate session (16 x 16, 40 mines).
    # Status returns to ready: no reveal has happened yet.
    # Timer is reset: no started_at, no ended_at, elapsed 0.
    # Flags are cleared: flag_count 0.
    # No mine layout is fixed yet, so no cell holds a mine.
    assert game.difficulty == "Intermediate"
    assert game.status == "ready"
    assert game.started_at is None
    assert game.ended_at is None
    assert game.elapsed_seconds == 0
    assert game.mine_count == 40
    assert game.flag_count == 0
    # The old board's cells are discarded: none of its ids remain.
    assert all(not c["id"].startswith("old") for c in game.cells)
    # Every remaining cell is a fresh hidden cell with no mine.
    assert all(c["state"] == "hidden" for c in game.cells)
    assert all(c["has_mine"] is False for c in game.cells)


def test_reveal_cell_on_ready_game_lays_out_board_and_starts_session():
    # Given: a ready Beginner game (9 x 9, 10 mines) with no board yet.
    # Its status is ready, timer not started, cells empty.
    game = Game(id="game-3")
    game.difficulty = "Beginner"
    game.status = "ready"
    game.mine_count = 10
    game.flag_count = 0
    game.cells = []

    # When: the first reveal is made at the corner (0, 0).
    game.reveal_cell(row=0, column=0)

    # Then: the board is laid out as 9 x 9 = 81 cells.
    assert len(game.cells) == 81
    # Exactly the Beginner mine count is placed.
    assert sum(1 for c in game.cells if c["has_mine"]) == 10
    # First-click safety: the target and its in-board neighbours (0,1), (1,0),
    # (1,1) hold no mine, so the first reveal cannot lose.
    for r, c in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        assert _cell_at(game, r, c)["has_mine"] is False
    # The target was hidden and unflagged, so it is now revealed.
    assert _cell_at(game, 0, 0)["state"] == "revealed"
    # The first reveal started the timer and moved the game to in_progress.
    # The mine is not hit and not all 71 safe cells are opened by one reveal,
    # so the game is neither lost nor won.
    assert game.started_at is not None
    assert game.ended_at is None
    assert game.status == "in_progress"


def test_toggle_flag_cycles_hidden_to_flagged_and_back_without_starting_timer():
    # Given: an in-progress Beginner game (9 x 9, 10 mines) whose timer was
    # started earlier at STARTED and has run for 0 seconds in this model.
    # All 81 cells are hidden with no mine placed in the target area,
    # so flagging (4, 4) is decided by the flag rule alone.
    game = Game(id="game-4")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = STARTED
    game.elapsed_seconds = 0
    game.mine_count = 10
    game.flag_count = 0
    game.cells = _blank_board(9, 9)

    # When: the hidden cell (4, 4) is toggled once.
    game.toggle_flag(row=4, column=4)

    # Then: the cell becomes flagged and flag_count goes from 0 to 1.
    # The timer is untouched: started_at and elapsed_seconds are as before,
    # and the status is still in_progress.
    assert _cell_at(game, 4, 4)["state"] == "flagged"
    assert game.flag_count == 1
    assert game.started_at == STARTED
    assert game.elapsed_seconds == 0
    assert game.status == "in_progress"

    # When: the same cell is toggled again.
    game.toggle_flag(row=4, column=4)

    # Then: the flagged cell returns to hidden and flag_count returns to 0.
    assert _cell_at(game, 4, 4)["state"] == "hidden"
    assert game.flag_count == 0
    assert game.started_at == STARTED
    assert game.elapsed_seconds == 0
    assert game.status == "in_progress"
