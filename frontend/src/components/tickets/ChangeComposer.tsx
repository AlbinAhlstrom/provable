import React, { useState } from 'react';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import { ChangeCardDTO } from '../../types/api';
import { StatusMessage, StudioMessage } from '../StatusMessage';
import { ChangeCard } from './ChangeCard';

export interface ChangeComposerProps {
  built: boolean;                    // an app exists: a request is a change to it; otherwise it is the app to build
  onBuild: (pitch: string) => void;
  draft?: string;                    // what was last asked for, when it did not become an app
  disabled?: boolean;
}

/** Where everything is asked for in plain words: the first app, and then each change to it, shown as a card. */
export const ChangeComposer: React.FC<ChangeComposerProps> = ({ built, onBuild, draft = '', disabled = false }) => {
  const [request, setRequest] = useState<string>(built ? '' : draft);
  const [planning, setPlanning] = useState<boolean>(false);
  const [card, setCard] = useState<ChangeCardDTO | null>(null);
  const [message, setMessage] = useState<StudioMessage | null>(null);

  const canPlan = !disabled && !planning && !!request.trim();

  const plan = async () => {
    if (!canPlan) return;
    if (!built) return onBuild(request.trim());
    setPlanning(true);
    setMessage(null);
    try {
      const res = await fetch('/api/tickets/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request: request.trim() }),
      });
      let data: any = {};
      try {
        data = await res.json();
      } catch {
        data = { error: `Server returned HTTP ${res.status}` };
      }
      if (res.ok && data.success) {
        setCard(data as ChangeCardDTO);
      } else {
        setMessage({ severity: 'error', text: data.error || data.detail || `HTTP ${res.status}` });
      }
    } catch (err: any) {
      console.error('Could not plan the change:', err);
      setMessage({ severity: 'error', text: `Could not reach the server${err?.message ? `: ${err.message}` : ''}` });
    } finally {
      setPlanning(false);
    }
  };

  return (
    <div className="change-composer">
      {built && card && <ChangeCard card={card} onDiscard={() => setCard(null)} />}
      {message && <StatusMessage message={message} />}
      <div className="change-composer-row">
        <textarea
          className="change-composer-input"
          value={request}
          onChange={e => setRequest(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) plan(); }}
          placeholder={built ? 'What should change?' : 'Describe your app'}
          aria-label={built ? 'What should change?' : 'Describe your app'}
          rows={built ? 2 : 4}
          autoFocus={!built}
          disabled={disabled || planning}
        />
        {built ? (
          <button className="tool-btn tool-btn-primary" onClick={plan} disabled={!canPlan} title="Plan the change (Ctrl + Enter)">
            {planning ? <span className="spinner" /> : <AutoFixHighIcon fontSize="inherit" />}
            {planning ? 'Planning…' : card ? 'Plan again' : 'Plan'}
          </button>
        ) : (
          <button className="tool-btn tool-btn-primary" onClick={plan} disabled={!canPlan} title="Build the app (Ctrl + Enter)">
            <RocketLaunchIcon fontSize="inherit" /> Build
          </button>
        )}
      </div>
    </div>
  );
};

export default ChangeComposer;
