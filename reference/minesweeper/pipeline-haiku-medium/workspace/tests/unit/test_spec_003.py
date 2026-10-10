from src.domain.difficulty import Difficulty


def test_selecting_expert_gives_a_board_of_16_rows_30_columns_and_99_mines():
    # Given: the difficulty presets are available (the preset table is built into Difficulty).
    # When: the player selects the Expert preset.
    selected = Difficulty.select_preset(name="Expert")

    # Then: the Expert preset fixes the board at 16 rows.
    # Expert is defined as 16 rows, so rows must be 16.
    assert selected.rows == 16

    # Then: the Expert preset fixes the board at 30 columns.
    # Expert is defined as 30 columns, so columns must be 30.
    assert selected.columns == 30

    # Then: the Expert preset places 99 mines.
    # Expert is defined as 99 mines, so mine_count must be 99.
    assert selected.mine_count == 99


def test_expert_preset_is_exactly_at_30_columns_and_99_mines_not_one_beyond():
    # Given: the difficulty presets are available.
    # When: the player selects the Expert preset.
    selected = Difficulty.select_preset(name="Expert")

    # Exactly at the limit: 30 columns is accepted and the preset keeps that exact value.
    # The Expert preset has 30 columns, so the value equals 30.
    assert selected.columns == 30

    # Just beyond the limit: 31 columns would be a different board and must not be the Expert preset.
    # The Expert preset has 30 columns, so it is not 31.
    assert selected.columns != 31

    # Exactly at the limit: 99 mines is accepted and the preset keeps that exact value.
    # The Expert preset has 99 mines, so the value equals 99.
    assert selected.mine_count == 99

    # Just beyond the limit: 100 mines would be a different board and must not be the Expert preset.
    # The Expert preset has 99 mines, so it is not 100.
    assert selected.mine_count != 100
