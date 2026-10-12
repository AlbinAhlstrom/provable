import pytest

from src.domain.difficulty import Difficulty


def test_selecting_intermediate_gives_16_rows_16_columns_40_mines():
    # Given the difficulty presets are available (the preset table is built into the class).
    # When the player selects Intermediate.
    difficulty = Difficulty.select_preset(name="Intermediate")

    # Then the new game board has 16 rows.
    # The Intermediate preset fixes rows at exactly 16 (the value at the limit).
    assert difficulty.rows == 16

    # Then the new game board has 16 columns.
    # The Intermediate preset fixes columns at exactly 16, not the Expert value of 30.
    assert difficulty.columns == 16

    # Then the new game board has 40 mines.
    # The Intermediate preset fixes mine_count at exactly 40, not Beginner's 10 or Expert's 99.
    assert difficulty.mine_count == 40


def test_intermediate_preset_is_not_one_step_beyond_its_limits():
    # Given the difficulty presets are available.
    # When the player selects Intermediate.
    difficulty = Difficulty.select_preset(name="Intermediate")

    # Then the rows are not one step beyond the limit: the value is 16, so it is not 15 or 17.
    assert difficulty.rows not in (15, 17)

    # Then the columns are not one step beyond the limit: the value is 16, so it is not 15 or 17.
    assert difficulty.columns not in (15, 17)

    # Then the mines are not one step beyond the limit: the value is 40, so it is not 39 or 41.
    assert difficulty.mine_count not in (39, 41)
