// Run with: node --test tests/
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const E = require('../src/engine.js');

const sum = (arr) => Array.prototype.reduce.call(arr, (a, b) => a + b, 0);

/** Build a game with mines exactly where the picture has '*'. */
function fromPicture(lines) {
  const rows = lines.length, cols = lines[0].length;
  const mines = lines.join('').split('*').length - 1;
  const game = E.createGame({ cols, rows, mines });
  // Go through the public (de)serialiser so adjacency is computed by the engine itself.
  const data = E.serialize(game);
  data.mine = lines.join('').replace(/[^*]/g, '0').replace(/\*/g, '1');
  data.placed = true;
  data.status = 'playing';
  const built = E.deserialize(data);
  assert.ok(built, 'picture must be a legal board');
  return built;
}

const at = (game, r, c) => r * game.cols + c;

test('R1 presets are the classic levels', () => {
  assert.deepEqual(E.PRESETS.beginner, { cols: 9, rows: 9, mines: 10 });
  assert.deepEqual(E.PRESETS.intermediate, { cols: 16, rows: 16, mines: 40 });
  assert.deepEqual(E.PRESETS.expert, { cols: 30, rows: 16, mines: 99 });
});

test('R1 custom configuration is clamped to legal values', () => {
  assert.deepEqual(E.normalizeConfig({ cols: 1, rows: 999, mines: 0 }), { cols: 5, rows: 30, mines: 1 });
  assert.deepEqual(E.normalizeConfig({ cols: 5, rows: 5, mines: 500 }), { cols: 5, rows: 5, mines: 16 });
  assert.deepEqual(E.normalizeConfig({ cols: 'x', rows: null, mines: undefined }), { cols: 9, rows: 5, mines: 10 });
});

test('R2 no mines exist before the first reveal', () => {
  const game = E.createGame(E.PRESETS.expert, E.mulberry32(1));
  assert.equal(game.status, 'ready');
  assert.equal(sum(game.mine), 0);
});

test('R2/R3 first reveal is safe, opens an area, and places exactly the mine count', () => {
  for (const [name, preset] of Object.entries(E.PRESETS)) {
    for (let seed = 1; seed <= 200; seed++) {
      const game = E.createGame(preset, E.mulberry32(seed));
      const first = Math.floor(E.mulberry32(seed + 9999)() * preset.cols * preset.rows);
      const changed = E.reveal(game, first);
      assert.equal(sum(game.mine), preset.mines, `${name} seed ${seed}: mine count`);
      assert.equal(game.mine[first], 0);
      assert.equal(game.adj[first], 0, `${name} seed ${seed}: first cell must be a zero`);
      for (const nb of E.neighbours(game, first)) assert.equal(game.mine[nb], 0);
      assert.ok(changed.length >= 4, 'an area opened');
      assert.notEqual(game.status, 'lost');
    }
  }
});

test('R2 holds on the densest legal board, where the opening is an instant win', () => {
  const game = E.createGame({ cols: 5, rows: 5, mines: 16 }, E.mulberry32(3));
  E.reveal(game, at(game, 2, 2));
  assert.equal(sum(game.mine), 16);
  assert.equal(game.status, 'won');
});

test('R3 mine placement covers the board (no cell is systematically skipped)', () => {
  const seen = new Uint8Array(81);
  for (let seed = 1; seed <= 300; seed++) {
    const game = E.createGame(E.PRESETS.beginner, E.mulberry32(seed));
    E.reveal(game, 0);
    game.mine.forEach((m, i) => { if (m) seen[i] = 1; });
  }
  // Cells 0, 1, 9, 10 are the protected opening; every other cell should have held a mine at least once.
  assert.equal(sum(seen), 81 - 4);
});

test('R4 numbers count the mines in the 8 neighbours', () => {
  const game = fromPicture([
    '*....',
    '.....',
    '..*..',
    '.....',
    '.....'
  ]);
  assert.deepEqual(Array.from(game.adj), [
    0, 1, 0, 0, 0,
    1, 2, 1, 1, 0,
    0, 1, 0, 1, 0,
    0, 1, 1, 1, 0,
    0, 0, 0, 0, 0
  ]);
  const ring = fromPicture([
    '.....',
    '.***.',
    '.*.*.',
    '.***.',
    '.....'
  ]);
  assert.equal(ring.adj[12], 8);
});

