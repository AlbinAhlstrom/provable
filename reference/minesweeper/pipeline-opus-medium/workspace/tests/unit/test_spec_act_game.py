import copy

import pytest

from src.domain.game import Game


CREATED_AT = "2024-01-01T00:00:00"
STARTED_AT = "2024-01-01T00:00:05"
ENDED_AT = "2024-01-01T00:01:00"

# Board B (9x9, 10 mines): bottom row columns 0-6 are mines, plus a ring of three
# mines (7,7), (7,8), (8,7) enclosing the safe corner (8,8), whose count is 3.
# (8,8) touches only mines, so no cascade can ever reach it, so the game never
# wins by accident unless (8,8) itself is opened.
BOARD_B_MINES = {(8, c) for c in range(7)} | {(7, 7), (7, 8), (8, 7)}


def make_game(difficulty_id="beginner", width=9, height=9, mine_count=10, game_id="g1"):
    return Game(
        id=game_id,
        difficulty_id=difficulty_id,
        width=width,
        height=height,
        mine_count=mine_count,
        remaining_mines=mine_count,
        created_at=CREATED_AT,
    )


def neighbours(width, height, r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width:
                yield nr, nc


def build_cells(width, height, mines, opened=(), flagged=(), detonated=()):
    cells = []
    for r in range(height):
        for c in range(width):
            count = sum(1 for n in neighbours(width, height, r, c) if n in mines)
            if (r, c) in detonated:
                state = "Detonated"
            elif (r, c) in opened:
                state = "Opened"
            elif (r, c) in flagged:
                state = "Flagged"
            else:
                state = "Hidden"
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": (r, c) in mines,
                    "adjacent_mine_count": count,
                    "state": state,
                }
            )
    return cells


def arrange(game, mines=BOARD_B_MINES, opened=(), flagged=(), detonated=(),
            status="Playing", elapsed=42, struck=None, ended_at=None):
    game.cells = build_cells(game.width, game.height, set(mines), set(opened),
                             set(flagged), set(detonated))
    game.status = status
    game.mines_laid = True
    game.started_at = STARTED_AT
    game.ended_at = ended_at
    game.struck_cell_id = struck
    game.elapsed_seconds = elapsed
    game.flags_placed = len(set(flagged))
    game.remaining_mines = game.mine_count - len(set(flagged))
    return game


def cell(game, r, c):
    return game.cells[r * game.width + c]


def snapshot(game):
    return copy.deepcopy(
        {
            "id": game.id,
            "difficulty_id": game.difficulty_id,
            "width": game.width,
            "height": game.height,
            "mine_count": game.mine_count,
            "status": game.status,
            "mines_laid": game.mines_laid,
            "flags_placed": game.flags_placed,
            "remaining_mines": game.remaining_mines,
            "elapsed_seconds": game.elapsed_seconds,
            "started_at": game.started_at,
            "ended_at": game.ended_at,
            "struck_cell_id": game.struck_cell_id,
            "cells": game.cells,
        }
    )


def all_safe_board_b():
    return {(r, c) for r in range(9) for c in range(9)} - BOARD_B_MINES


def assert_starting_state(new, difficulty_id, width, height, mine_count):
    assert isinstance(new, Game)
    assert new.difficulty_id == difficulty_id
    assert new.width == width
    assert new.height == height
    assert new.mine_count == mine_count
    assert new.status == "Ready"
    assert new.mines_laid is False
    assert new.flags_placed == 0
    assert new.elapsed_seconds == 0
    assert new.remaining_mines == mine_count
    assert new.started_at is None
    assert new.ended_at is None
    assert new.struck_cell_id is None
    assert len(new.cells) == width * height
    for i, cl in enumerate(new.cells):
        r, c = divmod(i, width)
        assert cl["id"] == f"{r}-{c}"
        assert cl["row"] == r and cl["column"] == c
        assert cl["has_mine"] is False
        assert cl["adjacent_mine_count"] == 0
        assert cl["state"] == "Hidden"


# ---------------------------------------------------------------- construction

