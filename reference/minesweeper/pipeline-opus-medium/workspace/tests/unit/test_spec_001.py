import pytest

from src.domain.game import Game


CREATED_AT = "2024-01-01T10:00:00+00:00"


def _new_game(difficulty_id, width, height, mine_count, game_id="game-1"):
    return Game(
        id=game_id,
        difficulty_id=difficulty_id,
        width=width,
        height=height,
        mine_count=mine_count,
        remaining_mines=mine_count,
        created_at=CREATED_AT,
    )


def _assert_board_shape_and_mines(game, width, height, mine_count, opened_row, opened_column):
    # The board is a width x height rectangle: one cell per (row, column),
    # rows 0..height-1 and columns 0..width-1, nothing more, nothing less.
    assert len(game.cells) == width * height
    positions = {(cell["row"], cell["column"]) for cell in game.cells}
    expected_positions = {(r, c) for r in range(height) for c in range(width)}
    assert positions == expected_positions

    # Once laid, exactly mine_count cells hold a mine (auto-flagging on a
    # possible win changes state only, never has_mine).
    assert game.mines_laid is True
    mines = [cell for cell in game.cells if cell["has_mine"]]
    assert len(mines) == mine_count

    # First click is safe: the opened cell never holds one of those mines.
    opened = [
        cell for cell in game.cells
        if cell["row"] == opened_row and cell["column"] == opened_column
    ]
    assert len(opened) == 1
    assert opened[0]["has_mine"] is False


@pytest.mark.parametrize(
    "difficulty_id, width, height, mine_count",
    [
        ("beginner", 9, 9, 10),
        ("expert", 30, 16, 99),
        ("custom", 12, 20, 25),
    ],
)
def test_laying_mines_places_exactly_mine_count_on_a_width_by_height_board(
    difficulty_id, width, height, mine_count
):
    # Given a newly created Ready game of width W, height H and mine count M
    game = _new_game(difficulty_id, width, height, mine_count)

    # Before laying: W*H cells, none holds a mine.
    assert len(game.cells) == width * height
    assert sum(1 for cell in game.cells if cell["has_mine"]) == 0

    # When the mines are laid by the first open (a cell inside the grid)
    row, column = height // 2, width // 2
    game.open_cell(row=row, column=column)

    # Then the board still has W*H cells, and exactly M of them hold a mine;
    # M <= (W-1)*(H-1) < W*H - 1 so there is always room off the opened cell.
    _assert_board_shape_and_mines(game, width, height, mine_count, row, column)


def test_mine_count_exactly_at_the_maximum_is_accepted_and_fully_laid():
    # Given a beginner game; a Custom 9x9 board allows at most (9-1)*(9-1) = 64 mines
    game = _new_game("beginner", 9, 9, 10)

    # When the player picks Custom 9x9 with exactly 64 mines (at the limit)
    new_game = game.change_difficulty(
        difficulty_id="custom", width=9, height=9, mine_count=64
    )

    # Then it is accepted: a new Ready game with the chosen configuration
    assert new_game.width == 9
    assert new_game.height == 9
    assert new_game.mine_count == 64
    assert new_game.status == "Ready"

    # When its mines are laid by the first open at the centre (4, 4):
    # 80 other cells exist, so all 64 mines fit off the opened cell.
    new_game.open_cell(row=4, column=4)

    # Then the board has 81 cells and exactly 64 of them hold a mine
    _assert_board_shape_and_mines(new_game, 9, 9, 64, 4, 4)


def test_mine_count_just_beyond_the_maximum_is_refused():
    # Given a beginner game; a Custom 9x9 board allows at most 64 mines
    game = _new_game("beginner", 9, 9, 10)

    # When the player picks Custom 9x9 with 65 mines (one beyond the limit)
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="custom", width=9, height=9, mine_count=65
        )

    # Then the configuration is refused and the current game is unchanged
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    assert game.status == "Ready"
    assert game.difficulty_id == "beginner"
    assert game.width == 9
    assert game.height == 9
    assert game.mine_count == 10
    assert len(game.cells) == 81
    assert sum(1 for cell in game.cells if cell["has_mine"]) == 0
