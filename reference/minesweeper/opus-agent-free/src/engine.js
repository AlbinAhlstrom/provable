/*
 * Minesweeper rules engine. Pure logic, no DOM.
 * Works as a classic <script> (window.MinesweeperEngine) and as a CommonJS module (Node tests).
 *
 * A game is a plain object:
 *   cols, rows, mines      board configuration
 *   mine[i]   0/1          is there a mine (all 0 until the first reveal places them)
 *   adj[i]    0..8         mines among the 8 neighbours
 *   state[i]  HIDDEN | REVEALED | FLAGGED
 *   status    'ready' (no reveal yet) | 'playing' | 'won' | 'lost'
 *   placed    have the mines been placed
 *   exploded  index of the mine that ended the game, or -1
 *   revealedCount, flagCount
 * Cell index i = row * cols + col.
 *
 * reveal / toggleFlag / chord mutate the game and return the indexes whose state changed.
 */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.MinesweeperEngine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var HIDDEN = 0, REVEALED = 1, FLAGGED = 2;

  var PRESETS = {
    beginner: { cols: 9, rows: 9, mines: 10 },
    intermediate: { cols: 16, rows: 16, mines: 40 },
    expert: { cols: 30, rows: 16, mines: 99 }
  };

  var LIMITS = { minCols: 5, maxCols: 40, minRows: 5, maxRows: 30, minMines: 1 };

  /** Largest mine count that still lets the first click open a 3x3 safe area. */
  function maxMines(cols, rows) {
    return cols * rows - 9;
  }

  function clampInt(value, lo, hi, fallback) {
    var n = Math.floor(Number(value));
    if (!isFinite(n)) n = fallback;
    return Math.min(hi, Math.max(lo, n));
  }

  /** Force any input into a legal configuration. */
  function normalizeConfig(config) {
    config = config || {};
    var cols = clampInt(config.cols, LIMITS.minCols, LIMITS.maxCols, 9);
    var rows = clampInt(config.rows, LIMITS.minRows, LIMITS.maxRows, 9);
    var mines = clampInt(config.mines, LIMITS.minMines, maxMines(cols, rows), 10);
    return { cols: cols, rows: rows, mines: mines };
  }

  /** Small seeded generator, for repeatable boards. */
  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function createGame(config, rng) {
    var c = normalizeConfig(config);
    var n = c.cols * c.rows;
    return {
      cols: c.cols,
      rows: c.rows,
      mines: c.mines,
      mine: new Uint8Array(n),
      adj: new Uint8Array(n),
      state: new Uint8Array(n),
      status: 'ready',
      placed: false,
      exploded: -1,
      revealedCount: 0,
      flagCount: 0,
      rng: rng || Math.random
    };
  }

  function neighbours(game, i) {
    var cols = game.cols, rows = game.rows;
    var r = Math.floor(i / cols), c = i % cols;
    var out = [];
    for (var dr = -1; dr <= 1; dr++) {
      for (var dc = -1; dc <= 1; dc++) {
        if (dr === 0 && dc === 0) continue;
        var rr = r + dr, cc = c + dc;
        if (rr >= 0 && rr < rows && cc >= 0 && cc < cols) out.push(rr * cols + cc);
      }
    }
    return out;
  }

  function computeAdjacency(game) {
    var n = game.cols * game.rows;
    game.adj.fill(0);
    for (var i = 0; i < n; i++) {
      if (!game.mine[i]) continue;
      var nb = neighbours(game, i);
      for (var k = 0; k < nb.length; k++) game.adj[nb[k]]++;
    }
  }

  /** Place the mines anywhere except the first-clicked cell and its neighbours. */
  function placeMines(game, safeIndex) {
    var n = game.cols * game.rows;
    var blocked = new Uint8Array(n);
    blocked[safeIndex] = 1;
    var nb = neighbours(game, safeIndex);
    for (var k = 0; k < nb.length; k++) blocked[nb[k]] = 1;

    var candidates = [];
    for (var i = 0; i < n; i++) if (!blocked[i]) candidates.push(i);

    // Partial Fisher-Yates: the first `mines` entries become a uniform random sample.
    for (var m = 0; m < game.mines; m++) {
      var j = m + Math.floor(game.rng() * (candidates.length - m));
      var tmp = candidates[m];
      candidates[m] = candidates[j];
      candidates[j] = tmp;
      game.mine[candidates[m]] = 1;
    }
    computeAdjacency(game);
    game.placed = true;
  }

  /** Open a safe hidden cell and flood through zeros. */
  function openFrom(game, start, changed) {
    var stack = [start];
    while (stack.length) {
      var i = stack.pop();
      if (game.state[i] !== HIDDEN || game.mine[i]) continue;
      game.state[i] = REVEALED;
      game.revealedCount++;
      changed.push(i);
      if (game.adj[i] === 0) {
        var nb = neighbours(game, i);
        for (var k = 0; k < nb.length; k++) {
          if (game.state[nb[k]] === HIDDEN) stack.push(nb[k]);
        }
      }
    }
  }

  function checkWin(game, changed) {
    var n = game.cols * game.rows;
    if (game.status !== 'playing' || game.revealedCount !== n - game.mines) return;
    game.status = 'won';
    for (var i = 0; i < n; i++) {
      if (game.mine[i] && game.state[i] !== FLAGGED) {
        game.state[i] = FLAGGED;
        game.flagCount++;
        changed.push(i);
      }
    }
  }

  function isOver(game) {
    return game.status === 'won' || game.status === 'lost';
  }

  function inBoard(game, i) {
    return Number.isInteger(i) && i >= 0 && i < game.cols * game.rows;
  }

  function reveal(game, i) {
    if (isOver(game) || !inBoard(game, i) || game.state[i] !== HIDDEN) return [];
    if (!game.placed) placeMines(game, i);
    game.status = 'playing';
    if (game.mine[i]) {
      game.status = 'lost';
      game.exploded = i;
      return [i];
    }
    var changed = [];
    openFrom(game, i, changed);
    checkWin(game, changed);
    return changed;
  }

  function toggleFlag(game, i) {
    if (isOver(game) || !inBoard(game, i)) return [];
    if (game.state[i] === HIDDEN) {
      game.state[i] = FLAGGED;
      game.flagCount++;
      return [i];
    }
    if (game.state[i] === FLAGGED) {
      game.state[i] = HIDDEN;
      game.flagCount--;
      return [i];
    }
    return [];
  }

  /** On a revealed number with exactly that many flags around it, open the rest. */
  function chord(game, i) {
    if (game.status !== 'playing' || !inBoard(game, i)) return [];
    if (game.state[i] !== REVEALED || game.adj[i] === 0) return [];
    var nb = neighbours(game, i);
    var flags = 0, k;
    for (k = 0; k < nb.length; k++) if (game.state[nb[k]] === FLAGGED) flags++;
    if (flags !== game.adj[i]) return [];

    var changed = [];
    var hit = -1;
    for (k = 0; k < nb.length; k++) {
      var j = nb[k];
      if (game.state[j] !== HIDDEN) continue;
      if (game.mine[j]) {
        if (hit < 0) hit = j;
      } else {
        openFrom(game, j, changed);
      }
    }
    if (hit >= 0) {
      game.status = 'lost';
      game.exploded = hit;
      changed.push(hit);
      return changed;
    }
    checkWin(game, changed);
    return changed;
  }

  function serialize(game) {
    return {
      v: 1,
      cols: game.cols,
      rows: game.rows,
      mines: game.mines,
      status: game.status,
      placed: game.placed,
      exploded: game.exploded,
      mine: Array.prototype.join.call(game.mine, ''),
      state: Array.prototype.join.call(game.state, '')
    };
  }

  /** Rebuild a game from serialize() output. Returns null when the data is not a consistent game. */
  function deserialize(data, rng) {
    if (!data || data.v !== 1) return null;
    var c = normalizeConfig(data);
    if (c.cols !== data.cols || c.rows !== data.rows || c.mines !== data.mines) return null;
    var n = c.cols * c.rows;
    if (typeof data.mine !== 'string' || typeof data.state !== 'string') return null;
    if (data.mine.length !== n || data.state.length !== n) return null;
    if (!/^[01]*$/.test(data.mine) || !/^[012]*$/.test(data.state)) return null;
    if (['ready', 'playing', 'won', 'lost'].indexOf(data.status) < 0) return null;

    var game = createGame(c, rng);
    var mineTotal = 0;
    for (var i = 0; i < n; i++) {
      game.mine[i] = data.mine.charCodeAt(i) - 48;
      game.state[i] = data.state.charCodeAt(i) - 48;
      mineTotal += game.mine[i];
      if (game.state[i] === REVEALED) game.revealedCount++;
      if (game.state[i] === FLAGGED) game.flagCount++;
    }
    game.placed = !!data.placed;
    if (game.placed ? mineTotal !== c.mines : mineTotal !== 0) return null;
    if (!game.placed && (data.status !== 'ready' || game.revealedCount !== 0)) return null;
    game.status = data.status;
    game.exploded = inBoard(game, data.exploded) ? data.exploded : -1;
    computeAdjacency(game);
    return game;
  }

  return {
    HIDDEN: HIDDEN,
    REVEALED: REVEALED,
    FLAGGED: FLAGGED,
    PRESETS: PRESETS,
    LIMITS: LIMITS,
    maxMines: maxMines,
    normalizeConfig: normalizeConfig,
    mulberry32: mulberry32,
    createGame: createGame,
    neighbours: neighbours,
    reveal: reveal,
    toggleFlag: toggleFlag,
    chord: chord,
    isOver: isOver,
    serialize: serialize,
    deserialize: deserialize
  };
});
