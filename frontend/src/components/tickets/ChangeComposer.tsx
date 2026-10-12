import React, { useState } from 'react';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import { ChangeCardDTO } from '../../types/api';
import { StatusMessage, StudioMessage } from '../StatusMessage';
import { ChangeCard } from './ChangeCard';

/** Asks for a change to the built app in plain words and shows the planned change as a card. */
export const ChangeComposer: React.FC<{ disabled?: boolean }> = ({ disabled = false }) => {
  const [request, setRequest] = useState<string>('');
  const [planning, setPlanning] = useState<boolean>(false);
  const [card, setCard] = useState<ChangeCardDTO | null>(null);
  const [message, setMessage] = useState<StudioMessage | null>(null);

  const canPlan = !disabled && !planning && !!request.trim();

  const plan = async () => {
    if (!canPlan) return;
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
      {card && <ChangeCard card={card} onDiscard={() => setCard(null)} />}
      {message && <StatusMessage message={message} />}
      <div className="change-composer-row">
        <textarea
          className="change-composer-input"
          value={request}
          onChange={e => setRequest(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) plan(); }}
          placeholder="What should change?"
          aria-label="What should change?"
          rows={2}
          disabled={disabled || planning}
        />
        <button className="tool-btn tool-btn-primary" onClick={plan} disabled={!canPlan} title="Plan the change (Ctrl + Enter)">
          {planning ? <span className="spinner" /> : <AutoFixHighIcon fontSize="inherit" />}
          {planning ? 'Planning…' : card ? 'Plan again' : 'Plan'}
        </button>
      </div>
    </div>
  );
};

export default ChangeComposer;
