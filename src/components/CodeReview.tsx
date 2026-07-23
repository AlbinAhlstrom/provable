import React from 'react';
import DiffViewer from './DiffViewer';
import { Requirement } from '../hooks/useRequirements';

interface CodeReviewProps {
  reviews: any[];
  selectedReviewId: string | null;
  setSelectedReviewId: (id: string | null) => void;
  requirements: Requirement[];
  handleApproveCode: (req: Requirement) => Promise<void>;
  handleProvideFeedback: (req: Requirement) => Promise<void>;
  handleAbandonTicket: (req: Requirement) => Promise<void>;
}

const CodeReview: React.FC<CodeReviewProps> = ({
  reviews,
  selectedReviewId,
  setSelectedReviewId,
  requirements,
  handleApproveCode,
  handleProvideFeedback,
  handleAbandonTicket
}) => {
  if (selectedReviewId === null) {
    return (
      <div className="gerrit-dashboard" style={{ padding: '2rem' }}>
        <div className="gerrit-dashboard-title" style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '1.5rem', color: 'white' }}>Incoming Reviews</div>
        {reviews.length === 0 ? (
          <p className="text-muted" style={{ padding: '2rem', textAlign: 'center', background: 'rgba(255,255,255,0.01)', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>No reviews pending.</p>
        ) : (
          <table className="gerrit-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-glass)', color: 'var(--text-secondary)' }}>
                <th className="gerrit-header-cell" style={{ width: '120px', padding: '0.75rem 1rem', textAlign: 'left' }}>ID</th>
                <th className="gerrit-header-cell" style={{ padding: '0.75rem 1rem', textAlign: 'left' }}>Subject</th>
                <th className="gerrit-header-cell" style={{ width: '120px', padding: '0.75rem 1rem', textAlign: 'left' }}>Status</th>
                <th className="gerrit-header-cell" style={{ width: '120px', padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((req) => (
                <tr key={req.id} className="gerrit-row" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td className="gerrit-cell-mono" style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', color: 'var(--accent-primary)' }}>{req.id}</td>
                  <td className="gerrit-cell" style={{ padding: '0.75rem 1rem', fontWeight: 500 }}>
                    <a 
                      href={`#review-${req.id}`} 
                      onClick={(e) => { e.preventDefault(); setSelectedReviewId(req.id); }}
                      style={{ color: '#f8fafc', textDecoration: 'none' }}
                      onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                      onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
                    >
                      {req.title}
                    </a>
                  </td>
                  <td className="gerrit-cell" style={{ padding: '0.75rem 1rem' }}>
                    <span className={`status-tag status-${req.status.toLowerCase()}`}>{req.status}</span>
                  </td>
                  <td className="gerrit-cell" style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                    <button 
                      className="btn btn-outline" 
                      style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }}
                      onClick={() => setSelectedReviewId(req.id)}
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  }

  const req = requirements.find(r => r.id === selectedReviewId);
  if (!req) return <div style={{ padding: '2rem' }}>Review not found.</div>;

  return (
    <div className="code-review-detail" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%', overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-glass)', paddingBottom: '1rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <button 
              className="btn btn-outline" 
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }} 
              onClick={() => setSelectedReviewId(null)}
            >
              ← Back
            </button>
            <h1 style={{ fontSize: '2.2rem', margin: 0, background: 'linear-gradient(135deg, #fff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Review: {selectedReviewId}
            </h1>
          </div>
          <p className="text-muted" style={{ margin: 0, paddingLeft: '4.8rem' }}>{req.title}</p>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {req.status === 'Conflict' ? (
            <div 
              className="glass-panel" 
              style={{ 
                padding: '0.5rem 1rem', 
                border: '1px solid var(--accent-warning)', 
                background: 'rgba(245, 158, 11, 0.1)', 
                color: 'var(--accent-warning)', 
                borderRadius: '8px', 
                fontWeight: 600,
                fontSize: '0.9rem' 
              }}
            >
              ⚠️ Git Merge Conflict
            </div>
          ) : (
            <>
              <button 
                className="btn btn-outline" 
                style={{ borderColor: 'rgba(239, 68, 68, 0.3)', color: '#ef4444' }}
                onClick={() => handleAbandonTicket(req)}
              >
                Abandon
              </button>
              <button 
                className="btn btn-outline"
                onClick={() => handleProvideFeedback(req)}
              >
                Request Changes
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => handleApproveCode(req)}
              >
                Approve & Merge
              </button>
            </>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1.5rem', flex: 1, minHeight: 0 }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--text-secondary)' }}>Requirement Description</h3>
            <p style={{ margin: 0, lineHeight: 1.6 }}>{req.description}</p>
            
            {req.feedback && (
              <div style={{ marginTop: '0.5rem', padding: '1rem', background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent-warning)', fontSize: '0.9rem' }}>Previous Review Feedback</h4>
                <p style={{ margin: 0, fontSize: '0.9rem', whiteSpace: 'pre-wrap' }}>{req.feedback}</p>
              </div>
            )}
          </div>

          <div style={{ flex: 1, minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: 'var(--text-secondary)' }}>Proposed Code Changes</h3>
            <div style={{ flex: 1, minHeight: 0 }}>
              <DiffViewer ticketId={selectedReviewId} />
            </div>
          </div>
        </div>

        <div style={{ width: '320px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: 'var(--text-secondary)' }}>Test Execution Results</h3>
            {req.tests && req.tests.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                {req.tests.map((test: any, idx: number) => (
                  <div 
                    key={idx} 
                    style={{ 
                      padding: '0.8rem', 
                      background: test.status === 'Passing' ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)', 
                      border: `1px solid ${test.status === 'Passing' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
                      borderRadius: '6px' 
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, fontFamily: 'monospace' }}>{test.name || test.title}</span>
                      <span className={`status-tag status-${test.status.toLowerCase()}`} style={{ fontSize: '0.75rem', padding: '0.1rem 0.4rem' }}>
                        {test.status}
                      </span>
                    </div>
                    {test.failureMessage && (
                      <pre style={{ margin: '0.4rem 0 0 0', padding: '0.5rem', background: 'rgba(0,0,0,0.3)', color: '#f87171', fontSize: '0.75rem', borderRadius: '4px', overflowX: 'auto' }}>
                        {test.failureMessage}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted" style={{ fontSize: '0.9rem', margin: 0 }}>No automated test results attached.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeReview;