test('R5 revealing a zero floods to the numbered border and stops there', () => {
  const game = fromPicture([
    '.....',
    '.....',
    '.....',
    '...*.',
    '.....'
  ]);
  const changed = E.reveal(game, at(game, 0, 0));
  // Everything opens except the mine and (3,4), (4,3), (4,4): numbers that touch no zero cell.
  const hidden = [];
  game.state.forEach((s, i) => { if (s === E.HIDDEN) hidden.push(i); });
  assert.deepEqual(hidden, [at(game, 3, 3), at(game, 3, 4), at(game, 4, 3), at(game, 4, 4)]);
  assert.equal(changed.length, 21);
  assert.equal(new Set(changed).size, changed.length, 'no cell reported twice');
  assert.equal(game.revealedCount, 21);
  assert.equal(game.status, 'playing');
});

test('R5 the flood does not open flagged cells', () => {
  const game = fromPicture([
    '.....',
    '.....',
    '.....',
    '.....',
    '....*'
  ]);
  E.toggleFlag(game, at(game, 0, 1));
  E.reveal(game, at(game, 0, 0));
  assert.equal(game.state[at(game, 0, 1)], E.FLAGGED);
  assert.equal(game.status, 'playing', 'a flagged safe cell is still unrevealed, so no win yet');
});

test('R6 flags toggle, block reveal, and cannot be put on revealed cells', () => {
  const game = fromPicture([
    '*....',
    '.....',
    '.....',
    '.....',
    '.....'
  ]);
  assert.deepEqual(E.toggleFlag(game, 0), [0]);
  assert.equal(game.flagCount, 1);
  assert.deepEqual(E.reveal(game, 0), [], 'flagged cell does not reveal');
  assert.equal(game.status, 'playing');
  assert.deepEqual(E.toggleFlag(game, 0), [0]);
  assert.equal(game.flagCount, 0);
  E.reveal(game, 1);
  assert.deepEqual(E.toggleFlag(game, 1), [], 'cannot flag a revealed cell');
  assert.equal(game.flagCount, 0);
});

test('R6 flags may be placed before the first reveal', () => {
  const game = E.createGame(E.PRESETS.beginner, E.mulberry32(5));
  E.toggleFlag(game, 80);
  assert.equal(game.status, 'ready');
  E.reveal(game, 0);
  assert.equal(game.state[80], E.FLAGGED);
  assert.equal(game.flagCount, 1);
});

test('R7 chord opens the remaining neighbours when flags match the number', () => {
  const game = fromPicture([
    '*....',
    '.....',
    '.....',
    '.....',
    '....*'
  ]);
  const one = at(game, 1, 1);
  E.reveal(game, one);
  assert.equal(game.adj[one], 1);
  assert.deepEqual(E.chord(game, one), [], 'no flags yet: nothing happens');
  E.toggleFlag(game, 0);
  const changed = E.chord(game, one);
  assert.ok(changed.length > 0);
  for (const nb of E.neighbours(game, one)) {
    assert.notEqual(game.state[nb], E.HIDDEN);
  }
  assert.notEqual(game.status, 'lost');
});

test('R7 chord with a wrong flag explodes the real mine', () => {
  const game = fromPicture([
    '*....',
    '.....',
    '.....',
    '.....',
    '....*'
  ]);
  const one = at(game, 1, 1);
  E.reveal(game, one);
  E.toggleFlag(game, at(game, 0, 1)); // wrong: the mine is at (0,0)
  E.chord(game, one);
  assert.equal(game.status, 'lost');
  assert.equal(game.exploded, 0);
});

test('R7 chord does nothing on hidden cells, zeros, or with too many flags', () => {
  const game = fromPicture([
    '*....',
    '.....',
    '.....',
    '.....',
    '....*'
  ]);
  assert.deepEqual(E.chord(game, 0), []);
  const one = at(game, 1, 1);
  E.reveal(game, one);
  E.toggleFlag(game, 0);
  E.toggleFlag(game, 1);
  assert.deepEqual(E.chord(game, one), []);
  assert.equal(game.status, 'playing');
});

