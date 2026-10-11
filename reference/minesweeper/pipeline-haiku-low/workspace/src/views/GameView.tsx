import React, { useEffect, useState } from 'react';
import { Game, fetchGameList, createGame } from '../api/client';

// A first draft of the app: the records as they are, until the page is written.
const TITLE_FIELD = 'difficulty';
const FORM_FIELDS: { name: string; numeric: boolean }[] = [{ name: 'difficulty', numeric: false }, { name: 'status', numeric: false }, { name: 'started_at', numeric: false }, { name: 'ended_at', numeric: false }, { name: 'elapsed_seconds', numeric: true }, { name: 'mine_count', numeric: true }, { name: 'flag_count', numeric: true }];

const label = (key: string) => key.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
const shown = (value: unknown): string =>
  Array.isArray(value) ? String(value.length)
    : typeof value === 'boolean' ? (value ? 'Yes' : 'No')
    : value === null || value === undefined || value === '' ? '–' : String(value);
const listed = (key: string) => key !== 'id' && key !== 'events' && key !== TITLE_FIELD && !key.endsWith('_id');

const surface = { background: 'var(--draft-surface)', borderColor: 'color-mix(in srgb, var(--draft-text) 14%, transparent)' };
const muted = { color: 'color-mix(in srgb, var(--draft-text) 62%, transparent)' };
const accent = { background: 'var(--draft-accent)', color: 'var(--draft-on-accent)' };
const heading = { fontFamily: 'var(--draft-heading-font)' };

export const GameView: React.FC = () => {
  const [items, setItems] = useState<Game[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const [formData, setFormData] = useState<Record<string, any>>({});

  const load = async () => {
    try {
      setItems(await fetchGameList());
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Could not load games');
    }
  };

  // The starting content is written a little after the app starts: ask again while there is nothing to show
  const empty = items.length === 0;
  useEffect(() => {
    load();
    if (!empty) return;
    const timer = setInterval(load, 3000);
    return () => clearInterval(timer);
  }, [empty]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createGame(formData);
      setAdding(false);
      setFormData({});
      await load();
    } catch (err: any) {
      setError(err.message || 'Could not save');
    }
  };

  return (
    <section className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold" style={heading}>Games</h2>
        {FORM_FIELDS.length > 0 && (
          <button onClick={() => setAdding(!adding)} className="px-4 py-2 rounded-lg text-sm font-medium" style={accent}>
            {adding ? 'Close' : 'Add'}
          </button>
        )}
      </div>

      {error && <p className="rounded-lg border px-4 py-3 text-sm" style={surface} role="alert">{error}</p>}

      {adding && (
        <form onSubmit={handleCreate} className="rounded-xl border p-5 space-y-4" style={surface}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {FORM_FIELDS.map(field => (
              <label key={field.name} className="block text-sm">
                <span className="block mb-1" style={muted}>{label(field.name)}</span>
                <input
                  type={field.numeric ? 'number' : 'text'}
                  value={formData[field.name] ?? ''}
                  onChange={e => setFormData({ ...formData, [field.name]: field.numeric && e.target.value !== '' ? Number(e.target.value) : e.target.value })}
                  className="w-full rounded-lg border px-3 py-2 text-sm bg-transparent"
                  style={{ borderColor: surface.borderColor }}
                />
              </label>
            ))}
          </div>
          <button type="submit" className="px-4 py-2 rounded-lg text-sm font-medium" style={accent}>Save</button>
        </form>
      )}

      {empty ? (
        <p className="rounded-xl border border-dashed px-6 py-10 text-center text-sm" style={{ ...surface, ...muted }}>Nothing here yet.</p>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item, index) => (
            <li key={item.id || index} className="rounded-xl border p-5" style={surface}>
              <h3 className="text-lg font-semibold mb-3" style={heading}>{shown(item[TITLE_FIELD])}</h3>
              <dl className="space-y-1.5 text-sm">
                {Object.keys(item).filter(listed).map(key => (
                  <div key={key} className="flex justify-between gap-4">
                    <dt style={muted}>{label(key)}</dt>
                    <dd className="text-right break-words min-w-0">{shown(item[key])}</dd>
                  </div>
                ))}
              </dl>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
};
