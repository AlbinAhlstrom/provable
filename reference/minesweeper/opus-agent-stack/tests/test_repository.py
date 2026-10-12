"""The SQLite repository stores and returns games unchanged (R23 through real storage)."""
from src.adapters.sqlite_repository import SqliteGameRepository
from src.domain.game import Game


def make(id: str, now: float) -> Game:
    return Game.new(id=id, difficulty="beginner", seed=4, now=now)


def test_add_then_get_returns_an_equal_game(tmp_path):
    repo = SqliteGameRepository(tmp_path / "games.db")
    game = make("a", 1.0)
    game.reveal(4, 4, now=2.0)
    game.toggle_flag(*sorted(game.mines)[0])
    repo.add(game)
    assert repo.get("a") == game


def test_get_unknown_id_is_none(tmp_path):
    assert SqliteGameRepository(tmp_path / "games.db").get("nope") is None


def test_save_overwrites_the_stored_game(tmp_path):
    repo = SqliteGameRepository(tmp_path / "games.db")
    game = make("a", 1.0)
    repo.add(game)
    game.reveal(0, 0, now=3.0)
    repo.save(game)
    assert repo.get("a").status == game.status != "ready"
    assert len(repo.list()) == 1


def test_list_is_newest_first(tmp_path):
    repo = SqliteGameRepository(tmp_path / "games.db")
    for id, now in [("old", 1.0), ("new", 3.0), ("mid", 2.0)]:
        repo.add(make(id, now))
    assert [g.id for g in repo.list()] == ["new", "mid", "old"]
    assert [g.id for g in repo.list(limit=2)] == ["new", "mid"]


def test_games_survive_reopening_the_database(tmp_path):
    path = tmp_path / "nested" / "games.db"
    SqliteGameRepository(path).add(make("a", 1.0))
    assert SqliteGameRepository(path).get("a") == make("a", 1.0)