def test_new_game_starts_ready_with_hidden_empty_grid():
    game = make_game(difficulty_id="expert", width=30, height=16, mine_count=99)
    # Freshly constructed: Ready, nothing laid, counters at their start values,
    # 30*16 = 480 hidden mine-free cells in row-major order with ids "row-column".
    assert_starting_state(game, "expert", 30, 16, 99)
    assert game.id == "g1"
    assert game.created_at == CREATED_AT
    assert game.events == []
    assert game.cells[0]["id"] == "0-0"
    assert game.cells[1]["id"] == "0-1"
    assert game.cells[30]["id"] == "1-0"
    assert game.cells[-1]["id"] == "15-29"


# ------------------------------------------------------------------- open_cell

def test_open_cell_first_open_lays_mines_and_starts_playing():
    game = make_game()
    # Before the first open no cell holds a mine.
    assert not any(cl["has_mine"] for cl in game.cells)

    game.open_cell(row=4, column=4)

    # Mines are laid now: exactly 10 of the 81 cells, never the opened one.
    assert game.mines_laid is True
    assert sum(1 for cl in game.cells if cl["has_mine"]) == 10
    assert cell(game, 4, 4)["has_mine"] is False
    assert cell(game, 4, 4)["state"] == "Opened"
    # Every cell's count equals the mines among its existing neighbours.
    mines = {(cl["row"], cl["column"]) for cl in game.cells if cl["has_mine"]}
    for cl in game.cells:
        expected = sum(1 for n in neighbours(9, 9, cl["row"], cl["column"]) if n in mines)
        assert cl["adjacent_mine_count"] == expected
    # A safe first open never loses; no mine is opened or detonated.
    assert not any(cl["state"] == "Detonated" for cl in game.cells)
    assert not any(cl["has_mine"] and cl["state"] == "Opened" for cl in game.cells)
    assert game.struck_cell_id is None
    # If the opened cell is a zero, the cascade opened all its neighbours.
    if cell(game, 4, 4)["adjacent_mine_count"] == 0:
        for r, c in neighbours(9, 9, 4, 4):
            assert cell(game, r, c)["state"] == "Opened"
    # Status is Playing, unless the cascade happened to open every safe cell (Won).
    safe_left = any(not cl["has_mine"] and cl["state"] != "Opened" for cl in game.cells)
    assert game.status == ("Playing" if safe_left else "Won")
    assert game.started_at is not None


def test_open_cell_numbered_cell_opens_only_itself():
    game = arrange(make_game())
    before = snapshot(game)

    game.open_cell(row=7, column=0)

    # (7,0) neighbours (8,0),(8,1) are mines -> count 2, so no cascade:
    # only (7,0) changes from Hidden to Opened; the game stays Playing.
    assert cell(game, 7, 0)["state"] == "Opened"
    assert cell(game, 7, 0)["adjacent_mine_count"] == 2
    changed = [i for i, cl in enumerate(game.cells) if cl != before["cells"][i]]
    assert changed == [7 * 9 + 0]
    assert game.status == "Playing"


def test_open_cell_zero_cascades_stops_at_numbers_and_skips_flags():
    game = arrange(make_game(), flagged={(3, 3)})

    game.open_cell(row=0, column=0)

    # Rows 0-5 are all zeros, row 6 cols 0-5 zeros, (6,6..8) and row 7 cols 0-6
    # numbered: the cascade opens every safe cell it can reach. (8,8) touches
    # only mines so it is never reached; flagged (3,3) is skipped and stays Flagged.
    expected_opened = all_safe_board_b() - {(8, 8), (3, 3)}
    for r in range(9):
        for c in range(9):
            st = cell(game, r, c)["state"]
            if (r, c) in expected_opened:
                assert st == "Opened"
            elif (r, c) == (3, 3):
                assert st == "Flagged"
            else:
                assert st == "Hidden"
    # (8,8) is still hidden, so not Won; no mine opened, so not Lost.
    assert game.status == "Playing"
    assert game.flags_placed == 1
    assert game.remaining_mines == 9


