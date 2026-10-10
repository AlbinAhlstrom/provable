"""R20-R23: what the player sees, statistics, round trip."""
import json

from src.domain.game import Game
from src.domain.stats import summarize
from tests.helpers import board


# ---- R20 hidden information ----------------------------------------------

def test_r20_view_in_play_shows_only_hidden_flags_and_numbers():
    game = Game.new(id="g", difficulty="expert", seed=11, now=0.0)
    game.toggle_flag(0, 0)
    game.reveal(8, 15, now=1.0)
    assert game.status == "playing"
    view = game.view(now=2.0)
    assert len(view.board) == 16 and all(len(row) == 30 for row in view.board)
    assert set("".join(view.board)) <= set("HF012345678")
    assert view.board[0][0] == "F"


def test_r20_view_carries_no_mines_and_no_seed():
    game = Game.new(id="g", difficulty="beginner", seed=987654321, now=0.0)
    game.reveal(4, 4, now=1.0)
    fields = game.view(now=2.0).as_dict()
    assert set(fields) == {
        "id", "difficulty", "rows", "cols", "mine_count", "status",
        "mines_remaining", "elapsed_seconds", "created_at", "board",
    }
    assert "987654321" not in json.dumps(fields)


def test_r20_a_hidden_mine_looks_like_any_hidden_cell():
    game = board("""
        *..
        ...
        ..*
    """)
    game.reveal(1, 1, now=1.0)
    assert game.view(now=1.0).board == ["HHH", "H2H", "HHH"]


def test_view_reports_counter_status_and_time():
    game = board("""
        *..
        ...
        ..*
    """)
    game.toggle_flag(0, 0)
    game.reveal(1, 1, now=10.0)
    view = game.view(now=14.0)
    assert view.status == "playing"
    assert view.mines_remaining == 1
    assert view.elapsed_seconds == 4.0
    assert (view.rows, view.cols, view.mine_count) == (3, 3, 2)


# ---- R21 the board after a loss -------------------------------------------

def test_r21_loss_shows_exploded_mine_other_mines_and_wrong_flags():
    game = board("""
        *.*.
        ....
        *...
    """)
    game.reveal(1, 1, now=1.0)
    game.toggle_flag(0, 2)   # correct flag
    game.toggle_flag(1, 3)   # wrong flag
    game.reveal(0, 0, now=2.0)
    assert game.status == "lost"
    assert game.view(now=3.0).board == [
        "XHFH",
        "H3HW",
        "MHHH",
    ]


def test_r21_win_shows_every_mine_as_a_flag():
    game = board("""
        *..
        ...
        ...
    """)
    game.reveal(2, 2, now=1.0)
    assert game.status == "won"
    assert game.view(now=1.0).board == ["F10", "110", "000"]


# ---- R22 statistics --------------------------------------------------------

def _finished(difficulty: str, won: bool, seconds: float) -> Game:
    game = Game.with_mines(rows=5, cols=5, mines={(4, 4)}, difficulty=difficulty)
    game.reveal(3, 3, now=0.0)  # a "1": still playing
    if won:
        game.reveal(0, 0, now=seconds)
    else:
        game.reveal(4, 4, now=seconds)
    assert game.status == ("won" if won else "lost")
    return game


def test_r22_counts_and_best_time_per_difficulty():
    games = [
        _finished("beginner", True, 40.0),
        _finished("beginner", True, 25.5),
        _finished("beginner", False, 3.0),
        _finished("expert", False, 100.0),
    ]
    stats = summarize(games)
    assert stats["beginner"].played == 3
    assert stats["beginner"].won == 2
    assert stats["beginner"].best_seconds == 25.5
    assert round(stats["beginner"].win_rate, 3) == 0.667
    assert stats["expert"].played == 1
    assert stats["expert"].won == 0
    assert stats["expert"].best_seconds is None
    assert stats["expert"].win_rate == 0


def test_r22_every_difficulty_is_present_even_with_no_games():
    stats = summarize([])
    assert set(stats) == {"beginner", "intermediate", "expert", "custom"}
    assert all(s.played == 0 and s.won == 0 and s.best_seconds is None and s.win_rate == 0
               for s in stats.values())


def test_r22_unfinished_games_do_not_count():
    ready = Game.new(id="a", difficulty="beginner", seed=1, now=0.0)
    playing = Game.new(id="b", difficulty="beginner", seed=1, now=0.0)
    playing.reveal(4, 4, now=1.0)
    assert playing.status == "playing"
    assert summarize([ready, playing])["beginner"].played == 0


# ---- R23 round trip --------------------------------------------------------

def test_r23_a_game_survives_save_and_load_at_every_stage():
    ready = Game.new(id="r", difficulty="custom", seed=3, now=1.0, rows=6, cols=7, mines=5)
    ready.toggle_flag(0, 0)

    playing = Game.new(id="p", difficulty="beginner", seed=3, now=1.0)
    playing.reveal(4, 4, now=2.0)
    playing.toggle_flag(*sorted(playing.mines)[0])

    lost = board("""
        *..
        ...
        ..*
    """)
    lost.reveal(0, 0, now=5.0)

    for game in (ready, playing, lost):
        stored = json.loads(json.dumps(game.to_dict()))  # must be plain JSON
        loaded = Game.from_dict(stored)
        assert loaded == game
        assert loaded.view(now=9.0) == game.view(now=9.0)


def test_r23_a_loaded_game_plays_on_identically():
    a = Game.new(id="p", difficulty="beginner", seed=3, now=1.0)
    b = Game.from_dict(json.loads(json.dumps(a.to_dict())))
    a.reveal(4, 4, now=2.0)
    b.reveal(4, 4, now=2.0)
    assert a == b
