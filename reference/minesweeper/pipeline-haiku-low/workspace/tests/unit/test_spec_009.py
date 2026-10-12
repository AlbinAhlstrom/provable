from src.domain.game import Game


MINES = {(0, 0), (8, 8)}
ROWS = 9
COLUMNS = 9
STARTED = "2024-01-01T10:00:00+00:00"
LOST_AT = "2024-01-01T10:00:42+00:00"


def _neighbour_mine_count(row, column):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < ROWS and 0 <= c < COLUMNS and (r, c) in MINES:
                count += 1
    return count


def _build_cells():
    cells = []
    for r in range(ROWS):
        for c in range(COLUMNS):
            cells.append({
                "id": f"cell-{r}-{c}",
                "row": r,
                "column": c,
                "has_mine": (r, c) in MINES,
                "adjacent_mine_count": _neighbour_mine_count(r, c),
                "state": "hidden",
            })
    return cells


def _in_progress_game():
    game = Game(id="game-1")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    # Timestamps are timezone-aware, matching the moment passed to reveal_cell.
    game.started_at = STARTED
    game.mine_count = len(MINES)
    game.flag_count = 0
    game.cells = _build_cells()
    return game


def _cell(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at {row},{column}")


def test_revealing_a_mine_loses_the_game_and_shows_all_mines():
    # Given an in-progress 9x9 board with mines at (0,0) and (8,8) and no flags.
    # (0,0) is hidden and unflagged, so the reveal is not blocked by any rule.
    game = _in_progress_game()

    # When the player reveals the mine at (0,0), at a fixed moment 42 seconds after start.
    game.reveal_cell(row=0, column=0, now=LOST_AT)

    # Then the status becomes "lost": (0,0) has has_mine true, so the session ends as lost.
    assert game.status == "lost"

    # And ended_at is set to the moment passed in, since the session has ended.
    assert game.ended_at == LOST_AT

    # And elapsed_seconds is fixed at 42 (from STARTED to LOST_AT), a sanity check on the timer stop.
    assert game.elapsed_seconds == 42

    # And every mine cell is shown as revealed:
    # (0,0) is the cell just hit, and (8,8) is a second hidden mine that must be exposed at game end.
    assert _cell(game, 0, 0)["state"] == "revealed"
    assert _cell(game, 8, 8)["state"] == "revealed"
