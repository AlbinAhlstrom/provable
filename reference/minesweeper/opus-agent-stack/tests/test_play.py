"""R7-R19: revealing, flags, chording, ending, time."""
import pytest

from src.domain.game import Game, GameOver, OutOfBounds
from tests.helpers import board


# ---- R7 numbers -----------------------------------------------------------

def test_r7_revealed_cell_counts_its_mine_neighbours():
    game = board("""
        *.*
        ...
        *..
    """)
    game.reveal(1, 1, now=1.0)
    assert game.revealed == {(1, 1)}
    assert game.adjacent_mines(1, 1) == 3
    assert game.board()[1][1] == "3"


def test_r7_counts_all_eight_directions():
    game = board("""
        ***
        *.*
        ***
    """)
    game.reveal(1, 1, now=1.0)
    assert game.board()[1][1] == "8"


# ---- R8 flood fill --------------------------------------------------------

def test_r8_zero_opens_its_region_and_stops_at_numbers():
    game = board("""
        ....*
        ....*
        .....
        **...
    """)
    game.reveal(0, 0, now=1.0)
    # the zeros (rows 0-1, cols 0-2) open their numbered border and nothing beyond it
    assert game.board() == [
        "0002H",
        "0002H",
        "2211H",
        "HHHHH",
    ]
    assert game.status == "playing"


def test_r8_flood_fill_keeps_flags_and_does_not_open_them():
    game = board("""
        ....
        ....
        ...*
    """)
    game.toggle_flag(0, 1)
    game.reveal(0, 0, now=1.0)
    assert (0, 1) in game.flags
    assert (0, 1) not in game.revealed
    assert game.board()[0][1] == "F"
    assert game.status == "playing"  # the flagged safe cell is still unopened


def test_r8_flood_fill_handles_the_largest_board():
    game = Game.with_mines(rows=24, cols=30, mines={(23, 29)})
    game.reveal(0, 0, now=1.0)
    assert len(game.revealed) == 24 * 30 - 1
    assert game.status == "won"


# ---- R9 harmless repeats --------------------------------------------------

def test_r9_revealing_a_flagged_cell_does_nothing():
    game = board("""
        *..
        ...
    """)
    game.toggle_flag(0, 0)
    game.reveal(0, 0, now=1.0)
    assert game.status == "ready"
    assert game.revealed == set()
    assert game.started_at is None


def test_r9_revealing_a_revealed_cell_does_nothing():
    game = board("""
        *..
        ...
    """)
    game.reveal(0, 1, now=1.0)
    before = (set(game.revealed), game.status, game.started_at)
    game.reveal(0, 1, now=9.0)
    assert (game.revealed, game.status, game.started_at) == before


# ---- R10 losing -----------------------------------------------------------

def test_r10_revealing_a_mine_loses():
    game = board("""
        *..
        ...
        ..*
    """)
    game.reveal(1, 1, now=1.0)
    game.reveal(0, 0, now=4.0)
    assert game.status == "lost"
    assert game.exploded == (0, 0)
    assert game.finished_at == 4.0


# ---- R11, R12 flags -------------------------------------------------------

def test_r11_flag_toggles_on_a_hidden_cell():
    game = board("""
        *..
        ...
    """)
    game.toggle_flag(0, 0)
    assert game.flags == {(0, 0)}
    game.toggle_flag(0, 0)
    assert game.flags == set()


def test_r11_a_revealed_cell_cannot_be_flagged():
    game = board("""
        *..
        ...
    """)
    game.reveal(0, 1, now=1.0)
    game.toggle_flag(0, 1)
    assert game.flags == set()


def test_r12_mines_remaining_counts_down_and_can_go_negative():
    game = board("""
        *...
        ....
    """)
    assert game.mines_remaining == 1
    game.toggle_flag(0, 0)
    assert game.mines_remaining == 0
    game.toggle_flag(1, 3)
    assert game.mines_remaining == -1


# ---- R13-R15 chording -----------------------------------------------------

def chord_board() -> Game:
    game = board("""
        *....
        .....
        ....*
    """)
    game.reveal(1, 1, now=1.0)  # a "1" next to the mine at (0, 0)
    assert game.board()[1][1] == "1"
    return game


def test_r13_chord_opens_the_other_neighbours_when_flags_match():
    game = chord_board()
    game.toggle_flag(0, 0)
    game.chord(1, 1, now=2.0)
    for cell in [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]:
        assert cell in game.revealed
    assert (0, 0) not in game.revealed
    assert game.status != "lost"


def test_r13_chord_flood_fills_through_zeros():
    game = board("""
        *....
        .....
        .....
    """)
    game.reveal(1, 1, now=1.0)
    game.toggle_flag(0, 0)
    game.chord(1, 1, now=2.0)
    assert game.status == "won"  # everything safe is open


