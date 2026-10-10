from src.domain.game import Game

import pytest


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10

# Mines: the whole top row (0,0)..(0,8) plus (1,0), giving 10 mines.
MINES = {(0, c) for c in range(WIDTH)} | {(1, 0)}


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _adjacent(row, column):
    return sum(1 for n in _neighbours(row, column) if n in MINES)


def _make_playing_game(hidden_safe, flag_mines=None, flagged_safe=()):
    """Build a 9x9 Playing game with mines already laid.

    Every safe cell is Opened except those listed in hidden_safe (Hidden)
    and flagged_safe (Flagged). Mine cells in flag_mines are Flagged;
    the other mine cells are Hidden.
    """
    flag_mines = set(flag_mines or ())
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
    for r in range(HEIGHT):
        for c in range(WIDTH):
            has_mine = (r, c) in MINES
            if has_mine:
                state = "Flagged" if (r, c) in flag_mines else "Hidden"
            elif (r, c) in flagged_safe:
                state = "Flagged"
            elif (r, c) in hidden_safe:
                state = "Hidden"
            else:
                state = "Opened"
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": has_mine,
                    "adjacent_mine_count": _adjacent(r, c),
                    "state": state,
                }
            )
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    flags = len(flag_mines) + len(flagged_safe)
    game.flags_placed = flags
    game.remaining_mines = MINE_COUNT - flags
    game.elapsed_seconds = 42
    game.started_at = "2024-01-01T10:00:05"
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


@pytest.mark.parametrize(
    "flag_mines",
    [
        set(),  # no mine flagged
        set(MINES),  # every mine flagged
        {(0, 0), (0, 4), (1, 0)},  # some mines flagged
    ],
    ids=["no_flags", "all_mines_flagged", "some_mines_flagged"],
)
def test_opening_last_non_mine_cell_wins_regardless_of_flags(flag_mines):
    # Only safe cell left unopened is (1,1). Its neighbours (0,0),(0,1),(0,2),(1,0)
    # are mines, so its count is 4: no cascade is triggered.
    game = _make_playing_game(hidden_safe={(1, 1)}, flag_mines=flag_mines)

    game.open_cell(row=1, column=1)

    # (1,1) is Hidden and safe -> becomes Opened.
    assert _cell(game, 1, 1)["state"] == "Opened"
    # Now every one of the 71 non-mine cells is Opened -> Won, whatever the flags.
    assert game.status == "Won"
    # Win records an end time.
    assert game.ended_at is not None
    # No mine was opened: nothing struck.
    assert game.struck_cell_id is None
    # Auto-flag on win: all 10 mine cells Flagged, flags_placed 10, remaining 0.
    for r, c in MINES:
        assert _cell(game, r, c)["state"] == "Flagged"
    assert game.flags_placed == MINE_COUNT
    assert game.remaining_mines == 0
    # Timer is not advanced by opening; it is frozen at 42.
    assert game.elapsed_seconds == 42
    # Every safe cell is Opened.
    for cell in game.cells:
        if not cell["has_mine"]:
            assert cell["state"] == "Opened"


@pytest.mark.parametrize(
    "flag_mines",
    [set(), set(MINES)],
    ids=["no_flags", "all_mines_flagged"],
)
def test_not_won_while_a_hidden_non_mine_cell_remains(flag_mines):
    # Two safe cells unopened: (1,1) with count 4 and (1,2) with count 3
    # (neighbours (0,1),(0,2),(0,3)). Opening (1,1) does not cascade, so (1,2)
    # stays Hidden.
    game = _make_playing_game(hidden_safe={(1, 1), (1, 2)}, flag_mines=flag_mines)
    flags_before = game.flags_placed
    remaining_before = game.remaining_mines

    game.open_cell(row=1, column=1)

    # (1,1) opened.
    assert _cell(game, 1, 1)["state"] == "Opened"
    # (1,2) is a non-mine cell still Hidden -> not Won, still Playing.
    assert _cell(game, 1, 2)["state"] == "Hidden"
    assert game.status == "Playing"
    assert game.ended_at is None
    # No auto-flag happened: counters unchanged.
    assert game.flags_placed == flags_before
    assert game.remaining_mines == remaining_before


def test_not_won_while_a_flagged_non_mine_cell_remains_unopened():
    # Safe cell (1,2) is Flagged (not opened); (1,1) is the only Hidden safe cell.
    # All mines flagged too except one, so flags placed = 9 mines + 1 safe = 10.
    flag_mines = set(MINES) - {(0, 8)}
    game = _make_playing_game(
        hidden_safe={(1, 1)}, flag_mines=flag_mines, flagged_safe={(1, 2)}
    )

    game.open_cell(row=1, column=1)

    # (1,1) opened (count 4, no cascade).
    assert _cell(game, 1, 1)["state"] == "Opened"
    # (1,2) is safe but Flagged, i.e. not opened -> the game is not Won.
    assert _cell(game, 1, 2)["state"] == "Flagged"
    assert game.status == "Playing"
    assert game.ended_at is None
    assert game.flags_placed == 10
    assert game.remaining_mines == 0
