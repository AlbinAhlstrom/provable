from src.domain.game import Game

ROWS = 9
COLUMNS = 9

# Mines chosen so that:
# - the target (4,4) has count 0 (no mine in rows 3-5, cols 3-5)
# - every neighbour of the target has count > 0
# - (2,5) has count 0 and is reachable from the target only through the
#   numbered neighbour (3,4) (or the flagged neighbour (3,5), which must not expand)
MINES = {
    (2, 3),
    (4, 2),
    (4, 6),
    (6, 4),
    (0, 0),
    (0, 8),
    (8, 0),
    (8, 8),
    (0, 4),
    (8, 4),
}


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < ROWS and 0 <= c < COLUMNS:
                yield r, c


def _build_cells(flagged):
    cells = []
    for r in range(ROWS):
        for c in range(COLUMNS):
            count = sum(1 for nr, nc in _neighbours(r, c) if (nr, nc) in MINES)
            state = "flagged" if (r, c) in flagged else "hidden"
            cells.append(
                {
                    "id": f"r{r}c{c}",
                    "row": r,
                    "column": c,
                    "has_mine": (r, c) in MINES,
                    "adjacent_mine_count": count,
                    "state": state,
                }
            )
    return cells


def _cell(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at {row},{column}")


def test_zero_expansion_stops_at_numbered_cells_and_respects_flags():
    # Given an in-progress Beginner game where the target (4,4) has count 0,
    # its neighbour (3,4) has count 1, its neighbour (3,5) is flagged,
    # and (2,5) is a zero-count hidden cell reachable only through (3,4) or (3,5).
    game = Game(id="game-zero-stop")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = "2024-01-01T10:00:00"
    game.mine_count = 10
    game.flag_count = 1
    game.cells = _build_cells(flagged={(3, 5)})

    # When the player reveals the zero-count cell (4,4).
    game.reveal_cell(row=4, column=4)

    # Then the target itself is revealed (it was hidden, unflagged, count 0).
    # Its count is 0: no mine among (3..5, 3..5).
    assert _cell(game, 4, 4)["state"] == "revealed"

    # And the numbered neighbour (3,4) is revealed: it was hidden and unflagged;
    # it has count 1 from the mine at (2,3).
    assert _cell(game, 3, 4)["adjacent_mine_count"] == 1
    assert _cell(game, 3, 4)["state"] == "revealed"

    # And the flagged neighbour (3,5) is not revealed; it stays flagged
    # (it is a neighbour of the zero target, but flagged cells are never revealed).
    assert _cell(game, 3, 5)["state"] == "flagged"

    # And expansion does not continue beyond the numbered neighbour (3,4):
    # (2,5) has count 0 and would be revealed by a wrong expansion through (3,4),
    # but it must stay hidden. Its neighbours (1..3, 4..6) hold no mine.
    assert _cell(game, 2, 5)["adjacent_mine_count"] == 0
    assert _cell(game, 2, 5)["state"] == "hidden"

    # And the flag count and status are unchanged by the reveal.
    assert game.flag_count == 1
    assert game.status == "in_progress"