def test_r14_chord_does_nothing_when_flag_count_differs():
    game = chord_board()
    game.chord(1, 1, now=2.0)  # no flags yet
    assert game.revealed == {(1, 1)}
    game.toggle_flag(0, 0)
    game.toggle_flag(0, 1)     # two flags around a "1"
    game.chord(1, 1, now=2.0)
    assert game.revealed == {(1, 1)}


def test_r14_chord_on_a_hidden_cell_does_nothing():
    game = chord_board()
    game.chord(2, 2, now=2.0)
    assert game.revealed == {(1, 1)}
    assert game.status == "playing"


def test_r14_chord_on_a_zero_does_nothing():
    game = board("""
        ...*
        ....
    """)
    game.toggle_flag(1, 1)
    game.reveal(0, 0, now=1.0)
    assert game.board()[0][0] == "0"
    before = set(game.revealed)
    game.chord(0, 0, now=2.0)
    assert game.revealed == before


def test_r15_chord_with_a_wrong_flag_loses():
    game = chord_board()
    game.toggle_flag(0, 1)  # wrong: the mine is at (0, 0)
    game.chord(1, 1, now=3.0)
    assert game.status == "lost"
    assert game.exploded == (0, 0)
    assert game.finished_at == 3.0


# ---- R16 winning ----------------------------------------------------------

def test_r16_win_when_every_safe_cell_is_open():
    game = board("""
        *.
        ..
    """)
    game.reveal(0, 1, now=1.0)
    game.reveal(1, 0, now=2.0)
    assert game.status == "playing"
    game.reveal(1, 1, now=7.0)
    assert game.status == "won"
    assert game.finished_at == 7.0


def test_r16_win_flags_every_mine_and_clears_wrong_counts():
    game = board("""
        *..
        ...
        ..*
    """)
    game.toggle_flag(1, 1)        # a wrong flag on a safe cell
    game.toggle_flag(1, 1)        # ...taken back
    game.reveal(0, 2, now=1.0)    # zero: opens the top-right area
    assert game.status == "playing"
    assert game.mines_remaining == 2
    game.reveal(2, 0, now=2.0)    # zero: opens the rest
    assert game.status == "won"
    assert game.flags == {(0, 0), (2, 2)}
    assert game.mines_remaining == 0


def test_r16_win_on_the_very_first_reveal():
    corner = Game.with_mines(rows=5, cols=5, mines={(4, 4)})
    corner.reveal(0, 0, now=3.0)
    assert corner.status == "won"
    assert corner.started_at == 3.0 and corner.finished_at == 3.0
    assert corner.elapsed(now=50.0) == 0


# ---- R17, R18 rejections --------------------------------------------------

def finished_games():
    won = Game.with_mines(rows=5, cols=5, mines={(4, 4)})
    won.reveal(0, 0, now=1.0)
    lost = Game.with_mines(rows=5, cols=5, mines={(4, 4)})
    lost.reveal(4, 4, now=1.0)
    return [won, lost]


@pytest.mark.parametrize("index", [0, 1])
def test_r17_no_action_after_the_game_is_over(index):
    game = finished_games()[index]
    snapshot = game.to_dict()
    with pytest.raises(GameOver):
        game.reveal(0, 0, now=2.0)
    with pytest.raises(GameOver):
        game.toggle_flag(0, 0)
    with pytest.raises(GameOver):
        game.chord(0, 0, now=2.0)
    assert game.to_dict() == snapshot


@pytest.mark.parametrize("row, col", [(-1, 0), (0, -1), (3, 0), (0, 3), (99, 99)])
def test_r18_cells_off_the_board_are_rejected(row, col):
    game = board("""
        *..
        ...
        ...
    """)
    with pytest.raises(OutOfBounds):
        game.reveal(row, col, now=1.0)
    with pytest.raises(OutOfBounds):
        game.toggle_flag(row, col)
    with pytest.raises(OutOfBounds):
        game.chord(row, col, now=1.0)
    assert game.status == "ready"


# ---- R19 time -------------------------------------------------------------

def test_r19_elapsed_runs_from_first_reveal_and_freezes_at_the_end():
    game = board("""
        *..
        ...
        ..*
    """, now=100.0)
    assert game.elapsed(now=150.0) == 0
    game.reveal(1, 1, now=200.0)
    assert game.elapsed(now=200.0) == 0
    assert game.elapsed(now=212.5) == 12.5
    game.reveal(0, 0, now=230.0)  # boom
    assert game.elapsed(now=230.0) == 30.0
    assert game.elapsed(now=9999.0) == 30.0


def test_r19_elapsed_never_goes_negative_if_the_clock_steps_back():
    game = board("""
        *..
        ...
        ..*
    """)
    game.reveal(1, 1, now=200.0)
    assert game.elapsed(now=199.0) == 0
