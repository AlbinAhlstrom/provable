import pytest

from src.domain.difficulty_setting import DifficultySetting


# Expected grid per difficulty, read from the specification.
# The spec writes size as "width x height": Expert 30x16 means 30 columns and 16 rows.
EXPECTED = {
    "Beginner": {"rows": 9, "columns": 9, "mine_count": 10},
    "Intermediate": {"rows": 16, "columns": 16, "mine_count": 40},
    "Expert": {"rows": 16, "columns": 30, "mine_count": 99},
}


@pytest.mark.parametrize("name", ["Beginner", "Intermediate", "Expert"])
def test_choosing_difficulty_yields_exact_board_size_and_mine_count(name):
    # Given: a player starting a game. No prior state is needed; the choice alone
    # determines the board.

    # When: the difficulty is chosen by name.
    setting = DifficultySetting.for_difficulty(name)

    # Then: the board dimensions and mine count match the specification exactly.
    # Beginner -> 9 rows, 9 columns, 10 mines (9*9 = 81 cells).
    # Intermediate -> 16 rows, 16 columns, 40 mines (256 cells).
    # Expert -> 16 rows, 30 columns, 99 mines (480 cells).
    expected = EXPECTED[name]
    assert setting.name == name
    assert setting.rows == expected["rows"]
    assert setting.columns == expected["columns"]
    assert setting.mine_count == expected["mine_count"]


def test_beginner_mine_count_is_exactly_ten_not_eleven():
    # Given: a player starting a game.

    # When: Beginner is chosen.
    setting = DifficultySetting.for_difficulty("Beginner")

    # Then: the mine count is exactly 10. Beginner has 81 cells, so 10 mines is
    # the limit specified; one more mine (11) would not match the specification.
    assert setting.mine_count == 10
    assert setting.mine_count != 11


def test_expert_mine_count_is_exactly_ninety_nine_not_one_hundred():
    # Given: a player starting a game.

    # When: Expert is chosen.
    setting = DifficultySetting.for_difficulty("Expert")

    # Then: the mine count is exactly 99 (30x16 = 480 cells). One more mine (100)
    # is just beyond the specified limit and does not match.
    assert setting.mine_count == 99
    assert setting.mine_count != 100


def test_unknown_difficulty_is_rejected():
    # Given: a player starting a game.

    # When: a difficulty that is not one of the three is chosen.
    with pytest.raises(Exception) as exc_info:
        DifficultySetting.for_difficulty("Impossible")

    # Then: the choice is refused.
    assert type(exc_info.value).__name__ == "ValueError"
