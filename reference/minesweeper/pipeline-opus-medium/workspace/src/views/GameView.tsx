import { useEffect, useRef, useState } from 'react';
import type { GameState } from '../api/gameClient';

type Cell = { id: string; row: number; column: number; has_mine: boolean; adjacent_mine_count: number; state: string };
type Act = (type: string, params?: Record<string, unknown>) => Promise<string | null>;
type Props = { game: GameState; onAction: Act; message?: string | null };
type Mood = 'smile' | 'o' | 'cool' | 'dead';

const NUM = ['', 'text-blue-700', 'text-green-700', 'text-red-600', 'text-[#000080]', 'text-[#800000]', 'text-teal-700', 'text-black', 'text-gray-500'];
const RAISED = 'border-2 border-t-white border-l-white border-b-gray-600 border-r-gray-600';
const SUNKEN = 'border-2 border-t-gray-600 border-l-gray-600 border-b-white border-r-white';
const SIZE = 24;

const parseTs = (s?: string | null) => {
  if (!s) return NaN;
  return Date.parse(/([zZ]|[+-]\d\d:?\d\d)$/.test(s) ? s : `${s}Z`);
};

export function elapsedSeconds(g: GameState, now: number): number {
  const start = parseTs(g.started_at);
  const end = g.status === 'Playing' ? now : parseTs(g.ended_at);
  const derived = !isNaN(start) && !isNaN(end) ? Math.floor((end - start) / 1000) : 0;
  return Math.min(999, Math.max(0, g.elapsed_seconds ?? 0, derived));
}

const fmt = (n: number) => (n < 0 ? '-' + String(Math.min(99, -n)).padStart(2, '0') : String(Math.min(999, n)).padStart(3, '0'));

const Mine = ({ crossed }: { crossed?: boolean }) => (
  <svg viewBox="0 0 16 16" className="w-[70%] h-[70%]" aria-hidden>
    <g stroke="black" strokeWidth="1.5"><line x1="8" y1="1" x2="8" y2="15" /><line x1="1" y1="8" x2="15" y2="8" /><line x1="3" y1="3" x2="13" y2="13" /><line x1="13" y1="3" x2="3" y2="13" /></g>
    <circle cx="8" cy="8" r="4.5" fill="black" /><rect x="5.5" y="5.5" width="2" height="2" fill="white" />
    {crossed && <g stroke="#dc2626" strokeWidth="1.8"><line x1="1" y1="1" x2="15" y2="15" /><line x1="15" y1="1" x2="1" y2="15" /></g>}
  </svg>
);

const Flag = () => (
  <svg viewBox="0 0 16 16" className="w-[70%] h-[70%]" aria-hidden>
    <polygon points="9,2 9,9 3,5.5" fill="#dc2626" /><line x1="9" y1="2" x2="9" y2="12" stroke="black" strokeWidth="1.5" /><rect x="4" y="12" width="9" height="2" fill="black" />
  </svg>
);

const Face = ({ mood }: { mood: Mood }) => (
  <svg viewBox="0 0 20 20" className="w-6 h-6" aria-hidden>
    <circle cx="10" cy="10" r="8.5" fill="#fde047" stroke="black" strokeWidth="1" />
    {mood === 'cool' ? <g fill="black"><rect x="4" y="6.5" width="5" height="3" /><rect x="11" y="6.5" width="5" height="3" /><rect x="8" y="7" width="4" height="1" /></g>
      : mood === 'dead' ? <g stroke="black" strokeWidth="1"><line x1="5.5" y1="6" x2="8.5" y2="9" /><line x1="8.5" y1="6" x2="5.5" y2="9" /><line x1="11.5" y1="6" x2="14.5" y2="9" /><line x1="14.5" y1="6" x2="11.5" y2="9" /></g>
      : <g fill="black"><circle cx="7" cy="7.5" r="1.2" /><circle cx="13" cy="7.5" r="1.2" /></g>}
    {mood === 'o' ? <circle cx="10" cy="13.5" r="2" fill="none" stroke="black" strokeWidth="1.2" />
      : mood === 'dead' ? <path d="M6.5 15 Q10 11.5 13.5 15" fill="none" stroke="black" strokeWidth="1.2" />
      : <path d="M6 12 Q10 16 14 12" fill="none" stroke="black" strokeWidth="1.2" />}
  </svg>
);

