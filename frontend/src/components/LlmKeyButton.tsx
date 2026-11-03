import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import KeyOutlinedIcon from '@mui/icons-material/KeyOutlined';
import { StatusMessage, type StudioMessage } from './StatusMessage';

interface KeyStatus {
  managed: boolean;
  configured?: boolean;
  provider?: string | null;
  last4?: string | null;
  house?: boolean;
  providers?: string[];
}

/** Fired after the key changes, so that whatever depends on having one asks again. */
export const LLM_KEY_CHANGED = 'provable:llm-key-changed';
/** Fired when something needs a key before it can go on: the key dialog opens. */
export const LLM_KEY_NEEDED = 'provable:llm-key-needed';

const PROVIDERS: Record<string, { label: string; keysAt: string }> = {
  gemini: { label: 'Google Gemini', keysAt: 'https://aistudio.google.com/apikey' },
  openai: { label: 'OpenAI', keysAt: 'https://platform.openai.com/api-keys' },
  anthropic: { label: 'Anthropic', keysAt: 'https://console.anthropic.com/settings/keys' },
};

const labelOf = (provider?: string | null) => (provider ? PROVIDERS[provider]?.label ?? provider : '');

/** The provider a pasted key's own prefix names, when it names one. */
function providerOfKey(key: string): string | null {
  const text = key.trim();
  if (text.startsWith('sk-ant-')) return 'anthropic';
  if (text.startsWith('AIza')) return 'gemini';
  if (text.startsWith('sk-')) return 'openai';
  return null;
}

/** The signed-in user's own LLM key; renders nothing on an engine that runs on its own settings. */
const LlmKeyButton: React.FC = () => {
  const [status, setStatus] = useState<KeyStatus | null>(null);
  const [unavailable, setUnavailable] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [provider, setProvider] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<StudioMessage | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/api/llm-key');
        const data = await res.json();
        if (res.ok) setStatus(data);
        else setUnavailable(String(data.detail ?? `HTTP ${res.status}`));
      } catch (err) {
        setUnavailable(`Could not reach the engine: ${String(err)}`);
      }
    };
    load();
    const openDialog = () => { setMessage(null); setOpen(true); };
    window.addEventListener(LLM_KEY_NEEDED, openDialog);
    return () => window.removeEventListener(LLM_KEY_NEEDED, openDialog);
  }, []);

  if (unavailable) {
    return <button className="project-selector-btn" disabled title={unavailable}><KeyOutlinedIcon fontSize="small" /><span className="project-selector-name">LLM keys unavailable</span></button>;
  }
  if (!status?.managed) return null;
  const chosen = provider || status.provider || status.providers?.[0] || '';
  const canSave = !saving && apiKey.trim().length > 0;

  const send = async (method: 'PUT' | 'DELETE', body?: object) => {
    setSaving(true);
    setMessage(null);
    try {
      const res = await fetch('/api/llm-key', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
      });
      const data = await res.json();
      if (!res.ok) {
        setMessage({ severity: 'error', text: String(data.detail ?? `HTTP ${res.status}`) });
        return;
      }
      setStatus(data);
      setApiKey('');
      setProvider('');
      if (method === 'PUT') setOpen(false);  // the header now shows the saved key
      window.dispatchEvent(new Event(LLM_KEY_CHANGED));
    } catch (err) {
      setMessage({ severity: 'error', text: `Could not reach the engine: ${String(err)}` });
    } finally {
      setSaving(false);
    }
  };

  const save = () => { if (canSave) send('PUT', { provider: chosen, api_key: apiKey }); };

  const typeKey = (value: string) => {
    setApiKey(value);
    const named = providerOfKey(value);
    if (named && status.providers?.includes(named)) setProvider(named);
  };

  return (
    <>
      <button
        id="llm-key-btn"
        className={`project-selector-btn${status.configured ? '' : ' llm-key-missing'}`}
        onClick={() => { setMessage(null); setOpen(true); }}
      >
        <KeyOutlinedIcon fontSize="small" />
        <span className="project-selector-name">
          {status.configured ? (status.last4 ? `${labelOf(status.provider)} ...${status.last4}` : 'House key') : 'Add LLM key'}
        </span>
      </button>

      {open && createPortal(
        <div className="modal-overlay" onClick={() => setOpen(false)} onKeyDown={e => e.key === 'Escape' && setOpen(false)}>
          <div className="modal-box" role="dialog" aria-modal="true" aria-labelledby="llm-key-title" onClick={e => e.stopPropagation()}>
            <h3 id="llm-key-title">Your LLM key</h3>
            <p className="llm-key-note">Builds run on this key. Your provider bills you.</p>
            <p className="llm-key-note">Stored encrypted. Never shown again.</p>
            {status.last4 && <p className="llm-key-note llm-key-current">In use: {labelOf(status.provider)} ...{status.last4}</p>}
            <label className="llm-key-label" htmlFor="llm-key-provider">Provider</label>
            <select id="llm-key-provider" className="modal-input" value={chosen} onChange={e => setProvider(e.target.value)}>
              {status.providers?.map(name => <option key={name} value={name}>{labelOf(name)}</option>)}
            </select>
            <label className="llm-key-label" htmlFor="llm-key-input">{status.last4 ? 'New API key' : 'API key'}</label>
            <input
              id="llm-key-input"
              type="password"
              autoComplete="off"
              className="modal-input"
              value={apiKey}
              onChange={e => typeKey(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && save()}
              autoFocus
            />
            {PROVIDERS[chosen] && (
              <a className="llm-key-link" href={PROVIDERS[chosen].keysAt} target="_blank" rel="noreferrer">
                Get a key from {labelOf(chosen)}
              </a>
            )}
            {message && <StatusMessage message={message} />}
            <div className="modal-actions">
              {status.last4 && (
                <button className="btn btn-outline" disabled={saving} onClick={() => send('DELETE')}>Remove key</button>
              )}
              <button className="btn btn-outline" onClick={() => setOpen(false)}>Close</button>
              <button id="llm-key-save-btn" className="btn btn-primary" disabled={!canSave} onClick={save}>
                {saving ? 'Saving...' : 'Save key'}
              </button>
            </div>
          </div>
        </div>,
        document.body,  // the header's backdrop filter would otherwise clip the overlay to the header
      )}
    </>
  );
};

export default LlmKeyButton;
