import { useState } from 'react';
import type { GameState } from '../../api/gameClient';
import type { DifficultyState } from '../../api/difficultyClient';
import { Dialog, BTN } from '../History/GameHistory';

type Act = (type: string, params?: Record<string, unknown>) => Promise<string | null>;
type Props = { game: GameState | null; difficulties: DifficultyState[]; onAction: Act; onShowBest: () => void };

export function newGameData(difficulty_id: string, width: number, height: number, mine_count: number): Partial<GameState> {
  const cells = [];
  for (let r = 0; r < height; r++) for (let c = 0; c < width; c++) {
    cells.push({ id: `${r}-${c}`, row: r, column: c, has_mine: false, adjacent_mine_count: 0, state: 'Hidden' });
  }
  return {
    difficulty_id, width, height, mine_count, remaining_mines: mine_count, created_at: new Date().toISOString(),
    status: 'Ready', mines_laid: false, flags_placed: 0, elapsed_seconds: 0, cells,
  } as unknown as Partial<GameState>;
}

function CustomDialog({ game, onAction, onClose }: { game: GameState; onAction: Act; onClose: () => void }) {
  const [w, setW] = useState(String(game.width ?? 9));
  const [h, setH] = useState(String(game.height ?? 9));
  const [m, setM] = useState(String(game.mine_count ?? 10));
  const [bad, setBad] = useState<Record<string, boolean>>({});
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const W = Number(w); const H = Number(h); const M = Number(m);
  const max = Number.isInteger(W) && Number.isInteger(H) && W >= 2 && H >= 2 ? (W - 1) * (H - 1) : null;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (busy) return;
    const b = {
      w: w === '' || !Number.isInteger(W) || W < 9 || W > 30,
      h: h === '' || !Number.isInteger(H) || H < 9 || H > 24,
      m: m === '' || max === null || !Number.isInteger(M) || M < 10 || M > max,
    };
    setBad(b);
    if (b.w || b.h || b.m) { setErr(`Width must be 9–30, height 9–24, and mines 10–${max ?? '…'}.`); return; }
    setBusy(true);
    try {
      const msg = await onAction('change_difficulty', { difficulty_id: 'custom', width: W, height: H, mine_count: M });
      if (msg) setErr(msg); else onClose();
    } finally { setBusy(false); }
  };

  const fields = [
    { id: 'custom-width', label: 'Width', val: w, set: setW, hint: '9–30', bad: bad.w },
    { id: 'custom-height', label: 'Height', val: h, set: setH, hint: '9–24', bad: bad.h },
    { id: 'custom-mines', label: 'Mines', val: m, set: setM, hint: `10–${max ?? '…'}`, bad: bad.m },
  ];
  return (
    <Dialog title="Custom Field">
      <form onSubmit={submit} className="flex flex-col gap-2" noValidate>
        {fields.map((f) => (
          <div key={f.id} className="flex flex-col">
            <div className="flex items-center justify-between gap-3">
              <label htmlFor={f.id}>{f.label}</label>
              <input id={f.id} type="number" inputMode="numeric" value={f.val} onChange={(e) => f.set(e.target.value)}
                className={`w-20 bg-white px-1 py-0.5 border-2 border-t-gray-600 border-l-gray-600 border-b-white border-r-white ${f.bad ? 'outline outline-2 outline-red-600' : ''}`} />
            </div>
            <span className="text-[12px] text-gray-700 self-end">{f.hint}</span>
          </div>
        ))}
        {err && <p role="alert" className="text-[12px] text-red-700 break-words max-w-[14rem]">{err}</p>}
        <div className="flex justify-end gap-2 pt-1">
          <button type="submit" className={BTN}>OK</button>
          <button type="button" className={BTN} onClick={onClose}>Cancel</button>
        </div>
      </form>
    </Dialog>
  );
}

export function GameControls({ game, difficulties, onAction, onShowBest }: Props) {
  const [open, setOpen] = useState(false);
  const [custom, setCustom] = useState(false);
  const item = 'block w-full text-left px-5 py-0.5 hover:bg-[#000080] hover:text-white relative';

  const pick = (d: DifficultyState) => {
    setOpen(false);
    if (!d.is_standard) { setCustom(true); return; }
    void onAction('change_difficulty', { difficulty_id: d.id, width: d.width, height: d.height, mine_count: d.mine_count });
  };

  return (
    <nav className="relative flex text-[13px]">
      <button type="button" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen((o) => !o)}
        className={`px-2 py-0.5 ${open ? 'bg-[#000080] text-white' : 'hover:bg-[#000080] hover:text-white'}`}>
        Game
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div role="menu" className="absolute left-0 top-full z-20 w-44 bg-[#c0c0c0] py-1 border-2 border-t-white border-l-white border-b-gray-600 border-r-gray-600">
            <button type="button" role="menuitem" className={item} onClick={() => { setOpen(false); void onAction('restart_game'); }}>New Game</button>
            <div className="my-1 border-t border-gray-600 border-b border-b-white" />
            {difficulties.length === 0 && <p className="px-5 py-0.5 text-gray-700">No difficulties available.</p>}
            {difficulties.map((d) => (
              <button key={d.id} type="button" role="menuitemradio" aria-checked={game?.difficulty_id === d.id} className={item} onClick={() => pick(d)}>
                {game?.difficulty_id === d.id && <span className="absolute left-1.5">{'✓\uFE0E'}</span>}
                {d.is_standard ? d.name : `${d.name ?? ''}…`}
              </button>
            ))}
            <div className="my-1 border-t border-gray-600 border-b border-b-white" />
            <button type="button" role="menuitem" className={item} onClick={() => { setOpen(false); onShowBest(); }}>Best Times…</button>
          </div>
        </>
      )}
      {custom && game && <CustomDialog game={game} onAction={onAction} onClose={() => setCustom(false)} />}
    </nav>
  );
}

export default GameControls;
