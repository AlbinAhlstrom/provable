import pytest

from src.domain.game import Game

WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10

# Mine layout for the Playing board: the whole top row plus (1, 0) = 10 mines.
MINE_POSITIONS = [(0, c) for c in range(9)] + [(1, 0)]
# Cells flagged before the action: the 10 mine cells first, then safe extras
# (rows 2-3 are safe cells, far from the target cell (8, 8)).
FLAG_ORDER = MINE_POSITIONS + [(2, 4), (2, 5)]
TARGET = (8, 8)


def _neighbour_mines(row, column, mines):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH and (r, c) in mines:
                count += 1
    return count


def _build_game(status, flags_already, target_state="Hidden"):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    mines = set(MINE_POSITIONS) if status == "Playing" else set()
    flagged = set(FLAG_ORDER[:flags_already])
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            state = "Flagged" if (row, column) in flagged else "Hidden"
            if (row, column) == TARGET:
                state = target_state
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in mines,
                    "adjacent_mine_count": _neighbour_mines(row, column, mines)
                    if status == "Playing"
                    else 0,
                    "state": state,
                }
            )
    game.cells = cells
    game.status = status
    game.mines_laid = status == "Playing"
    game.started_at = "2024-01-01T10:00:05" if status == "Playing" else None
    game.flags_placed = flags_already
    game.remaining_mines = MINE_COUNT - flags_already
    game.events = []
    return game


def _cell(game, row, column):
    return next(c for c in game.cells if c["row"] == row and c["column"] == column)


@pytest.mark.parametrize("status", ["Ready", "Playing"])
@pytest.mark.parametrize("flags_already", [MINE_COUNT - 1, MINE_COUNT, MINE_COUNT + 1])
def test_flagging_hidden_cell_is_not_limited_by_mine_count(status, flags_already):
    game = _build_game(status, flags_already)
    before = {c["id"]: c["state"] for c in game.cells}

    game.toggle_flag(row=TARGET[0], column=TARGET[1])

    # Target (8, 8) was Hidden, status Ready/Playing allows flagging, and flags
    # are unlimited, so it becomes Flagged even when flags_placed >= mine_count.
    assert _cell(game, *TARGET)["state"] == "Flagged"
    # flags_placed goes up by one from flags_already (9, 10 or 11).
    assert game.flags_placed == flags_already + 1
    # remaining_mines = 10 - (flags_already + 1): 0, -1 or -2 (negative allowed).
    assert game.remaining_mines == MINE_COUNT - (flags_already + 1)
    # Flagging opens nothing, so no win/loss/transition: status stays the same.
    assert game.status == status
    # Every other cell keeps its previous state.
    for c in game.cells:
        if c["id"] != f"{TARGET[0]}-{TARGET[1]}":
            assert c["state"] == before[c["id"]]


def test_flagging_opened_cell_at_mine_count_is_ignored():
    # Same board as the accepted Playing case with 10 flags, but the target is
    # Opened (it is safe, with 0 adjacent mines since mines are in rows 0-1).
    game = _build_game("Playing", MINE_COUNT, target_state="Opened")
    before = {c["id"]: c["state"] for c in game.cells}

    game.toggle_flag(row=TARGET[0], column=TARGET[1])

    # An Opened cell cannot become Flagged: the toggle is ignored, no error.
    assert _cell(game, *TARGET)["state"] == "Opened"
    # flags_placed stays at 10 and remaining_mines at 10 - 10 = 0.
    assert game.flags_placed == MINE_COUNT
    assert game.remaining_mines == 0
    # Nothing else changes.
    assert game.status == "Playing"
    assert {c["id"]: c["state"] for c in game.cells} == before