def test_open_cell_on_mine_loses():
    game = arrange(make_game(), elapsed=42)

    game.open_cell(row=8, column=0)

    # (8,0) holds a mine -> Detonated, recorded as struck, game Lost, timer frozen.
    assert cell(game, 8, 0)["state"] == "Detonated"
    assert game.struck_cell_id == "8-0"
    assert game.status == "Lost"
    assert game.ended_at is not None
    assert game.elapsed_seconds == 42


def test_open_cell_last_safe_cell_wins_and_flags_mines():
    game = arrange(make_game(), opened=all_safe_board_b() - {(8, 8)}, elapsed=42)

    game.open_cell(row=8, column=8)

    # (8,8) is the last unopened safe cell (count 3) -> Opened, game Won.
    assert cell(game, 8, 8)["state"] == "Opened"
    assert game.status == "Won"
    assert game.ended_at is not None
    assert game.elapsed_seconds == 42
    # Every mine is auto-flagged; counter reads 0.
    for r, c in BOARD_B_MINES:
        assert cell(game, r, c)["state"] == "Flagged"
    assert game.flags_placed == 10
    assert game.remaining_mines == 0


@pytest.mark.parametrize("target", [(0, 0), (8, 0)])
def test_open_cell_on_opened_or_flagged_cell_is_ignored(target):
    # (0,0) is Opened (safe), (8,0) is a Flagged mine.
    game = arrange(make_game(), opened={(0, 0)}, flagged={(8, 0)})
    before = snapshot(game)

    game.open_cell(row=target[0], column=target[1])

    # Opening an Opened or Flagged cell changes nothing and raises nothing.
    assert snapshot(game) == before


@pytest.mark.parametrize("status", ["Won", "Lost", "Abandoned"])
def test_open_cell_in_finished_game_is_ignored(status):
    game = arrange(make_game(), status=status, ended_at=ENDED_AT)
    before = snapshot(game)

    game.open_cell(row=0, column=0)

    # The board is locked: (0,0) stays Hidden and no field changes.
    assert snapshot(game) == before


@pytest.mark.parametrize("row,column,ok", [(8, 8, True), (9, 0, False), (0, 9, False), (-1, 0, False)])
def test_open_cell_outside_grid_is_refused(row, column, ok):
    game = arrange(make_game(), opened=all_safe_board_b() - {(8, 8), (0, 0)})
    if ok:
        # (8,8) is the last valid row/column: accepted, the cell opens.
        game.open_cell(row=row, column=column)
        assert cell(game, 8, 8)["state"] == "Opened"
    else:
        before = snapshot(game)
        with pytest.raises(Exception) as exc_info:
            game.open_cell(row=row, column=column)
        # Row/column 9 or -1 is outside the 9x9 grid.
        assert type(exc_info.value).__name__ == "CellNotFoundError"
        assert snapshot(game) == before


# ----------------------------------------------------------------- toggle_flag

@pytest.mark.parametrize("status", ["Ready", "Playing"])
def test_toggle_flag_switches_hidden_and_flagged(status):
    game = make_game()
    if status == "Playing":
        arrange(game)

    game.toggle_flag(row=0, column=0)
    # Hidden -> Flagged, flags 0 -> 1, counter 10 - 1 = 9; status unchanged.
    assert cell(game, 0, 0)["state"] == "Flagged"
    assert game.flags_placed == 1
    assert game.remaining_mines == 9
    assert game.status == status

    game.toggle_flag(row=0, column=0)
    # Flagged -> Hidden, flags back to 0, counter 10.
    assert cell(game, 0, 0)["state"] == "Hidden"
    assert game.flags_placed == 0
    assert game.remaining_mines == 10
    assert game.status == status


def test_toggle_flag_is_unlimited_and_counter_goes_negative():
    flags = {(0, c) for c in range(9)} | {(1, 0)}  # 10 flags = mine_count
    game = arrange(make_game(), flagged=flags)

    game.toggle_flag(row=2, column=0)

    # An 11th flag is still placed: counter 10 - 11 = -1.
    assert cell(game, 2, 0)["state"] == "Flagged"
    assert game.flags_placed == 11
    assert game.remaining_mines == -1


