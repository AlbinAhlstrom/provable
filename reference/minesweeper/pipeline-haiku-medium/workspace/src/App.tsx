import { useEffect, useRef, useState } from 'react';
import { listDifficulty, type DifficultyState } from './api/difficultyClient';
import {
  listGameSession,
  getGameSession,
  createGameSession,
  sendAction,
  type GameSessionState,
} from './api/game_sessionClient';
import { GameSessionView } from './views/GameSessionView';
import { GameSessionControls } from './components/Controls/GameSessionControls';

const toMessage = (e: unknown) => (e instanceof Error ? e.message : 'Something went wrong. Try again.');
const boardParams = (d: DifficultyState) => ({
  difficulty_id: d.id,
  rows: d.rows,
  columns: d.columns,
  mine_count: d.mine_count,
});

export const App = () => {
  const [difficulties, setDifficulties] = useState<DifficultyState[]>([]);
  const [session, setSession] = useState<GameSessionState | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const started = useRef(false);

  const run = async (task: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await task();
    } catch (e) {
      setError(toMessage(e));
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void run(async () => {
      const [diffs, sessions] = await Promise.all([listDifficulty(), listGameSession()]);
      setDifficulties(diffs);
      const start = diffs.find((d) => d.name === 'Beginner') ?? diffs[0];
      let current: GameSessionState | undefined = sessions[sessions.length - 1];
      if (!current && start) current = await createGameSession(boardParams(start));
      setSession(current ?? null);
    });
  }, []);

  // Keep the elapsed time current while a game runs by reading the server record.
  const sessionId = session?.id;
  const sessionStatus = session?.status;
  useEffect(() => {
    if (!sessionId || sessionStatus !== 'in_progress') return;
    const t = window.setInterval(() => {
      getGameSession(sessionId)
        .then((s) => setSession((prev) => (prev?.id === sessionId && prev.status === 'in_progress' ? s : prev)))
        .catch(() => undefined);
    }, 1000);
    return () => window.clearInterval(t);
  }, [sessionId, sessionStatus]);

  const handleAction = (actionType: string, params?: Record<string, unknown>) =>
    run(async () => {
      if (!session) return;
      const res = await sendAction(session.id, actionType, params);
      setSession(res.state);
    });

  const newGame = () =>
    run(async () => {
      if (!session) return;
      let current = session;
      if (current.status === 'ready' || current.status === 'in_progress') {
        current = (await sendAction(current.id, 'abandon_game')).state;
        setSession(current);
      }
      const res = await sendAction(current.id, 'start_new_game', {
        difficulty_id: current.difficulty_id,
        rows: current.rows,
        columns: current.columns,
        mine_count: current.mine_count,
      });
      setSession(res.state);
    });

  return (
    <div className="min-h-screen bg-[#c0c0c0] font-sans text-[#111111]">
      <header className="flex items-center justify-between px-3 py-3 sm:px-6">
        <h1 className="text-base font-bold">Minesweeper</h1>
      </header>
      <main className="flex flex-col items-center gap-3 px-3 pb-6">
        {session ? (
          <GameSessionView
            session={session}
            busy={busy}
            error={error}
            onReveal={(row, column) => handleAction('reveal_cell', { row, column })}
            onFlag={(row, column) => handleAction('toggle_flag', { row, column })}
            onFace={newGame}
          >
            <GameSessionControls
              difficulties={difficulties}
              session={session}
              busy={busy}
              onAction={handleAction}
            />
          </GameSessionView>
        ) : (
          <p role="status" className="text-center text-sm">
            {busy ? 'Loading…' : error ?? 'No board is available yet.'}
          </p>
        )}
      </main>
    </div>
  );
};

export default App;