export function GameView({ game, onAction, message }: Props) {
  const [now, setNow] = useState(Date.now());
  const [pressed, setPressed] = useState<string | null>(null);
  const timer = useRef<number | null>(null);
  const longFired = useRef(false);
  const lastPointer = useRef('mouse');
  const status = game.status;
  const locked = status !== 'Ready' && status !== 'Playing';

  useEffect(() => {
    setNow(Date.now());
    if (status !== 'Playing') return;
    const t = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(t);
  }, [status, game.id]);
  useEffect(() => {
    const up = () => setPressed(null);
    window.addEventListener('pointerup', up);
    return () => window.removeEventListener('pointerup', up);
  }, []);

  const W = game.width ?? 9;
  const H = game.height ?? 9;
  const byId = new Map(((game.cells ?? []) as Cell[]).map((c) => [c.id, c]));
  const mood: Mood = status === 'Won' ? 'cool' : status === 'Lost' ? 'dead' : pressed ? 'o' : 'smile';
  const seconds = elapsedSeconds(game, now);
  const remaining = status === 'Won' ? 0 : game.remaining_mines ?? (game.mine_count ?? 0) - (game.flags_placed ?? 0);

  const clearTimer = () => { if (timer.current) { window.clearTimeout(timer.current); timer.current = null; } };
  const down = (e: React.PointerEvent, c: Cell) => {
    lastPointer.current = e.pointerType;
    longFired.current = false;
    if (locked || e.button !== 0) return;
    if (c.state === 'Hidden' || c.state === 'Opened') setPressed(c.id);
    if (e.pointerType !== 'mouse') {
      timer.current = window.setTimeout(() => {
        longFired.current = true;
        setPressed(null);
        void onAction('toggle_flag', { row: c.row, column: c.column });
      }, 400);
    }
  };
  const click = (c: Cell) => {
    clearTimer();
    if (longFired.current) { longFired.current = false; return; }
    if (locked) return;
    const type = c.state === 'Opened' && c.adjacent_mine_count > 0 ? 'chord_cell' : 'open_cell';
    void onAction(type, { row: c.row, column: c.column });
  };
  const context = (e: React.MouseEvent, c: Cell) => {
    e.preventDefault();
    if (locked || lastPointer.current !== 'mouse') return;
    void onAction('toggle_flag', { row: c.row, column: c.column });
  };

  const renderCell = (c: Cell) => {
    let open = false; let bg = 'bg-[#bdbdbd]'; let icon: React.ReactNode = null; let label = 'hidden';
    if (c.state === 'Detonated') { open = true; bg = 'bg-red-600'; icon = <Mine />; label = 'mine'; }
    else if (c.state === 'Flagged') {
      if (status === 'Lost' && !c.has_mine) { open = true; icon = <Mine crossed />; label = 'wrong flag'; }
      else { icon = <Flag />; label = 'flagged'; }
    } else if (c.state === 'Hidden') {
      if (status === 'Lost' && c.has_mine) { open = true; icon = <Mine />; label = 'mine'; }
      else if (pressed === c.id) open = true;
    } else {
      open = true;
      const n = c.adjacent_mine_count ?? 0;
      label = n > 0 ? String(n) : 'empty';
      if (n > 0) icon = <span className={`font-bold text-[15px] leading-none ${NUM[n] ?? 'text-black'}`}>{n}</span>;
    }
    return (
      <button key={c.id} type="button" aria-label={`Row ${c.row + 1}, column ${c.column + 1}, ${label}`}
        className={`flex items-center justify-center p-0 select-none touch-manipulation ${open ? `${bg} border border-gray-500` : `bg-[#c0c0c0] ${RAISED}`}`}
        onPointerDown={(e) => down(e, c)} onPointerLeave={() => { clearTimer(); setPressed(null); }} onPointerCancel={clearTimer}
        onClick={() => click(c)} onContextMenu={(e) => context(e, c)}>
        {icon}
      </button>
    );
  };

  const cells: Cell[] = [];
  for (let r = 0; r < H; r++) for (let col = 0; col < W; col++) {
    const id = `${r}-${col}`;
    cells.push(byId.get(id) ?? { id, row: r, column: col, has_mine: false, adjacent_mine_count: 0, state: 'Hidden' });
  }
  const counter = 'bg-black text-red-600 font-mono font-bold text-[28px] leading-none px-1 tracking-wider tabular-nums';

  return (
    <div className="flex flex-col gap-[6px] min-w-0">
      <div className={`flex items-center justify-between gap-2 px-1.5 py-1 ${SUNKEN}`}>
        <span className={counter}>{fmt(remaining)}</span>
        <button type="button" aria-label="New game" onClick={() => void onAction('restart_game')}
          className={`w-9 h-9 flex items-center justify-center bg-[#c0c0c0] ${RAISED} active:border-t-gray-600 active:border-l-gray-600 active:border-b-white active:border-r-white`}>
          <Face mood={mood} />
        </button>
        <span className="sr-only" aria-live="polite">{status === 'Won' ? `You won in ${seconds} seconds.` : status === 'Lost' ? 'You hit a mine.' : ''}</span>
        <span className={counter}>{fmt(seconds)}</span>
      </div>
      <div className="max-w-full overflow-x-auto">
        <div className={`w-max ${SUNKEN}`}>
          <div style={{ display: 'grid', width: W * SIZE, height: H * SIZE, gridTemplateColumns: `repeat(${W}, minmax(0, 1fr))`, gridTemplateRows: `repeat(${H}, minmax(0, 1fr))` }}>
            {cells.map(renderCell)}
          </div>
        </div>
      </div>
      {message && <p role="alert" className="text-[12px] break-words">{message}</p>}
    </div>
  );
}

export default GameView;
