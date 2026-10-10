/*
 * Minesweeper UI. All rules live in engine.js; this file draws the board, turns
 * mouse / touch / keyboard input into engine calls, and keeps time, stats and saves.
 */
(function () {
  'use strict';

  var E = window.MinesweeperEngine;
  var STORAGE_KEY = 'minesweeper.v1';
  var LONG_PRESS_MS = 400;
  var CELL_MIN = 24, CELL_MAX = 40, GAP = 2;
  var FACES = { idle: '🙂', press: '😮', won: '😎', lost: '😵' };
  var ICON = {
    flag: '<svg class="ico" aria-hidden="true"><use href="#i-flag"/></svg>',
    mine: '<svg class="ico" aria-hidden="true"><use href="#i-mine"/></svg>'
  };

  var $ = function (id) { return document.getElementById(id); };
  var el = {
    app: document.querySelector('.app'),
    board: $('board'),
    wrap: $('board-wrap'),
    minesLeft: $('mines-left'),
    timer: $('timer'),
    face: $('face'),
    faceGlyph: $('face-glyph'),
    status: $('status'),
    modeDig: $('mode-dig'),
    modeFlag: $('mode-flag'),
    theme: $('theme'),
    levels: document.querySelector('.levels'),
    statBoard: $('stat-board'),
    statBest: $('stat-best'),
    statWon: $('stat-won'),
    dialog: $('custom-dialog'),
    form: $('custom-form'),
    cCols: $('c-cols'),
    cRows: $('c-rows'),
    cMines: $('c-mines'),
    cHint: $('c-hint'),
    cCancel: $('c-cancel')
  };

  // ---------- persistence ----------

  function loadStore() {
    try {
      var parsed = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (parsed && typeof parsed === 'object') return parsed;
    } catch (err) { /* private mode or corrupt data: start clean */ }
    return {};
  }

  var store = loadStore();
  if (!store.stats || typeof store.stats !== 'object') store.stats = {};

  function writeStore() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
    } catch (err) { /* storage unavailable: the game still works, it just forgets */ }
  }

  // ---------- state ----------

  var seedParam = new URLSearchParams(location.search).get('seed');
  var seed = seedParam !== null && /^\d+$/.test(seedParam) ? Number(seedParam) : null;

  var game = null;
  var level = 'beginner';
  var cells = [];
  var focusIndex = 0;
  var flagMode = false;

  var elapsedBase = 0;      // ms accumulated while the clock was not running
  var runningSince = null;  // performance.now() when the clock last started, or null
  var tickHandle = null;
  var lastOutcome = null;   // { ms, isBest } of the game that just ended

  var lastPointerType = 'mouse';
  var longPressTimer = null;
  var pressOrigin = null;
  var suppressClick = false;

  function makeRng() {
    return seed === null ? Math.random : E.mulberry32(seed);
  }

  function configKey(g) {
    return g.cols + 'x' + g.rows + 'x' + g.mines;
  }

  // ---------- clock ----------

  function elapsedMs() {
    return elapsedBase + (runningSince === null ? 0 : performance.now() - runningSince);
  }

  function startClock() {
    if (runningSince !== null) return;
    runningSince = performance.now();
    tickHandle = setInterval(renderTimer, 200);
  }

  function stopClock() {
    if (runningSince === null) return;
    elapsedBase = elapsedMs();
    runningSince = null;
    clearInterval(tickHandle);
    tickHandle = null;
  }

  function pad3(n) {
    var s = String(Math.abs(n));
    while (s.length < (n < 0 ? 2 : 3)) s = '0' + s;
    return (n < 0 ? '-' : '') + s;
  }

  function renderTimer() {
    var text = pad3(Math.min(999, Math.floor(elapsedMs() / 1000)));
    if (el.timer.textContent !== text) el.timer.textContent = text;
  }

  function formatTime(ms) {
    return (Math.floor(ms / 100) / 10).toFixed(1) + ' s';
  }

  // ---------- drawing ----------

  function fitBoard() {
    var availW = el.app.clientWidth - 30; // panel padding (24) and border (2), board padding (4)
    var availH = window.innerHeight - 300; // room for the header, HUD and footer
    var byW = Math.floor((availW - (game.cols - 1) * GAP) / game.cols);
    var byH = Math.floor((availH - (game.rows - 1) * GAP) / game.rows);
    var size = Math.max(CELL_MIN, Math.min(CELL_MAX, byW, byH));
    el.board.style.setProperty('--cell', size + 'px');
    el.board.style.gridTemplateColumns = 'repeat(' + game.cols + ', var(--cell))';
  }

  function buildBoard() {
    el.board.textContent = '';
    cells = [];
    var frag = document.createDocumentFragment();
    for (var r = 0; r < game.rows; r++) {
      var row = document.createElement('div');
      row.className = 'row';
      row.setAttribute('role', 'row');
      for (var c = 0; c < game.cols; c++) {
        var b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('role', 'gridcell');
        b.dataset.i = String(r * game.cols + c);
        b.tabIndex = -1;
        row.appendChild(b);
        cells.push(b);
      }
      frag.appendChild(row);
    }
    el.board.appendChild(frag);
    focusIndex = 0;
    cells[0].tabIndex = 0;
    fitBoard();
  }

  function renderCell(i) {
    var b = cells[i];
    var st = game.state[i];
    var lost = game.status === 'lost';
    var cls = 'cell';
    var html = '';
    var what;

    if (st === E.REVEALED) {
      var n = game.adj[i];
      cls += ' open' + (n ? ' n' + n : '');
      html = n ? String(n) : '';
      what = n ? n + (n === 1 ? ' mine nearby' : ' mines nearby') : 'empty';
    } else if (st === E.FLAGGED) {
      cls += ' flagged';
      html = ICON.flag;
      what = 'flagged';
      if (lost && !game.mine[i]) {
        cls += ' wrong';
        what = 'wrong flag, no mine here';
      }
    } else if (lost && game.mine[i]) {
      cls += ' open mine' + (i === game.exploded ? ' exploded' : '');
      html = ICON.mine;
      what = i === game.exploded ? 'the mine you hit' : 'mine';
    } else {
      what = 'hidden';
    }

    if (b.className !== cls) b.className = cls;
    if (b.innerHTML !== html) b.innerHTML = html;
    b.setAttribute('aria-label',
      'Row ' + (Math.floor(i / game.cols) + 1) + ', column ' + (i % game.cols + 1) + ': ' + what);
  }

  function renderAll() {
    for (var i = 0; i < cells.length; i++) renderCell(i);
  }

  function setFace(name) {
    el.faceGlyph.textContent = FACES[name];
  }

  function restFace() {
    setFace(game.status === 'won' ? 'won' : game.status === 'lost' ? 'lost' : 'idle');
  }

  function renderStatus() {
    var text = '';
    if (game.status === 'ready') {
      text = 'Dig anywhere. Your first dig is always safe.';
    } else if (game.status === 'playing') {
      var left = game.cols * game.rows - game.mines - game.revealedCount;
      text = left + (left === 1 ? ' safe square to go' : ' safe squares to go');
    } else if (game.status === 'won') {
      text = 'Cleared in ' + formatTime(lastOutcome ? lastOutcome.ms : elapsedMs()) + '.' +
        (lastOutcome && lastOutcome.isBest ? ' New best time!' : ' Well played.');
    } else if (game.status === 'lost') {
      text = 'Boom! You hit a mine.';
    }
    el.status.textContent = text;
    el.status.dataset.state = game.status;
  }

  function renderHud() {
    el.minesLeft.textContent = pad3(game.mines - game.flagCount);
    renderTimer();
    restFace();
    renderStatus();
    el.board.dataset.status = game.status;
  }

  function renderStats() {
    var s = store.stats[configKey(game)] || { played: 0, won: 0, best: null };
    el.statBoard.textContent = game.cols + ' × ' + game.rows + ', ' + game.mines + ' mines';
    el.statBest.textContent = s.best === null || s.best === undefined ? '–' : formatTime(s.best);
    el.statWon.textContent = s.won + ' of ' + s.played +
      (s.played ? ' (' + Math.round(100 * s.won / s.played) + '%)' : '');
  }

  function renderLevels() {
    var buttons = el.levels.querySelectorAll('button');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute('aria-pressed', String(buttons[i].dataset.level === level));
    }
  }

  function renderMode() {
    el.modeDig.setAttribute('aria-pressed', String(!flagMode));
    el.modeFlag.setAttribute('aria-pressed', String(flagMode));
    el.board.dataset.mode = flagMode ? 'flag' : 'dig';
  }

  // ---------- game flow ----------

  function saveProgress() {
    store.level = level;
    store.save = game.status === 'playing'
      ? { game: E.serialize(game), elapsed: Math.round(elapsedMs()) }
      : null;
    writeStore();
  }

  function newGame(config, levelName) {
    var sameSize = game && cells.length && game.cols === config.cols && game.rows === config.rows;
    stopClock();
    elapsedBase = 0;
    lastOutcome = null;
    level = levelName;
    game = E.createGame(config, makeRng());
    if (levelName === 'custom') store.custom = { cols: game.cols, rows: game.rows, mines: game.mines };
    if (!sameSize) buildBoard();
    renderAll();
    renderHud();
    renderStats();
    renderLevels();
    saveProgress();
  }

  function restart() {
    newGame({ cols: game.cols, rows: game.rows, mines: game.mines }, level);
  }

  function finish() {
    var ms = Math.round(elapsedMs());
    var key = configKey(game);
    var s = store.stats[key] || { played: 0, won: 0, best: null };
    s.played++;
    var isBest = false;
    if (game.status === 'won') {
      s.won++;
      isBest = s.best === null || s.best === undefined || ms < s.best;
      if (isBest) s.best = ms;
    }
    store.stats[key] = s;
    lastOutcome = { ms: ms, isBest: isBest };
    renderStats();
  }

  /** kind: 'dig' (reveal, or chord on a number), 'flag', 'chord'. */
  function act(i, kind) {
    if (E.isOver(game)) return;
    var before = game.status;
    var changed;
    if (kind === 'flag') changed = E.toggleFlag(game, i);
    else if (kind === 'chord' || game.state[i] === E.REVEALED) changed = E.chord(game, i);
    else changed = E.reveal(game, i);
    if (!changed.length) return;

    if (before === 'ready' && game.status !== 'ready') startClock();
    if (E.isOver(game)) {
      stopClock();
      finish();
      renderAll();
    } else {
      changed.forEach(renderCell);
    }
    renderHud();
    saveProgress();
  }

  /** What a plain tap / click / Enter does, given the Dig / Flag switch. */
  function primary(i) {
    act(i, flagMode && game.state[i] !== E.REVEALED ? 'flag' : 'dig');
  }

  /** What right-click / long-press does: the other thing. */
  function secondary(i) {
    act(i, flagMode ? 'dig' : 'flag');
  }

  function cellIndex(target) {
    var b = target && target.closest ? target.closest('.cell') : null;
    return b && el.board.contains(b) ? Number(b.dataset.i) : -1;
  }

  // ---------- input: pointer ----------

  function cancelLongPress() {
    clearTimeout(longPressTimer);
    longPressTimer = null;
    pressOrigin = null;
  }

  el.board.addEventListener('pointerdown', function (e) {
    lastPointerType = e.pointerType || 'mouse';
    suppressClick = false;
    cancelLongPress();
    var i = cellIndex(e.target);
    if (i < 0 || E.isOver(game)) return;

    if (lastPointerType === 'mouse') {
      if (e.button === 0 && game.state[i] !== E.FLAGGED) setFace('press');
      return;
    }
    // Touch and pen: holding still does the secondary action.
    pressOrigin = { x: e.clientX, y: e.clientY };
    longPressTimer = setTimeout(function () {
      longPressTimer = null;
      suppressClick = true;
      secondary(i);
      if (navigator.vibrate) navigator.vibrate(25);
    }, LONG_PRESS_MS);
  });

  el.board.addEventListener('pointermove', function (e) {
    if (!pressOrigin) return;
    if (Math.abs(e.clientX - pressOrigin.x) > 10 || Math.abs(e.clientY - pressOrigin.y) > 10) cancelLongPress();
  });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (type) {
    el.board.addEventListener(type, cancelLongPress);
  });
  window.addEventListener('pointerup', function () { if (game) restFace(); });
  window.addEventListener('pointercancel', function () { if (game) restFace(); });

  el.board.addEventListener('click', function (e) {
    var i = cellIndex(e.target);
    if (i < 0) return;
    if (suppressClick) { suppressClick = false; return; }
    primary(i);
  });

  el.board.addEventListener('contextmenu', function (e) {
    e.preventDefault(); // never show the browser menu over the minefield
    var i = cellIndex(e.target);
    if (i < 0) return;
    if (lastPointerType === 'touch' || lastPointerType === 'pen') return; // long-press already handled it
    secondary(i);
  });

  // Middle button chords. mousedown is cancelled so the browser does not start auto-scroll.
  el.board.addEventListener('mousedown', function (e) {
    if (e.button === 1) e.preventDefault();
  });
  el.board.addEventListener('auxclick', function (e) {
    if (e.button !== 1) return;
    var i = cellIndex(e.target);
    if (i >= 0) act(i, 'chord');
  });

  // ---------- input: keyboard ----------

  function moveFocus(to) {
    if (to < 0 || to >= cells.length) return;
    cells[focusIndex].tabIndex = -1;
    focusIndex = to;
    cells[to].tabIndex = 0;
    cells[to].focus();
  }

  el.board.addEventListener('focusin', function (e) {
    var i = cellIndex(e.target);
    if (i < 0 || i === focusIndex) return;
    cells[focusIndex].tabIndex = -1;
    focusIndex = i;
    cells[i].tabIndex = 0;
  });

  el.board.addEventListener('keydown', function (e) {
    var i = cellIndex(e.target);
    if (i < 0 || e.ctrlKey || e.metaKey || e.altKey) return;
    lastPointerType = 'keyboard';
    var r = Math.floor(i / game.cols), c = i % game.cols;
    var to = -1;
    switch (e.key) {
      case 'ArrowLeft': if (c > 0) to = i - 1; break;
      case 'ArrowRight': if (c < game.cols - 1) to = i + 1; break;
      case 'ArrowUp': if (r > 0) to = i - game.cols; break;
      case 'ArrowDown': if (r < game.rows - 1) to = i + game.cols; break;
      case 'Home': to = r * game.cols; break;
      case 'End': to = r * game.cols + game.cols - 1; break;
      case 'f': case 'F': act(i, 'flag'); e.preventDefault(); return;
      default: return;
    }
    e.preventDefault();
    if (to >= 0) moveFocus(to);
  });

  document.addEventListener('keydown', function (e) {
    if (el.dialog.open || e.ctrlKey || e.metaKey || e.altKey) return;
    var tag = e.target && e.target.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    if (e.key === 'r' || e.key === 'R' || e.key === 'F2') {
      e.preventDefault();
      restart();
    }
  });

  // ---------- controls ----------

  el.face.addEventListener('click', restart);

  el.modeDig.addEventListener('click', function () { flagMode = false; renderMode(); });
  el.modeFlag.addEventListener('click', function () { flagMode = true; renderMode(); });

  el.levels.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-level]');
    if (!b) return;
    if (b.dataset.level === 'custom') openCustomDialog();
    else newGame(E.PRESETS[b.dataset.level], b.dataset.level);
  });

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
  }

  function currentTheme() {
    if (store.theme === 'light' || store.theme === 'dark') return store.theme;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  el.theme.addEventListener('click', function () {
    store.theme = currentTheme() === 'dark' ? 'light' : 'dark';
    applyTheme(store.theme);
    writeStore();
  });

  // ---------- custom board dialog ----------

  function mineLimitText() {
    var cols = Number(el.cCols.value), rows = Number(el.cRows.value);
    var L = E.LIMITS;
    if (cols >= L.minCols && cols <= L.maxCols && rows >= L.minRows && rows <= L.maxRows) {
      return 'Mines: 1 to ' + E.maxMines(cols, rows) + ' on this size.';
    }
    return 'Columns 5 to 40, rows 5 to 30.';
  }

  function openCustomDialog() {
    var c = store.custom || { cols: game.cols, rows: game.rows, mines: game.mines };
    el.cCols.value = c.cols;
    el.cRows.value = c.rows;
    el.cMines.value = c.mines;
    el.cHint.textContent = mineLimitText();
    el.cHint.classList.remove('error');
    el.dialog.showModal();
    el.cCols.select();
  }

  [el.cCols, el.cRows, el.cMines].forEach(function (input) {
    input.addEventListener('input', function () {
      el.cHint.textContent = mineLimitText();
      el.cHint.classList.remove('error');
    });
  });

  function customError(input, message) {
    el.cHint.textContent = message;
    el.cHint.classList.add('error');
    input.focus();
    input.select();
  }

  function wholeNumber(input) {
    var text = input.value.trim();
    return /^\d+$/.test(text) ? Number(text) : NaN;
  }

  el.form.addEventListener('submit', function (e) {
    e.preventDefault();
    var L = E.LIMITS;
    var cols = wholeNumber(el.cCols), rows = wholeNumber(el.cRows), mines = wholeNumber(el.cMines);
    if (!(cols >= L.minCols && cols <= L.maxCols)) {
      return customError(el.cCols, 'Columns must be a whole number from ' + L.minCols + ' to ' + L.maxCols + '.');
    }
    if (!(rows >= L.minRows && rows <= L.maxRows)) {
      return customError(el.cRows, 'Rows must be a whole number from ' + L.minRows + ' to ' + L.maxRows + '.');
    }
    var top = E.maxMines(cols, rows);
    if (!(mines >= L.minMines && mines <= top)) {
      return customError(el.cMines, 'Mines must be a whole number from 1 to ' + top + ' on this size.');
    }
    el.dialog.close();
    newGame({ cols: cols, rows: rows, mines: mines }, 'custom');
  });

  el.cCancel.addEventListener('click', function () { el.dialog.close(); });

  // ---------- window ----------

  window.addEventListener('resize', function () { if (game) fitBoard(); });

  // The clock only runs while the page is visible, and progress is saved on the way out.
  document.addEventListener('visibilitychange', function () {
    if (!game || game.status !== 'playing') return;
    if (document.hidden) {
      stopClock();
      saveProgress();
    } else {
      startClock();
    }
  });
  window.addEventListener('pagehide', function () { if (game) saveProgress(); });

  // Another tab of the game wrote stats or a theme: pick them up instead of overwriting them later.
  window.addEventListener('storage', function (e) {
    if (e.key !== STORAGE_KEY || !game) return;
    var fresh = loadStore();
    store.stats = fresh.stats && typeof fresh.stats === 'object' ? fresh.stats : {};
    store.theme = fresh.theme;
    applyTheme(currentTheme());
    renderStats();
  });

  // ---------- start ----------

  function boot() {
    applyTheme(currentTheme());
    renderMode();

    var saved = store.save;
    var restored = saved && typeof saved === 'object' ? E.deserialize(saved.game, makeRng()) : null;
    if (restored && restored.status === 'playing') {
      level = ['beginner', 'intermediate', 'expert', 'custom'].indexOf(store.level) >= 0 ? store.level : 'custom';
      game = restored;
      elapsedBase = Math.max(0, Number(saved.elapsed) || 0);
      buildBoard();
      renderAll();
      renderHud();
      renderStats();
      renderLevels();
      if (!document.hidden) startClock();
      return;
    }

    var startLevel = E.PRESETS[store.level] ? store.level : (store.level === 'custom' && store.custom ? 'custom' : 'beginner');
    newGame(startLevel === 'custom' ? store.custom : E.PRESETS[startLevel], startLevel);
  }

  boot();

  // Read-only handle for the browser test and for the curious.
  window.__minesweeper = {
    get game() { return game; },
    get elapsedMs() { return elapsedMs(); }
  };
})();