test('R8 revealing a mine loses and locks the board', () => {
  const game = fromPicture([
    '*....',
    '.....',
    '.....',
    '.....',
    '.....'
  ]);
  assert.deepEqual(E.reveal(game, 0), [0]);
  assert.equal(game.status, 'lost');
  assert.equal(game.exploded, 0);
  assert.deepEqual(E.reveal(game, 8), []);
  assert.deepEqual(E.toggleFlag(game, 8), []);
  assert.deepEqual(E.chord(game, 8), []);
});

test('R9 win when all safe cells are open, without any flags; mines get auto-flagged', () => {
  const game = fromPicture([
    '*....',
    '.....',
    '.....',
    '.....',
    '.....'
  ]);
  E.reveal(game, 24); // floods everything except (0,0)
  assert.equal(game.status, 'won');
  assert.equal(game.state[0], E.FLAGGED);
  assert.equal(game.flagCount, 1);
  assert.deepEqual(E.reveal(game, 0), [], 'board is locked after a win');
});

test('R9 a win is not declared while a safe cell is still hidden', () => {
  const game = fromPicture([
    '*.*..',
    '.....',
    '.....',
    '.....',
    '.....'
  ]);
  E.reveal(game, at(game, 4, 0));
  assert.equal(game.status, 'playing'); // (0,1) is safe but walled in by numbers
  E.reveal(game, at(game, 0, 1));
  assert.equal(game.status, 'won');
});

test('out-of-range indexes are ignored', () => {
  const game = E.createGame(E.PRESETS.beginner, E.mulberry32(1));
  for (const bad of [-1, 81, 1.5, NaN, undefined]) {
    assert.deepEqual(E.reveal(game, bad), []);
    assert.deepEqual(E.toggleFlag(game, bad), []);
    assert.deepEqual(E.chord(game, bad), []);
  }
  assert.equal(game.status, 'ready');
});

test('R15 a game survives serialize -> JSON -> deserialize unchanged', () => {
  const game = E.createGame(E.PRESETS.intermediate, E.mulberry32(42));
  E.reveal(game, 100);
  const flagTarget = game.mine.indexOf(1);
  E.toggleFlag(game, flagTarget);
  const copy = E.deserialize(JSON.parse(JSON.stringify(E.serialize(game))));
  for (const key of ['cols', 'rows', 'mines', 'status', 'placed', 'exploded', 'revealedCount', 'flagCount']) {
    assert.equal(copy[key], game[key], key);
  }
  assert.deepEqual(Array.from(copy.mine), Array.from(game.mine));
  assert.deepEqual(Array.from(copy.adj), Array.from(game.adj));
  assert.deepEqual(Array.from(copy.state), Array.from(game.state));
});

test('R15 corrupt saves are rejected instead of producing a broken board', () => {
  const good = E.serialize(E.createGame(E.PRESETS.beginner));
  assert.ok(E.deserialize(good));
  assert.equal(E.deserialize(null), null);
  assert.equal(E.deserialize({ ...good, v: 2 }), null);
  assert.equal(E.deserialize({ ...good, mine: '101' }), null);
  assert.equal(E.deserialize({ ...good, state: good.state.replace('0', '7') }), null);
  assert.equal(E.deserialize({ ...good, status: 'banana' }), null);
  assert.equal(E.deserialize({ ...good, cols: 1000 }), null);
  assert.equal(E.deserialize({ ...good, placed: true }), null, 'placed but zero mines');
});

test('whole random games played by a simple solver end consistently', () => {
  // Reveal every safe cell in order: must end in a win with consistent counters, for many boards.
  for (let seed = 1; seed <= 50; seed++) {
    const game = E.createGame(E.PRESETS.intermediate, E.mulberry32(seed));
    E.reveal(game, 120);
    for (let i = 0; i < 256; i++) if (!game.mine[i]) E.reveal(game, i);
    assert.equal(game.status, 'won');
    assert.equal(game.revealedCount, 256 - 40);
    assert.equal(game.flagCount, 40);
    let revealed = 0;
    game.state.forEach((s) => { if (s === E.REVEALED) revealed++; });
    assert.equal(revealed, game.revealedCount);
  }
});
