import { useCallback, useEffect, useState } from 'react';
import { createGame, listGame, sendAction, type GameState } from './api/gameClient';
import { listDifficultySetting, type DifficultySettingState } from './api/difficulty_settingClient';
import GameView from './views/GameView';

const msg = (e: unknown) => (e instanceof Error ? e.message : 'Something went wrong.');

export const App = () => {
  const [game, setGame] = useState<GameState | null>(null);
  const [settings, setSettings] = useState<DifficultySettingState[]>([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setBusy(true);
      setError(null);
      try {
        const [games, diffs] = await Promise.all([listGame(), listDifficultySetting()]);
        setSettings(diffs);
        setGame(games[games.length - 1] ?? (await createGame({ difficulty: 'Beginner' })));
      } catch (e) {
        setError(msg(e));
      } finally {
        setBusy(false);
      }
    };
    void load();
  }, []);

  const gameId = game?.id;

  const handleAction = useCallback(
    async (actionType: string, params?: Record<string, unknown>) => {
      if (!gameId) return;
      setBusy(true);
      setError(null);
      try {
        const res = await sendAction(gameId, actionType, params);
        setGame(res.state);
      } catch (e) {
        setError(msg(e));
      } finally {
        setBusy(false);
      }
    },
    [gameId],
  );

  return (
    <div className="flex min-h-screen justify-center bg-[#94a3b8] p-2 font-sans text-stone-900 sm:p-6">
      <div className="flex w-full max-w-full flex-col items-center gap-3">
        <header className="flex w-full items-center justify-between gap-2">
          <h1 className="sr-only">Minesweeper</h1>
          {busy && game && <span className="text-xs text-stone-900">Working…</span>}
        </header>
        <main className="max-w-full rounded-sm border border-white bg-[#bdbdbd] p-2">
          {game ? (
            <GameView game={game} settings={settings} error={error} onAction={handleAction} />
          ) : (
            <p className="p-4 text-sm break-words">{error ?? 'Loading…'}</p>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
