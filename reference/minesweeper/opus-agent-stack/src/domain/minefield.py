"""Board geometry and mine placement. Pure: the only randomness is the seed handed in."""
from __future__ import annotations

import random

Cell = tuple[int, int]


def neighbours(rows: int, cols: int, cell: Cell) -> list[Cell]:
    """The up-to-eight cells around `cell` that are on the board, in reading order."""
    row, col = cell
    return [
        (r, c)
        for r in range(row - 1, row + 2)
        for c in range(col - 1, col + 2)
        if (r, c) != (row, col) and 0 <= r < rows and 0 <= c < cols
    ]


def place_mines(rows: int, cols: int, count: int, safe_cell: Cell, seed: int) -> frozenset[Cell]:
    """Choose `count` mine cells, none on `safe_cell` or its neighbours.

    Deterministic: the same arguments always give the same layout.
    """
    keep_clear = {safe_cell, *neighbours(rows, cols, safe_cell)}
    candidates = [
        (r, c) for r in range(rows) for c in range(cols) if (r, c) not in keep_clear
    ]
    if count > len(candidates):
        raise ValueError(f"{count} mines do not fit beside a clear first area")
    return frozenset(random.Random(seed).sample(candidates, count))
