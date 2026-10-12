import { useEffect, useRef, useState } from 'react';
import { createGame, listGame, sendAction, type GameState } from './api/gameClient';
import { listDifficulty, type DifficultyState } from './api/difficultyClient';
import { listBestTime, type BestTimeState } from './api/best_timeClient';
import { GameView, elapsedSeconds } from './views/GameView';
import { GameControls, newGameData } from './components/Controls/GameControls';
import { GameHistory, NewBestDialog, recordBest, BTN } from './components/History/GameHistory';

const KEY = 'minesweeper-difficulty';
const errText = (e: unknown) => (e instanceof Error ? e.message : String(e));

export const App = () => {
  const [game, setGame] = useState<GameState | null>(null);
  const [difficulties, setDifficulties] = useState<DifficultyState[]>([]);
  const [bests, setBests] = useState<BestTimeState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [showBest, setShowBest] = useState(false);
  const [newBest, setNewBest] = useState<{ id: string; seconds: number } | null>(null);
  const current = useRef<GameState | null>(null);
  current.current = game;

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const [games, diffs, times] = await Promise.all([listGame(), listDifficulty(), listBestTime()]);
      const sorted = [...diffs].sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0));
      setDifficulties(sorted); setBests(times);
      const last = games[games.length - 1];
      if (last && last.status !== 'Abandoned') { setGame(last); return; }
      const saved = sorted.find((d) => d.is_standard && d.id === localStorage.getItem(KEY));
      const data = last ? newGameData(last.difficulty_id, last.width, last.height, last.mine_count)
        : saved ? newGameData(saved.id, saved.width, saved.height, saved.mine_count) : newGameData('beginner', 9, 9, 10);
      setGame(await createGame(data));
    } catch (e) { setError(errText(e)); } finally { setLoading(false); }
  };

  useEffect(() => { void load(); }, []);
  useEffect(() => { if (game?.difficulty_id) localStorage.setItem(KEY, game.difficulty_id); }, [game?.difficulty_id]);
  useEffect(() => {
    const leave = () => {
      const g = current.current;
      if (g && (g.status === 'Ready' || g.status === 'Playing')) void sendAction(g.id, 'abandon_game').catch(() => undefined);
    };
    window.addEventListener('pagehide', leave);
    return () => window.removeEventListener('pagehide', leave);
  }, []);

  const handleAction = async (actionType: string, params?: Record<string, unknown>): Promise<string | null> => {
    const g = current.current;
    if (!g) return null;
    setActionError(null);
    try {
      const res = await sendAction(g.id, actionType, params ?? {});
      const next = res.state;
      setGame(next);
      if (g.status !== 'Won' && next.status === 'Won' && next.id === g.id) {
        const secs = elapsedSeconds(next, Date.now());
        const r = await recordBest(next, bests, secs);
        setBests(r.list);
        if (r.improved) setNewBest({ id: next.difficulty_id, seconds: secs });
      }
      return null;
    } catch (e) { const m = errText(e); setActionError(m); return m; }
  };

  return (
    <div className="min-h-screen bg-teal-700 p-2 sm:p-6 flex items-start sm:items-center justify-center font-sans text-[13px] text-black">
      <div className="w-max max-w-full min-w-0 bg-[#c0c0c0] p-[3px] border-2 border-t-white border-l-white border-b-gray-600 border-r-gray-600">
        <header className="bg-[#000080] text-white font-bold px-2 py-0.5 truncate">Minesweeper</header>
        <GameControls game={game} difficulties={difficulties} onAction={handleAction} onShowBest={() => setShowBest(true)} />
        <main className="p-[6px] min-w-0">
          {loading && !game && <p className="p-4">Loading game…</p>}
          {error && (
            <div className="p-4 flex flex-col gap-2 items-start">
              <p role="alert" className="break-words">{error}</p>
              <button type="button" className={BTN} onClick={() => void load()}>Try again</button>
            </div>
          )}
          {game && <GameView game={game} onAction={handleAction} message={actionError} />}
        </main>
      </div>
      {showBest && <GameHistory difficulties={difficulties} bests={bests} onClose={() => setShowBest(false)} />}
      {newBest && (
        <NewBestDialog name={difficulties.find((d) => d.id === newBest.id)?.name} seconds={newBest.seconds} onClose={() => setNewBest(null)} />
      )}
    </div>
  );
};

export default App;
