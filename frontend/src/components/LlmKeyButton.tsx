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

/** The signed-in user's own LLM key; renders nothing on an engine that runs on its own settings. */
const LlmKeyButton: React.FC = () => {
  const [status, setStatus] = useState<KeyStatus | null>(null);
  const [open, setOpen] = useState(false);
  const [provider, setProvider] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<StudioMessage | null>(null);

  useEffect(() => {
    fetch('/api/llm-key')
      .then(res => (res.ok ? res.json() : null))
      .then(setStatus)
      .catch(err => console.error('Failed to fetch the LLM key status', err));
  }, []);

  if (!status?.managed) return null;
  const chosen = provider || status.provider || status.providers?.[0] || '';

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
      setMessage({ severity: 'success', text: method === 'PUT' ? 'Key saved.' : 'Key removed.' });
      window.dispatchEvent(new Event(LLM_KEY_CHANGED));
    } catch (err) {
      setMessage({ severity: 'error', text: `Could not reach the engine: ${String(err)}` });
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <button id="llm-key-btn" className="project-selector-btn" onClick={() => { setMessage(null); setOpen(true); }}>
        <KeyOutlinedIcon fontSize="small" />
        <span className="project-selector-name">
          {status.configured ? (status.last4 ? `${status.provider} ...${status.last4}` : 'House key') : 'Add LLM key'}
        </span>
      </button>

      {open && createPortal(
        <div className="modal-overlay" onClick={() => setOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h3>Your LLM key</h3>
            <p className="llm-key-note">Builds run on this key. Your provider bills you.</p>
            <p className="llm-key-note">Stored encrypted. Never shown again.</p>
            <select id="llm-key-provider" className="modal-input" value={chosen} onChange={e => setProvider(e.target.value)}>
              {status.providers?.map(name => <option key={name} value={name}>{name}</option>)}
            </select>
            <input
              id="llm-key-input"
              type="password"
              autoComplete="off"
              className="modal-input"
              placeholder="API key"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              autoFocus
            />
            {message && <StatusMessage message={message} />}
            <div className="modal-actions">
              {status.last4 && (
                <button className="btn btn-outline" disabled={saving} onClick={() => send('DELETE')}>Remove key</button>
              )}
              <button className="btn btn-outline" onClick={() => setOpen(false)}>Close</button>
              <button
                id="llm-key-save-btn"
                className="btn btn-primary"
                disabled={saving || !apiKey.trim()}
                onClick={() => send('PUT', { provider: chosen, api_key: apiKey })}
              >
                Save key
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
