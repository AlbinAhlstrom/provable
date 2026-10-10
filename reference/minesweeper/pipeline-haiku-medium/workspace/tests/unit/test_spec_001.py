from src.domain.difficulty import Difficulty


def test_selecting_beginner_gives_9_rows_9_columns_10_mines():
    # Given: the difficulty presets are available (Beginner is one of them).
    # When: the player selects Beginner.
    beginner = Difficulty.select_preset(name="Beginner")

    # Then: the preset's board is exactly 9 rows, 9 columns and 10 mines.
    # Rows: the Beginner preset fixes rows at 9 (the at-limit value).
    assert beginner.rows == 9
    # Columns: the Beginner preset fixes columns at 9 (the at-limit value).
    assert beginner.columns == 9
    # Mines: the Beginner preset fixes mine_count at 10 (the at-limit value).
    assert beginner.mine_count == 10


def test_beginner_rows_and_columns_stop_at_9_not_one_beyond():
    # Given: the difficulty presets are available.
    # When: the player selects Beginner.
    beginner = Difficulty.select_preset(name="Beginner")

    # Then: the board is not one step beyond the limit of 9 in either direction.
    # One beyond the limit would be 10 rows, which Beginner must not use.
    assert beginner.rows != 10
    # One beyond the limit would be 10 columns, which Beginner must not use.
    assert beginner.columns != 10
    # Only the 9-row, 9-column board is Beginner, so rows is strictly below 10.
    assert beginner.rows < 10
    # And columns is strictly below 10.
    assert beginner.columns < 10


def test_beginner_mine_count_stops_at_10_not_one_beyond():
    # Given: the difficulty presets are available.
    # When: the player selects Beginner.
    beginner = Difficulty.select_preset(name="Beginner")

    # Then: the mine count is not one beyond the limit of 10.
    # One beyond the limit would be 11 mines, which Beginner must not use.
    assert beginner.mine_count != 11
    # Exactly 10 mines is the limit, so the count is strictly below 11.
    assert beginner.mine_count < 11
