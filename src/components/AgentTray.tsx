import React from 'react';

interface AgentTrayProps {
  agentStatus: {
    active: boolean;
    ticket_id: string | null;
    step: string;
    attempt: number;
    max_attempts: number;
    last_update: string;
  };
  backlogAnalysis: any[];
  agentLogs: string;
  isTrayExpanded: boolean;
  setIsTrayExpanded: (expanded: boolean) => void;
  fetchAgentStatus: () => void;
}

const AgentTray: React.FC<AgentTrayProps> = ({
  agentStatus,
  backlogAnalysis,
  agentLogs,
  isTrayExpanded,
  setIsTrayExpanded,
  fetchAgentStatus
}) => {
  return (
    <div className={`agent-dashboard-tray ${isTrayExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="agent-tray-header" onClick={() => setIsTrayExpanded(!isTrayExpanded)}>
        <div className="agent-status-indicator">
          <div className={`agent-status-glow ${agentStatus.active ? 'active' : 'idle'}`}></div>
          <span>
            <strong>Agent Status:</strong>{' '}
            {agentStatus.active ? (
              <span style={{ color: 'var(--accent-success)' }}>
                Active ({agentStatus.step} - Ticket {agentStatus.ticket_id || 'N/A'}, Attempt {agentStatus.attempt}/{agentStatus.max_attempts})
              </span>
            ) : (
              <span style={{ color: 'var(--accent-warning)' }}>Idle</span>
            )}
          </span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            className="btn btn-outline"
            style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem', borderColor: 'rgba(255,255,255,0.2)' }}
            onClick={async (e) => {
              e.stopPropagation();
              try {
                const res = await fetch('/api/trigger-agents', { method: 'POST' });
                const data = await res.json();
                alert(data.message || "Agent loop dispatched.");
                fetchAgentStatus();
              } catch (err) {
                alert("Failed to trigger agent.");
              }
            }}
          >
            🚀 Dispatch Agent
          </button>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Last Update: {agentStatus.last_update || 'N/A'}
          </span>
          <span style={{ fontSize: '0.8rem', transform: isTrayExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>
            ▲
          </span>
        </div>
      </div>

      {isTrayExpanded && (
        <div className="agent-tray-content">
          <div className="agent-tray-section" style={{ flex: 1.5 }}>
            <div className="agent-tray-section-title">Live Agent Console Logs</div>
            <div className="agent-terminal-panel">
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: '#c9d1d9' }}>
                {agentLogs || (agentStatus.active ? "Connecting to agent log stream..." : "Agent is idle. No logs to stream.")}
              </pre>
            </div>
          </div>

          <div className="agent-tray-section" style={{ flex: 1 }}>
            <div className="agent-tray-section-title">Backlog Dispatch Queue</div>
            <div className="agent-queue-panel">
              {backlogAnalysis.length === 0 ? (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center', margin: 'auto' }}>
                  No pending tasks in backlog.
                </div>
              ) : (
                backlogAnalysis.map((item: any) => (
                  <div key={item.id} className={`queue-item ${item.is_blocked ? 'blocked' : 'ready'}`}>
                    <div className="queue-item-header">
                      <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.id}</span>
                      <span className={item.is_blocked ? 'status-badge-blocked' : 'status-badge-ready'}>
                        {item.is_blocked ? 'Blocked' : 'Ready'}
                      </span>
                    </div>
                    <div className="queue-item-title" title={item.title}>{item.title}</div>
                    {item.is_blocked && item.reasons.length > 0 && (
                      <div className="queue-item-reasons">
                        {item.reasons.map((r: string, idx: number) => (
                          <div key={idx}>⚠️ {r}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentTray;
