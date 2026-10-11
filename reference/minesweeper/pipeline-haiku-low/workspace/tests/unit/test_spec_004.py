import pytest

from src.domain.game import Game


ROWS = 9
COLUMNS = 9
MINE_COUNT = 10


def build_empty_beginner_game() -> Game:
    """Beginner board in its newly created shape: one hidden, mine-free cell per position."""
    game = Game(id="game-first-click")
    game.difficulty = "Beginner"
    game.status = "ready"
    game.mine_count = MINE_COUNT
    game.cells = [
        {
            "id": f"c{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "hidden",
        }
        for row in range(ROWS)
        for column in range(COLUMNS)
    ]
    return game


def cell_at(game: Game, row: int, column: int) -> dict:
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def neighbour_positions(row: int, column: int):
    for d_row in (-1, 0, 1):
        for d_column in (-1, 0, 1):
            if d_row == 0 and d_column == 0:
                continue
            n_row = row + d_row
            n_column = column + d_column
            if 0 <= n_row < ROWS and 0 <= n_column < COLUMNS:
                yield n_row, n_column


def mine_positions(game: Game):
    return sorted(
        (cell["row"], cell["column"]) for cell in game.cells if cell["has_mine"]
    )


def test_first_reveal_target_and_all_neighbours_are_mine_free():
    # Given a ready Beginner game (9x9, 10 mines, no layout fixed yet).
    game = build_empty_beginner_game()
    assert game.status == "ready"

    # When the first cell, the centre (4, 4), is revealed.
    game.reveal_cell(row=4, column=4)

    # Then the target cell has no mine:
    # the centre is not a mine because the layout avoids the target itself.
    assert cell_at(game, 4, 4)["has_mine"] is False

    # And each of its eight neighbours has no mine:
    # the layout avoids the target and every cell adjacent to it,
    # which are all inside the 9x9 board since (4, 4) is central.
    for n_row, n_column in neighbour_positions(4, 4):
        assert cell_at(game, n_row, n_column)["has_mine"] is False, (
            f"neighbour ({n_row}, {n_column}) must be mine-free"
        )


def test_first_reveal_fixes_the_mine_layout():
    # Given a ready Beginner game with no layout fixed.
    game = build_empty_beginner_game()

    # When the first cell (4, 4) is revealed.
    game.reveal_cell(row=4, column=4)

    # Then the layout is fixed with exactly mine_count mines on the board:
    # 10 mines are placed on the 81 cells, none on the protected 3x3 area.
    layout_after_first_reveal = mine_positions(game)
    assert len(layout_after_first_reveal) == MINE_COUNT

    # And the layout does not move when a further safe cell is revealed:
    # (4, 5) is a neighbour of the target, so it is mine-free and not a loss;
    # the game stays in progress with 71 safe cells still hidden,
    # so no other rule ends the game or changes the mines.
    game.reveal_cell(row=4, column=5)
    assert mine_positions(game) == layout_after_first_reveal
    assert game.status == "in_progress"
