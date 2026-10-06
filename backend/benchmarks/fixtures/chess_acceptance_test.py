"""
Authoritative Chess Ground-Truth Acceptance Test Suite.
Used across all AppGen benchmark contenders to objectively measure
domain invariant enforcement, move validation, and turn alternation.
"""

import pytest


def get_chess_game():
    """Dynamically discovers and imports the Chess aggregate root."""
    import sys, os
    cur_dir = os.path.dirname(__file__)
    ws_root = os.path.abspath(os.path.join(cur_dir, "..", ".."))
    src_dir = os.path.join(ws_root, "src")
    for p in (ws_root, src_dir):
        if p not in sys.path and os.path.exists(p):
            sys.path.insert(0, p)

    for mod_name in ("domain.game", "domain.chess", "domain.model", "src.domain.game", "src.domain.chess", "src.domain.model"):
        try:
            mod = __import__(mod_name, fromlist=["ChessGame", "Game"])
            if hasattr(mod, "ChessGame"):
                return getattr(mod, "ChessGame")()
            if hasattr(mod, "Game"):
                return getattr(mod, "Game")()
        except ImportError:
            continue

    pytest.fail("Could not import ChessGame or Game aggregate from domain layer")


def test_board_initial_setup():
    """GIVEN a new chess match, THEN standard starting configuration and White to move."""
    game = get_chess_game()
    assert hasattr(game, "turn") or hasattr(game, "current_player") or hasattr(game, "active_color")
    turn = getattr(game, "turn", getattr(game, "current_player", getattr(game, "active_color", "white")))
    assert str(turn).lower() in ("white", "w")


def test_pawn_initial_two_square_and_single_square():
    """GIVEN a starting pawn, WHEN moving 1 or 2 squares forward, THEN move succeeds."""
    game = get_chess_game()
    # Attempt legal e2 -> e4 move
    success = False
    if hasattr(game, "make_move"):
        res = game.make_move("e2", "e4")
        success = res is not False
    elif hasattr(game, "move"):
        res = game.move("e2", "e4")
        success = res is not False
    elif hasattr(game, "play_move"):
        res = game.play_move(from_pos="e2", to_pos="e4")
        success = res is not False

    assert success, "Pawn initial 2-square advance from e2 to e4 should be legal."


def test_knight_can_jump_over_occupying_pieces():
    """GIVEN starting board, WHEN knight moves to c3, THEN move succeeds despite pawn obstruction."""
    game = get_chess_game()
    success = False
    if hasattr(game, "make_move"):
        res = game.make_move("b1", "c3")
        success = res is not False
    elif hasattr(game, "move"):
        res = game.move("b1", "c3")
        success = res is not False

    assert success, "Knight on b1 should be able to jump over rank 2 pawns to c3."


def test_turn_alternation_white_then_black():
    """GIVEN White makes a valid move, THEN the turn changes to Black."""
    game = get_chess_game()
    if hasattr(game, "make_move"):
        game.make_move("e2", "e4")
    elif hasattr(game, "move"):
        game.move("e2", "e4")

    turn = getattr(game, "turn", getattr(game, "current_player", getattr(game, "active_color", "black")))
    assert str(turn).lower() in ("black", "b"), "Turn must alternate to Black after White moves."


def test_cannot_move_opponent_piece():
    """GIVEN White's turn, WHEN White attempts to move Black's e7 pawn, THEN move is rejected."""
    game = get_chess_game()
    rejected = False
    try:
        if hasattr(game, "make_move"):
            res = game.make_move("e7", "e5")
            if res is False or (isinstance(res, dict) and not res.get("success", True)):
                rejected = True
        elif hasattr(game, "move"):
            res = game.move("e7", "e5")
            if res is False:
                rejected = True
    except Exception:
        rejected = True

    assert rejected, "Player cannot move opponent's pieces on their turn."


def test_bishop_diagonal_movement_after_pawn_advance():
    """GIVEN pawn has advanced, WHEN bishop moves along cleared diagonal, THEN move succeeds."""
    game = get_chess_game()
    # 1. e2 -> e4
    if hasattr(game, "make_move"):
        game.make_move("e2", "e4")
        # 1... e7 -> e5
        game.make_move("e7", "e5")
        # 2. f1 -> c4 (bishop)
        res = game.make_move("f1", "c4")
        assert res is not False, "Bishop should be able to move along open diagonal to c4."
    elif hasattr(game, "move"):
        game.move("e2", "e4")
        game.move("e7", "e5")
        res = game.move("f1", "c4")
        assert res is not False, "Bishop should be able to move along open diagonal to c4."


def test_rook_cannot_jump_over_pawns():
    """GIVEN starting position, WHEN rook attempts to move through a2 pawn, THEN move is rejected."""
    game = get_chess_game()
    rejected = False
    try:
        if hasattr(game, "make_move"):
            res = game.make_move("a1", "a3")
            if res is False or (isinstance(res, dict) and not res.get("success", True)):
                rejected = True
        elif hasattr(game, "move"):
            res = game.move("a1", "a3")
            if res is False:
                rejected = True
    except Exception:
        rejected = True

    assert rejected, "Rook cannot jump over blocking pieces on a2."
