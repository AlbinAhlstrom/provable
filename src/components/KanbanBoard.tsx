import React from 'react';
import { Requirement, Priority, KanbanStatus } from '../hooks/useRequirements';

interface KanbanBoardProps {
  requirements: Requirement[];
  agentLogs: string;
  agentStatus: {
    active: boolean;
    ticket_id: string | null;
    step: string;
    attempt: number;
    max_attempts: number;
    last_update: string;
  };
  fetchReqs: () => Promise<void>;
}

const getBadgeClass = (priority: Priority) => {
  switch (priority) {
    case 'High': return 'badge-high';
    case 'Med': return 'badge-med';
    case 'Low': return 'badge-low';
    default: return '';
  }
};

const columns: { id: KanbanStatus; title: string }[] = [
  { id: 'Backlog', title: 'Backlog (Pending)' },
  { id: 'InProgress', title: 'In Progress' },
  { id: 'Review', title: 'Review / Blocked' },
  { id: 'Done', title: 'Done (Merged)' },
];

const KanbanBoard: React.FC<KanbanBoardProps> = ({
  requirements,
  agentLogs,
  agentStatus,
  fetchReqs
}) => {
  const inProgressReqs = requirements.filter(r => r.status === 'InProgress');

  const handleTriggerAgent = async (ticketId: string) => {
    try {
      const res = await fetch(`/api/trigger-ticket/${ticketId}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await fetchReqs();
      } else {
        alert(`Failed to trigger agent: ${data.error || data.message || 'Unknown error'}`);
      }
    } catch (err) {
      console.error(err);
      alert("Network error occurred while triggering the agent.");
    }
  };

  return (
    <section className="kanban-board" style={{ padding: '2rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', width: '100%' }}>
        {agentStatus?.active && (
          <div className="active-agent-banner" style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid var(--accent-primary)', padding: '1rem', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%', minHeight: '500px', boxSizing: 'border-box' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div className="spinner" style={{ border: '3px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-primary)', borderRadius: '50%', width: '20px', height: '20px', animation: 'spin 1s linear infinite' }}></div>
              <div>
                <div style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>Agent Active</div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Working on {inProgressReqs.map(r => r.id).join(', ')}...</div>
              </div>
            </div>
            <div className="agent-terminal" style={{ background: '#0d1117', padding: '0.8rem', borderRadius: '4px', border: '1px solid #30363d', flex: 1, overflowY: 'auto' }}>
              <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.75rem', color: '#c9d1d9', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                {agentLogs || "Connecting to agent console..."}
              </pre>
            </div>
          </div>
        )}
        {columns.map(col => {
          const columnReqs = requirements.filter(r => {
            if (col.id === 'Review') {
              return (r.status === 'Review' || r.status === 'Conflict') && r.type !== 'Requirement' && r.type !== 'Folder' && r.type !== 'Epic';
            }
            return r.status === col.id && r.type !== 'Requirement' && r.type !== 'Folder' && r.type !== 'Epic';
          });
          return (
            <div key={col.id} className="kanban-column" style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-glass)', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem', minHeight: '500px' }}>
              <div className="kanban-column-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
                <span style={{ fontWeight: 'bold', color: 'white' }}>{col.title}</span>
                <span className="badge" style={{ background: 'rgba(255,255,255,0.05)' }}>{columnReqs.length}</span>
              </div>
              <div className="kanban-column-content" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: 1, overflowY: 'auto' }}>
                {columnReqs.map(req => {
                  const passingTests = req.tests?.filter(t => t.status === 'Passing').length || 0;
                  const totalTests = req.tests?.length || 0;
                  const isBug = req.type === 'Bug';
                  return (
                    <div key={req.id} className={`kanban-card ${isBug ? 'kanban-card-bug' : ''}`} style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '6px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', position: 'relative' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="text-muted" style={{ fontSize: '0.75rem' }}>{req.id}</span>
                        <span className={`badge ${isBug ? 'badge-bug' : getBadgeClass(req.priority)}`}>
                          {isBug ? 'Bug' : req.priority}
                        </span>
                      </div>
                      <h4 className="card-title" style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, color: 'white' }}>{req.title}</h4>
                      {req.status === 'Conflict' && (
                        <div className="kanban-card-conflict-badge" style={{ color: '#fbbf24', fontSize: '0.75rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          ⚠️ Conflict (Resolving...)
                        </div>
                      )}
                      <div className="card-meta" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{passingTests}/{totalTests} Tests</span>
                        <div style={{ display: 'flex', gap: '0.2rem' }}>
                          {req.assignedAgents?.map(agent => (
                            <div key={agent} title={agent} style={{ width: '20px', height: '20px', borderRadius: '50%', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 'bold', color: 'white' }}>
                              {agent.charAt(0)}
                            </div>
                          ))}
                        </div>
                      </div>
                      {req.status === 'Backlog' && (
                        <button 
                          className="btn btn-outline" 
                          style={{ marginTop: '0.5rem', width: '100%', fontSize: '0.75rem', padding: '0.25rem 0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem' }}
                          onClick={() => handleTriggerAgent(req.id)}
                        >
                          ⚡ Trigger Agent (Temp)
                        </button>
                      )}
                    </div>
                  );
                })}
                {columnReqs.length === 0 && (
                  <div style={{ margin: 'auto', fontSize: '0.8rem', color: 'var(--text-muted)' }}>No items</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default KanbanBoard;