def test_toggle_flag_on_opened_cell_is_ignored():
    game = arrange(make_game(), opened={(0, 0)})
    before = snapshot(game)

    game.toggle_flag(row=0, column=0)

    # An Opened cell cannot be flagged: nothing changes, no error.
    assert snapshot(game) == before


@pytest.mark.parametrize("status", ["Won", "Lost", "Abandoned"])
def test_toggle_flag_in_finished_game_is_ignored(status):
    game = arrange(make_game(), status=status, ended_at=ENDED_AT)
    before = snapshot(game)

    game.toggle_flag(row=0, column=0)

    # Locked board: (0,0) stays Hidden, flags and counter unchanged.
    assert snapshot(game) == before


@pytest.mark.parametrize("row,column,ok", [(0, 8, True), (0, 9, False), (9, 0, False)])
def test_toggle_flag_outside_grid_is_refused(row, column, ok):
    game = arrange(make_game())
    if ok:
        game.toggle_flag(row=row, column=column)
        # Column 8 is inside the grid: the Hidden cell becomes Flagged.
        assert cell(game, 0, 8)["state"] == "Flagged"
        assert game.flags_placed == 1
    else:
        with pytest.raises(Exception) as exc_info:
            game.toggle_flag(row=row, column=column)
        # Column/row 9 is outside the 9x9 grid.
        assert type(exc_info.value).__name__ == "CellNotFoundError"
        assert game.flags_placed == 0


# ------------------------------------------------------------------ chord_cell

def test_chord_cell_with_matching_flags_opens_neighbours_and_cascades():
    # (6,6) is Opened with count 1 (only mine neighbour is (7,7)), (7,7) flagged.
    game = arrange(make_game(), opened={(6, 6)}, flagged={(7, 7)})
    assert cell(game, 6, 6)["adjacent_mine_count"] == 1

    game.chord_cell(row=6, column=6)

    # 1 flag == N=1: hidden neighbours (5,5),(5,6),(5,7),(6,5),(6,7),(7,5),(7,6)
    # open; zeros among them cascade over the whole safe area. (8,8) touches only
    # mines and stays Hidden, so the game is still Playing; (7,7) stays Flagged.
    expected_opened = all_safe_board_b() - {(8, 8)}
    for r in range(9):
        for c in range(9):
            st = cell(game, r, c)["state"]
            if (r, c) in expected_opened:
                assert st == "Opened"
            elif (r, c) == (7, 7):
                assert st == "Flagged"
            else:
                assert st == "Hidden"
    assert game.status == "Playing"


@pytest.mark.parametrize("flags", [set(), {(7, 7), (5, 5)}])
def test_chord_cell_with_mismatched_flags_changes_nothing(flags):
    # Same as the matching case but with 0 or 2 flags around (6,6) (N=1).
    game = arrange(make_game(), opened={(6, 6)}, flagged=flags)
    before = snapshot(game)

    game.chord_cell(row=6, column=6)

    # Flag count differs from N: no cell changes, no error.
    assert snapshot(game) == before


def test_chord_cell_with_wrong_flag_loses():
    # (6,6) N=1, but the single flag is on safe (5,5); mine (7,7) is Hidden.
    game = arrange(make_game(), opened={(6, 6)}, flagged={(5, 5)})

    game.chord_cell(row=6, column=6)

    # 1 flag == N: hidden neighbours open, including mine (7,7) -> Detonated, Lost.
    assert cell(game, 7, 7)["state"] == "Detonated"
    assert game.struck_cell_id == "7-7"
    assert game.status == "Lost"
    assert game.ended_at is not None
    assert cell(game, 5, 5)["state"] == "Flagged"


def test_chord_cell_on_hidden_cell_is_ignored():
    game = arrange(make_game(), flagged={(7, 7)})
    before = snapshot(game)

    game.chord_cell(row=6, column=6)

    # (6,6) is Hidden: chording it changes nothing.
    assert snapshot(game) == before


