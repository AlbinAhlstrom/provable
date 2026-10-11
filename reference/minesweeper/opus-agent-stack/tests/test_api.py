"""The HTTP layer: every endpoint, its error codes, and that nothing secret leaks."""
import itertools
import json

import pytest
from fastapi.testclient import TestClient

from src.adapters.sqlite_repository import SqliteGameRepository
from src.app import create_app


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def ctx(tmp_path):
    clock = Clock()
    repo = SqliteGameRepository(tmp_path / "games.db")
    ids = (f"game-{n}" for n in itertools.count(1))
    app = create_app(repository=repo, clock=clock, new_seed=lambda: 31337, new_id=lambda: next(ids))
    return TestClient(app), repo, clock


def create(client, **body):
    response = client.post("/api/games", json=body or {"difficulty": "beginner"})
    assert response.status_code == 201, response.text
    return response.json()


def test_difficulties_lists_presets_and_custom_limits(ctx):
    client, _, _ = ctx
    body = client.get("/api/difficulties").json()
    assert [p["key"] for p in body["presets"]] == ["beginner", "intermediate", "expert"]
    assert body["presets"][2] == {"key": "expert", "rows": 16, "cols": 30, "mines": 99}
    assert body["custom"] == {"min_side": 5, "max_rows": 24, "max_cols": 30, "first_area": 9}


def test_create_returns_a_ready_game(ctx):
    client, _, _ = ctx
    game = create(client)
    assert game["id"] == "game-1"
    assert game["status"] == "ready"
    assert game["board"] == ["H" * 9] * 9
    assert game["mines_remaining"] == 10
    assert game["elapsed_seconds"] == 0


def test_create_custom_and_reject_bad_custom(ctx):
    client, _, _ = ctx
    game = create(client, difficulty="custom", rows=6, cols=8, mines=7)
    assert (game["rows"], game["cols"], game["mine_count"]) == (6, 8, 7)
    bad = client.post("/api/games", json={"difficulty": "custom", "rows": 6, "cols": 8, "mines": 40})
    assert bad.status_code == 422
    assert bad.json()["detail"] == "A board of 6 rows and 8 columns holds between 1 and 39 mines."
    assert client.post("/api/games", json={"difficulty": "silly"}).status_code == 422


def test_get_and_list(ctx):
    client, _, clock = ctx
    first = create(client)
    clock.now += 5
    second = create(client, difficulty="expert")
    assert client.get(f"/api/games/{first['id']}").json() == first
    listed = client.get("/api/games").json()
    assert [g["id"] for g in listed] == [second["id"], first["id"]]
    assert "board" not in listed[0]
    assert listed[0]["difficulty"] == "expert"


def test_unknown_game_is_404_everywhere(ctx):
    client, _, _ = ctx
    assert client.get("/api/games/nope").status_code == 404
    for action in ("reveal", "flag", "chord"):
        assert client.post(f"/api/games/nope/{action}", json={"row": 0, "col": 0}).status_code == 404


def test_reveal_plays_saves_and_times(ctx):
    client, repo, clock = ctx
    game = create(client)
    clock.now += 3
    after = client.post(f"/api/games/{game['id']}/reveal", json={"row": 4, "col": 4}).json()
    assert after["status"] == "playing"
    assert after["board"][4][4] == "0"
    assert after["elapsed_seconds"] == 0
    clock.now += 12
    assert client.get(f"/api/games/{game['id']}").json()["elapsed_seconds"] == 12
    stored = repo.get(game["id"])
    assert stored.status == "playing" and len(stored.mines) == 10


def test_flag_toggles_and_is_saved(ctx):
    client, repo, _ = ctx
    game = create(client)
    url = f"/api/games/{game['id']}/flag"
    after = client.post(url, json={"row": 0, "col": 0}).json()
    assert after["board"][0][0] == "F" and after["mines_remaining"] == 9
    assert repo.get(game["id"]).flags == {(0, 0)}
    after = client.post(url, json={"row": 0, "col": 0}).json()
    assert after["board"][0][0] == "H" and after["mines_remaining"] == 10


