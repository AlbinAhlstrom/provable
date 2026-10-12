from src.domain.game_session import GameSession


def test_new_session_starts_in_ready_state():
    # Given: the player has chosen the Expert difficulty (16 rows, 30 columns, 99 mines).
    session = GameSession(
        id="game-1",
        difficulty_id="expert",
        rows=16,
        columns=30,
        mine_count=99,
    )
    # Given: the previous game on this session has already ended as won, with a
    # running clock of 120 seconds, so the session is NOT in the ready state before
    # the new game is started. Its cells are left as constructed (hidden, no mines),
    # which is a valid board for a won game in this arrangement.
    session.status = "won"
    session.elapsed_seconds = 120
    session.started_at = "2025-01-01T10:00:00"
    session.ended_at = "2025-01-01T10:02:00"

    # When: a new game is started at that same difficulty (16 x 30 with 99 mines).
    session.start_new_game(
        difficulty_id="expert",
        rows=16,
        columns=30,
        mine_count=99,
    )

    # Then: the rules say a new game with no reveal yet is in the "ready" status.
    # The start is allowed from the won status, and the status was "won" before the call,
    # so this assertion can only hold if start_new_game changed it.
    assert session.status == "ready"

    # Then: the rules say the timer has not run, so elapsed_seconds is 0.
    # Before the call it was 120, so this assertion can only hold if start_new_game reset it.
    assert session.elapsed_seconds == 0