def test_chord_cell_on_zero_cell_is_ignored():
    game = arrange(make_game(), opened={(0, 0)})
    before = snapshot(game)

    game.chord_cell(row=0, column=0)

    # (0,0) is Opened with count 0: chord does not apply.
    assert snapshot(game) == before


@pytest.mark.parametrize("status", ["Won", "Lost", "Abandoned"])
def test_chord_cell_when_not_playing_is_ignored(status):
    game = arrange(make_game(), opened={(6, 6)}, flagged={(7, 7)}, status=status,
                   ended_at=ENDED_AT)
    before = snapshot(game)

    game.chord_cell(row=6, column=6)

    # Flags match, but the game is not Playing: nothing changes.
    assert snapshot(game) == before


@pytest.mark.parametrize("row,column,ok", [(8, 0, True), (9, 0, False), (0, 9, False)])
def test_chord_cell_outside_grid_is_refused(row, column, ok):
    game = arrange(make_game())
    before = snapshot(game)
    if ok:
        # (8,0) is inside the grid (a Hidden cell): ignored, no error.
        game.chord_cell(row=row, column=column)
        assert snapshot(game) == before
    else:
        with pytest.raises(Exception) as exc_info:
            game.chord_cell(row=row, column=column)
        assert type(exc_info.value).__name__ == "CellNotFoundError"
        assert snapshot(game) == before


# ------------------------------------------------------------------------ tick

@pytest.mark.parametrize("start,expected", [(5, 6), (998, 999), (999, 999)])
def test_tick_advances_playing_timer_capped_at_999(start, expected):
    game = arrange(make_game(), elapsed=start)

    game.tick()

    # Playing: +1 per tick, never beyond 999.
    assert game.elapsed_seconds == expected
    assert game.status == "Playing"


@pytest.mark.parametrize("status", ["Won", "Lost", "Abandoned"])
def test_tick_in_finished_game_changes_nothing(status):
    game = arrange(make_game(), status=status, elapsed=42, ended_at=ENDED_AT)
    before = snapshot(game)

    game.tick()

    # Not Playing: the timer stays at 42.
    assert snapshot(game) == before


def test_tick_in_ready_game_changes_nothing():
    game = make_game()
    before = snapshot(game)

    game.tick()

    # Ready: the timer has not started and stays at 0.
    assert snapshot(game) == before
    assert game.elapsed_seconds == 0


# ---------------------------------------------------------------- restart_game

@pytest.mark.parametrize("status", ["Ready", "Playing"])
def test_restart_game_abandons_active_game_and_returns_new_one(status):
    game = make_game(difficulty_id="intermediate", width=16, height=16, mine_count=40)
    if status == "Playing":
        arrange(game, mines={(15, c) for c in range(16)} | {(14, c) for c in range(16)}
                | {(13, c) for c in range(8)})

    new = game.restart_game()

    # Active game -> Abandoned with ended_at set.
    assert game.status == "Abandoned"
    assert game.ended_at is not None
    # New Ready game, new id, same configuration, starting state.
    assert new is not game
    assert new.id != game.id
    assert_starting_state(new, "intermediate", 16, 16, 40)


@pytest.mark.parametrize("status", ["Won", "Lost"])
def test_restart_game_after_end_keeps_outcome(status):
    game = arrange(make_game(), status=status, ended_at=ENDED_AT,
                   struck="8-0" if status == "Lost" else None,
                   detonated={(8, 0)} if status == "Lost" else ())
    before = snapshot(game)

    new = game.restart_game()

    # Finished game keeps its outcome and every field.
    assert snapshot(game) == before
    assert game.status == status
    assert new.id != game.id
    assert_starting_state(new, "beginner", 9, 9, 10)


# ----------------------------------------------------------- change_difficulty