def _play_to_the_end(client, repo, game_id, win: bool):
    """Use the stored mines (the test may peek; the API may not) to finish a game."""
    client.post(f"/api/games/{game_id}/reveal", json={"row": 4, "col": 4})
    stored = repo.get(game_id)
    if not win:
        row, col = sorted(stored.mines)[0]
        return client.post(f"/api/games/{game_id}/reveal", json={"row": row, "col": col})
    response = None
    for row in range(stored.rows):
        for col in range(stored.cols):
            if (row, col) not in stored.mines and repo.get(game_id).status == "playing":
                response = client.post(f"/api/games/{game_id}/reveal", json={"row": row, "col": col})
    return response


def test_chord_opens_neighbours(ctx):
    client, repo, _ = ctx
    game = create(client)
    client.post(f"/api/games/{game['id']}/reveal", json={"row": 4, "col": 4})
    stored = repo.get(game["id"])
    # find a revealed "1" and flag its one mine, then chord it
    for (row, col) in sorted(stored.revealed):
        if stored.adjacent_mines(row, col) == 1:
            break
    mine = next(m for m in stored.mines if abs(m[0] - row) <= 1 and abs(m[1] - col) <= 1)
    client.post(f"/api/games/{game['id']}/flag", json={"row": mine[0], "col": mine[1]})
    before = len(repo.get(game["id"]).revealed)
    response = client.post(f"/api/games/{game['id']}/chord", json={"row": row, "col": col})
    assert response.status_code == 200
    after = repo.get(game["id"])
    assert after.status != "lost"
    assert len(after.revealed) >= before
    hidden_around = [
        (r, c) for r in range(row - 1, row + 2) for c in range(col - 1, col + 2)
        if 0 <= r < 9 and 0 <= c < 9 and (r, c) not in after.revealed and (r, c) != mine
    ]
    assert hidden_around == []


def test_losing_reveals_the_mines_and_then_refuses_actions(ctx):
    client, repo, _ = ctx
    game = create(client)
    lost = _play_to_the_end(client, repo, game["id"], win=False).json()
    assert lost["status"] == "lost"
    flat = "".join(lost["board"])
    assert flat.count("X") == 1 and flat.count("M") == 9
    for action in ("reveal", "flag", "chord"):
        refused = client.post(f"/api/games/{game['id']}/{action}", json={"row": 0, "col": 0})
        assert refused.status_code == 409
        assert "already lost" in refused.json()["detail"]


def test_winning_stops_the_clock_and_feeds_the_statistics(ctx):
    client, repo, clock = ctx
    game = create(client)
    client.post(f"/api/games/{game['id']}/reveal", json={"row": 4, "col": 4})
    clock.now += 42.5
    won = _play_to_the_end(client, repo, game["id"], win=True).json()
    assert won["status"] == "won"
    assert won["elapsed_seconds"] == 42.5
    assert won["mines_remaining"] == 0
    clock.now += 100
    assert client.get(f"/api/games/{game['id']}").json()["elapsed_seconds"] == 42.5

    lost_game = create(client)
    _play_to_the_end(client, repo, lost_game["id"], win=False)
    create(client)  # never started: must not count

    stats = client.get("/api/stats").json()
    assert stats["beginner"] == {"played": 2, "won": 1, "best_seconds": 42.5, "win_rate": 0.5}
    assert stats["expert"] == {"played": 0, "won": 0, "best_seconds": None, "win_rate": 0}


def test_off_board_cell_is_422_with_a_readable_message(ctx):
    client, _, _ = ctx
    game = create(client)
    response = client.post(f"/api/games/{game['id']}/reveal", json={"row": 9, "col": 0})
    assert response.status_code == 422
    assert response.json()["detail"] == "Row 10, column 1 is outside the board (9 rows, 9 columns)."


def test_malformed_body_is_422_with_a_string_detail(ctx):
    client, _, _ = ctx
    game = create(client)
    response = client.post(f"/api/games/{game['id']}/reveal", json={"row": "x"})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_r20_no_response_leaks_mines_or_seed_during_play(ctx):
    client, repo, _ = ctx
    game = create(client)
    responses = [
        client.post(f"/api/games/{game['id']}/reveal", json={"row": 4, "col": 4}),
        client.post(f"/api/games/{game['id']}/flag", json={"row": 0, "col": 0}),
        client.get(f"/api/games/{game['id']}"),
        client.get("/api/games"),
        client.get("/api/stats"),
    ]
    assert repo.get(game["id"]).status == "playing"
    for response in responses:
        text = response.text
        assert "31337" not in text
        assert "seed" not in text and '"mines"' not in text
    board = "".join(responses[2].json()["board"])
    assert set(board) <= set("HF012345678")
