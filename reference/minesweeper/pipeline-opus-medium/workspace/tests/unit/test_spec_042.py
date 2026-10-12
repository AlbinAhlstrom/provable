import copy

import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10

# Mines: the cell (3,3) next to the target cell (4,4), plus the whole top row
# (0,0)..(0,8). That is 1 + 9 = 10 mines, which equals mine_count.
MINES = {(3, 3)} | {(0, c) for c in range(WIDTH)}

TARGET = (4, 4)


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _build_playing_game(target_state):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    cells = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            count = sum(1 for n in _neighbours(r, c) if n in MINES)
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": (r, c) in MINES,
                    "adjacent_mine_count": count,
                    "state": "Hidden",
                }
            )
    game.cells = cells
    # The mine next to the target is flagged: exactly 1 flagged neighbour.
    _cell(game, 3, 3)["state"] = "Flagged"
    _cell(game, *TARGET)["state"] = target_state
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 5
    game.flags_placed = 1
    game.remaining_mines = MINE_COUNT - 1
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    return game


def _cell(game, row, column):
    return game.cells[row * WIDTH + column]


def _snapshot(game):
    return {
        "cells": copy.deepcopy(game.cells),
        "status": game.status,
        "flags_placed": game.flags_placed,
        "remaining_mines": game.remaining_mines,
        "elapsed_seconds": game.elapsed_seconds,
        "started_at": game.started_at,
        "ended_at": game.ended_at,
        "struck_cell_id": game.struck_cell_id,
        "mines_laid": game.mines_laid,
        "events": list(game.events),
    }


def test_chording_a_hidden_cell_changes_nothing():
    game = _build_playing_game("Hidden")
    target = _cell(game, *TARGET)
    # Arrangement check: the target's number is 1 (only (3,3) among its
    # neighbours is a mine) and exactly 1 neighbour (3,3) is Flagged, so the
    # only thing keeping a chord from acting is that the target is Hidden.
    assert target["adjacent_mine_count"] == 1
    flagged = [n for n in _neighbours(*TARGET) if _cell(game, *n)["state"] == "Flagged"]
    assert len(flagged) == 1

    before = _snapshot(game)

    # Chording a Hidden cell is ignored: no error raised (no message shown).
    game.chord_cell(row=TARGET[0], column=TARGET[1])

    after = _snapshot(game)
    # The target is Hidden, so chord_cell does not apply: every cell keeps its
    # state (the target stays Hidden, (3,3) stays Flagged, the other
    # neighbours stay Hidden), status stays Playing, counters and timer are
    # unchanged and no event/message is produced.
    assert after == before
    assert _cell(game, *TARGET)["state"] == "Hidden"
    for n in _neighbours(*TARGET):
        expected = "Flagged" if n == (3, 3) else "Hidden"
        assert _cell(game, *n)["state"] == expected
    assert game.status == "Playing"


def test_chording_the_same_cell_when_opened_does_open_neighbours():
    # Same arrangement, only the target's state differs (Opened instead of
    # Hidden): now the chord applies.
    game = _build_playing_game("Opened")

    game.chord_cell(row=TARGET[0], column=TARGET[1])

    # Target (4,4) is Opened with number 1 and exactly 1 Flagged neighbour
    # (3,3), so every Hidden neighbour is opened. Those neighbours, (3,4),
    # (3,5), (4,3), (4,5), (5,3), (5,4), (5,5), hold no mine, so each becomes
    # Opened. The flagged mine (3,3) stays Flagged and no mine is opened, so the
    # game is not Lost.
    for n in _neighbours(*TARGET):
        if n == (3, 3):
            assert _cell(game, *n)["state"] == "Flagged"
        else:
            assert _cell(game, *n)["state"] == "Opened"
    assert game.status != "Lost"
    assert game.struck_cell_id is None