@pytest.mark.parametrize(
    "difficulty_id,width,height,mine_count",
    [("beginner", 9, 9, 10), ("intermediate", 16, 16, 40), ("expert", 30, 16, 99)],
)
def test_change_difficulty_presets(difficulty_id, width, height, mine_count):
    game = make_game(difficulty_id="custom", width=12, height=12, mine_count=20)

    new = game.change_difficulty(difficulty_id=difficulty_id, width=None, height=None,
                                 mine_count=None)

    # Ready game -> Abandoned; new game has the preset's size and mines.
    assert game.status == "Abandoned"
    assert new.id != game.id
    assert_starting_state(new, difficulty_id, width, height, mine_count)


@pytest.mark.parametrize(
    "width,height,mine_count",
    [(9, 9, 10), (30, 9, 10), (9, 24, 10), (9, 9, 64), (30, 24, 667)],
)
def test_change_difficulty_custom_at_limits_is_accepted(width, height, mine_count):
    game = arrange(make_game())

    new = game.change_difficulty(difficulty_id="custom", width=width, height=height,
                                 mine_count=mine_count)

    # Width 9/30, height 9/24, mines 10 and (W-1)*(H-1) are all inside the limits.
    assert game.status == "Abandoned"
    assert game.ended_at is not None
    assert_starting_state(new, "custom", width, height, mine_count)


@pytest.mark.parametrize(
    "difficulty_id,width,height,mine_count",
    [
        ("custom", 8, 9, 10),
        ("custom", 31, 9, 10),
        ("custom", 9, 8, 10),
        ("custom", 9, 25, 10),
        ("custom", 9, 9, 9),
        ("custom", 9, 9, 65),
        ("custom", 30, 24, 668),
        ("master", 9, 9, 10),
    ],
)
def test_change_difficulty_invalid_is_refused_and_game_unchanged(difficulty_id, width,
                                                                 height, mine_count):
    game = arrange(make_game(), opened={(0, 0)}, flagged={(8, 0)}, elapsed=42)
    before = snapshot(game)

    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(difficulty_id=difficulty_id, width=width, height=height,
                               mine_count=mine_count)

    # Each case is one step beyond a limit (or an unknown id): refused.
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    assert str(exc_info.value) != ""
    # The current game, board, timer and counter are untouched.
    assert snapshot(game) == before


def test_change_difficulty_refusal_message_states_width_limits():
    game = make_game()
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(difficulty_id="custom", width=31, height=9, mine_count=10)
    # Width 31 is above 30: the message names the 9-30 range.
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    assert "9" in str(exc_info.value) and "30" in str(exc_info.value)


@pytest.mark.parametrize("status", ["Won", "Lost"])
def test_change_difficulty_after_end_keeps_outcome(status):
    game = arrange(make_game(), status=status, ended_at=ENDED_AT)
    before = snapshot(game)

    new = game.change_difficulty(difficulty_id="expert", width=None, height=None,
                                 mine_count=None)

    # Finished game keeps its outcome; a new expert game is returned.
    assert snapshot(game) == before
    assert_starting_state(new, "expert", 30, 16, 99)


# ---------------------------------------------------------------- abandon_game

def test_abandon_game_from_ready():
    game = make_game()

    game.abandon_game()

    # Ready -> Abandoned, ended_at set, timer stays 0.
    assert game.status == "Abandoned"
    assert game.ended_at is not None
    assert game.elapsed_seconds == 0


def test_abandon_game_from_playing_freezes_timer():
    game = arrange(make_game(), elapsed=42)

    game.abandon_game()
    game.tick()

    # Playing -> Abandoned; the timer is frozen at 42 even when time passes.
    assert game.status == "Abandoned"
    assert game.ended_at is not None
    assert game.elapsed_seconds == 42


@pytest.mark.parametrize("status", ["Won", "Lost", "Abandoned"])
def test_abandon_game_when_finished_changes_nothing(status):
    game = arrange(make_game(), status=status, ended_at=ENDED_AT, elapsed=42)
    before = snapshot(game)

    game.abandon_game()

    # Won/Lost/Abandoned stay as they are, no error.
    assert snapshot(game) == before
    assert game.status == status
