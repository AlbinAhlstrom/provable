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

const PIPELINE_STAGES = [
  { id: 1, label: '1. Prepare Branch', keys: ['prepare', 'preparing', 'branch'] },
  { id: 2, label: '2. Code Generation', keys: ['code', 'generation', 'openhands', 'executing'] },
  { id: 3, label: '3. Test Runner', keys: ['test', 'verifying', 'runner'] },
  { id: 4, label: '4. Visual QA', keys: ['visual', 'qa', 'review'] },
  { id: 5, label: '5. Finalize', keys: ['finalize', 'finalizing', 'completed'] },
];

function getStageIndex(step: string, active: boolean): number {
  if (!step) return 0;
  const s = step.toLowerCase();
  if (s.includes('completed')) return 6;
  if (s.includes('prepare') || s.includes('branch')) return 1;
  if (s.includes('code') || s.includes('generation') || s.includes('openhands') || s.includes('executing')) return 2;
  if (s.includes('test') || s.includes('verifying') || s.includes('runner')) return 3;
  if (s.includes('visual') || s.includes('qa') || s.includes('review')) return 4;
  if (s.includes('finalize') || s.includes('finalizing')) return 5;
  if (active) return 1;
  return 0;
}

function getStageState(stageId: number, status: AgentTrayProps['agentStatus']): 'completed' | 'active' | 'idle' {
  const currentIdx = getStageIndex(status.step, status.active);
  if (currentIdx === 0) return 'idle';
  if (currentIdx === 6) return 'completed';
  if (stageId < currentIdx) return 'completed';
  if (stageId === currentIdx) return status.active ? 'active' : 'completed';
  return 'idle';
}

const PipelineGraph: React.FC<{ agentStatus: AgentTrayProps['agentStatus'] }> = ({ agentStatus }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', overflowX: 'auto' }}>
      {PIPELINE_STAGES.map((stage, idx) => {
        const state = getStageState(stage.id, agentStatus);
        const isCompleted = state === 'completed';
        const isActive = state === 'active';

        const bg = isActive
          ? 'rgba(59, 130, 246, 0.25)'
          : isCompleted
          ? 'rgba(16, 185, 129, 0.2)'
          : 'rgba(255, 255, 255, 0.05)';

        const color = isActive
          ? '#60a5fa'
          : isCompleted
          ? '#34d399'
          : 'rgba(255, 255, 255, 0.4)';

        const borderColor = isActive
          ? '#3b82f6'
          : isCompleted
          ? '#10b981'
          : 'rgba(255, 255, 255, 0.1)';

        return (
          <React.Fragment key={stage.id}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem',
                padding: '0.2rem 0.5rem',
                borderRadius: '6px',
                background: bg,
                color: color,
                border: `1px solid ${borderColor}`,
                fontWeight: isActive ? 600 : 400,
                boxShadow: isActive ? '0 0 8px rgba(59, 130, 246, 0.4)' : 'none',
                transition: 'all 0.3s ease',
                whiteSpace: 'nowrap'
              }}
            >
              <span>{isCompleted ? '✓' : isActive ? '⚡' : '○'}</span>
              <span>{stage.label}</span>
            </div>
            {idx < PIPELINE_STAGES.length - 1 && (
              <span style={{ color: isCompleted || isActive ? 'var(--text-muted, #94a3b8)' : 'rgba(255, 255, 255, 0.2)', fontSize: '0.7rem' }}>
                ➔
              </span>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

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

        <PipelineGraph agentStatus={agentStatus} />

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            className="btn btn-outline"
            style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem', borderColor: 'rgba(255,255,255,0.2)' }}
            onClick={async (e) => {
              e.stopPropagation();
              try {
                const res = await fetch('/api/trigger-agents', { method: 'POST' });
                const data = await res.json();
                alert(data.message || 'Agent loop dispatched.');
                fetchAgentStatus();
              } catch (err) {
                alert('Failed to trigger agent.');
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
                {agentLogs || (agentStatus.active ? 'Connecting to agent log stream...' : 'Agent is idle. No logs to stream.')}
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

