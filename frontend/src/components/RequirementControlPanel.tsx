import React, { useEffect, useRef, useState } from 'react';
import AddIcon from '@mui/icons-material/Add';
import PlaylistPlayIcon from '@mui/icons-material/PlaylistPlay';
import { LivingDeckDTO, RuleCardDTO } from '../types/api';
import { StatusMessage, StudioMessage } from './StatusMessage';
import { SpecDetail } from './specs/SpecDetail';
import { SpecFormModal, SpecFormValues } from './specs/SpecFormModal';
import { SpecTree } from './specs/SpecTree';

const DECK_POLL_MS = 4000;
const TOAST_MS = 4000;
export const STACKED_LAYOUT = '(max-width: 768px)';  // keep in step with the media query in index.css
const DEFAULT_CHAPTER = 'General';

export interface RequirementControlPanelProps {
  onSpecsChanged?: () => void;
  building?: boolean;      // a build is running: the specifications are still being written
  testingIds?: string[];   // the specs the running build is working on
}

const errorOf = async (res: Response): Promise<string> => {
  try {
    const data = await res.json();
    return data.error || data.detail || `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
};

/** The specifications of the generated app: a tree by chapter, the selected one in detail, and add, edit, delete and run. */
export const RequirementControlPanel: React.FC<RequirementControlPanelProps> = ({ onSpecsChanged, building = false, testingIds }) => {
  const [cards, setCards] = useState<RuleCardDTO[]>([]);
  const [chapterOrder, setChapterOrder] = useState<string[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [toast, setToast] = useState<StudioMessage | null>(null);
  const [form, setForm] = useState<{ card: RuleCardDTO | null } | null>(null);  // open when set
  const [saving, setSaving] = useState<boolean>(false);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [runningAllSince, setRunningAllSince] = useState<string | null>(null);  // set while every test is running
  const detailRef = useRef<HTMLDivElement>(null);

  const notify = (message: StudioMessage) => {
    setToast(message);
    setTimeout(() => setToast(null), TOAST_MS);
  };
  const unreachable = (err: unknown) => {
    console.error(err);
    notify({ severity: 'error', text: 'Could not reach the server.' });
  };

  const loadDeck = async () => {
    try {
      const res = await fetch('/api/specs/deck');
      if (!res.ok) return;
      const deck: LivingDeckDTO = await res.json();
      setCards(deck.all_cards || []);
      setChapterOrder(Object.keys(deck.chapters || {}));
    } catch (err) {
      console.error('Could not load the specifications:', err);
    }
  };

  useEffect(() => {
    loadDeck();
    const interval = setInterval(loadDeck, DECK_POLL_MS);
    return () => clearInterval(interval);
  }, []);

  const changed = async () => {
    await loadDeck();
    if (onSpecsChanged) onSpecsChanged();
  };

  const selected = cards.find(c => c.id === selectedId) || cards[0] || null;

  const chapters = new Map<string, RuleCardDTO[]>(chapterOrder.map(name => [name, []]));
  for (const card of cards) {
    const chapter = card.chapter || DEFAULT_CHAPTER;
    chapters.set(chapter, [...(chapters.get(chapter) || []), card]);
  }

  const select = (card: RuleCardDTO) => {
    setSelectedId(card.id);
    // Stacked, the detail sits below the whole tree: bring it into view
    if (window.matchMedia(STACKED_LAYOUT).matches) {
      requestAnimationFrame(() => detailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
    }
  };

  const save = async (values: SpecFormValues) => {
    const editing = form?.card || null;
    setSaving(true);
    try {
      const res = await fetch(editing ? `/api/specs/deck/${editing.id}/update` : '/api/specs/deck/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...values, is_active: true }),
      });
      if (res.ok) {
        setForm(null);
        notify({ severity: 'success', text: `${editing ? 'Updated' : 'Added'}: ${values.title}` });
        await changed();
      } else {
        notify({ severity: 'error', text: `Could not save: ${await errorOf(res)}` });
      }
    } catch (err) {
      unreachable(err);
    } finally {
      setSaving(false);
    }
  };

  const remove = async (card: RuleCardDTO) => {
    if (!window.confirm(`Delete specification "${card.title}"?`)) return;
    try {
      const res = await fetch(`/api/specs/deck/${card.id}`, { method: 'DELETE' });
      if (res.ok) {
        notify({ severity: 'success', text: `Deleted: ${card.title}` });
        await changed();
      } else {
        notify({ severity: 'error', text: `Could not delete: ${await errorOf(res)}` });
      }
    } catch (err) {
      unreachable(err);
    }
  };

  // A run changes no code. Its outcome is not announced here: the deck is read again and the light and reason show it
  const runTest = async (card: RuleCardDTO, rewrite = false) => {
    setRunningId(card.id);
    try {
      const res = await fetch(`/api/specs/rules/${card.id}/test${rewrite ? '?rewrite=true' : ''}`, { method: 'POST' });
      if (!res.ok) notify({ severity: 'error', text: `Could not run the test: ${await errorOf(res)}` });
      await changed();
    } catch (err) {
      unreachable(err);
    } finally {
      setRunningId(null);
    }
  };

  // A fix changes the page and is kept only when the rule's test passes and no passing rule turned red
  const fixRule = async (card: RuleCardDTO) => {
    setRunningId(card.id);
    try {
      const res = await fetch(`/api/specs/rules/${card.id}/fix`, { method: 'POST' });
      if (!res.ok) {
        notify({ severity: 'error', text: `Could not fix: ${await errorOf(res)}` });
      } else {
        const result = await res.json();
        notify(result.success
          ? { severity: 'success', text: `Fixed: ${(result.files || []).join(', ')}` }
          : { severity: 'warning', text: `Not fixed, the page is as it was: ${result.reason || 'no reason given'}` });
      }
      await changed();
    } catch (err) {
      unreachable(err);
    } finally {
      setRunningId(null);
    }
  };

  // Each outcome is stored as it arrives, so the lights change one by one while the deck is polled
  const runAllTests = async () => {
    setRunningAllSince(new Date().toISOString());
    try {
      const res = await fetch('/api/specs/rules/test', { method: 'POST' });
      if (!res.ok) notify({ severity: 'error', text: `Could not run the tests: ${await errorOf(res)}` });
      await changed();
    } catch (err) {
      unreachable(err);
    } finally {
      setRunningAllSince(null);
    }
  };

  // While every test runs, a rule is being worked on until its test has run since the start
  const waiting = runningAllSince
    ? cards.filter(c => c.is_active !== false && !(c.page_test?.ran_at && c.page_test.ran_at >= runningAllSince.slice(0, 19))).map(c => c.id)
    : [];
  const busyIds = [...(testingIds || []), ...waiting];

  return (
    <div className="specs-panel">
      <div className="specs-panel-header">
        <h3 className="panel-title">Specifications</h3>
        <div className="specs-panel-actions">
          <button className="tool-btn" onClick={runAllTests} disabled={!!runningAllSince || building || cards.length === 0}>
            {runningAllSince ? <span className="spinner" /> : <PlaylistPlayIcon fontSize="inherit" />}
            {runningAllSince ? 'Running…' : 'Run all tests'}
          </button>
          <button className="tool-btn tool-btn-primary" onClick={() => setForm({ card: null })}>
            <AddIcon fontSize="inherit" /> Add
          </button>
        </div>
      </div>

      {toast && <StatusMessage message={toast} />}

      <div className="specs-master-detail">
        <SpecTree chapters={[...chapters.entries()].filter(([, list]) => list.length > 0)} selectedId={selected?.id || null} onSelect={select} building={building} testingIds={busyIds} />
        <SpecDetail
          ref={detailRef}
          card={selected}
          running={!!selected && runningId === selected.id}
          testing={!!selected && busyIds.includes(selected.id)}
          onEdit={card => setForm({ card })}
          onDelete={remove}
          onRunTest={card => runTest(card)}
          onRewriteTest={card => runTest(card, true)}
          onFix={fixRule}
        />
      </div>

      {form && (
        <SpecFormModal
          card={form.card}
          chapters={[...chapters.keys()]}
          saving={saving}
          onSave={save}
          onClose={() => setForm(null)}
        />
      )}
    </div>
  );
};
