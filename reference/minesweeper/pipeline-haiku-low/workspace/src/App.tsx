import React, { useState } from 'react';
import { GameView } from './views/GameView';
import { DifficultySettingView } from './views/DifficultySettingView';

// A first draft of the app: what it keeps track of, shown plainly until the page is written.
const TABS: { name: string; label: string; view: React.FC }[] = [
  { name: 'Game', label: 'Games', view: GameView },
  { name: 'DifficultySetting', label: 'Difficulty settings', view: DifficultySettingView },
];

export const App: React.FC = () => {
  const [active, setActive] = useState<string>(TABS[0]?.name ?? '');
  const View = TABS.find(tab => tab.name === active)?.view;

  return (
    <div className="min-h-screen" style={{ background: 'var(--draft-bg)', color: 'var(--draft-text)' }}>
      <header className="max-w-5xl mx-auto px-4 sm:px-6 pt-10 pb-2">
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight" style={{ fontFamily: 'var(--draft-heading-font)' }}>Minesweeper</h1>
        {TABS.length > 1 && (
          <nav className="mt-6 flex flex-wrap gap-2">
            {TABS.map(tab => (
              <button
                key={tab.name}
                onClick={() => setActive(tab.name)}
                className="px-4 py-2 rounded-full text-sm font-medium border"
                style={tab.name === active
                  ? { background: 'var(--draft-accent)', color: 'var(--draft-on-accent)', borderColor: 'var(--draft-accent)' }
                  : { borderColor: 'color-mix(in srgb, var(--draft-text) 20%, transparent)' }}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        )}
      </header>
      {/* The outline of the main view, drawn by theme.css once the plan has chosen its form */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6"><div className="draft-shape" aria-hidden="true" /></div>
      <main>{View && <View />}</main>
    </div>
  );
};

export default App;
