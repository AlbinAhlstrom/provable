import React from 'react';
import DiffViewer from './DiffViewer';
import { Requirement } from '../hooks/useRequirements';

interface CodeReviewProps {
  reviews: any[];
  selectedReviewId: string | null;
  setSelectedReviewId: (id: string | null) => void;
  requirements: Requirement[];
  showPreview: boolean;
  previewBranch: 'pre' | 'post';
  setPreviewBranch: (branch: 'pre' | 'post') => void;
  handleApproveCode: (req: Requirement) => Promise<void>;
  handleProvideFeedback: (req: Requirement) => Promise<void>;
  handleAbandonTicket: (req: Requirement) => Promise<void>;
}

const CodeReview: React.FC<CodeReviewProps> = ({
  reviews,
  selectedReviewId,
  setSelectedReviewId,
  requirements,
  showPreview,
  previewBranch,
  setPreviewBranch,
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
                <th className="gerrit-header-cell" style={{ width: '100px', padding: '0.75rem 1rem', textAlign: 'left' }}>Size</th>
                <th className="gerrit-header-cell" style={{ width: '120px', padding: '0.75rem 1rem', textAlign: 'left' }}>Wait Time</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map(review => (
                <tr 
                  key={review.id} 
                  className="gerrit-row"
                  onClick={() => setSelectedReviewId(review.id)}
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', cursor: 'pointer', background: 'rgba(255,255,255,0.01)' }}
                >
                  <td className="gerrit-cell" style={{ fontFamily: 'monospace', padding: '1rem' }}>{review.id}</td>
                  <td className="gerrit-cell gerrit-subject" style={{ padding: '1rem', color: 'white' }}>
                    {review.title}
                    {review.status === 'Conflict' && (
                      <span className="badge" style={{ marginLeft: '0.5rem', background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                        ⚠️ Conflict (Resolving...)
                      </span>
                    )}
                  </td>
                  <td className="gerrit-cell" style={{ padding: '1rem' }}>
                    <span className={`gerrit-size-badge gerrit-size-${review.size.toLowerCase()}`}>
                      {review.size}
                    </span>
                  </td>
                  <td className="gerrit-cell" style={{ color: 'var(--text-muted)', padding: '1rem' }}>
                    {review.waitingTime}
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
  if (!req) {
    return (
      <div style={{ padding: '2rem' }}>
        <button className="btn btn-outline" onClick={() => setSelectedReviewId(null)}>
          ← Back to Dashboard
        </button>
        <p className="text-muted" style={{ marginTop: '1rem' }}>Review not found.</p>
      </div>
    );
  }

  return (
    <div className="gerrit-detail-container" style={{ padding: '2rem' }}>
      <header className="header" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <button 
              className="btn btn-outline" 
              style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }} 
              onClick={() => {
                setSelectedReviewId(null);
                if (previewBranch === 'pre') {
                  setPreviewBranch('post');
                  fetch('/api/checkout-preview', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ branch: 'main' })
                  });
                }
              }}
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
          {showPreview && (
            <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '3px', border: '1px solid var(--border-glass)' }}>
              <button
                className={`btn ${previewBranch === 'pre' ? 'btn-primary' : ''}`}
                style={{ padding: '0.3rem 0.8rem', fontSize: '0.8rem', borderRadius: '6px', background: previewBranch === 'pre' ? undefined : 'transparent', color: previewBranch === 'pre' ? undefined : 'var(--text-secondary)', border: 'none' }}
                onClick={async () => {
                  if (previewBranch === 'pre') return;
                  setPreviewBranch('pre');
                  await fetch('/api/checkout-preview', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ branch: 'main' })
                  });
                }}
                title="Preview before this commit (main branch)"
              >
                Before
              </button>
              <button
                className={`btn ${previewBranch === 'post' ? 'btn-primary' : ''}`}
                style={{ padding: '0.3rem 0.8rem', fontSize: '0.8rem', borderRadius: '6px', background: previewBranch === 'post' ? undefined : 'transparent', color: previewBranch === 'post' ? undefined : 'var(--text-secondary)', border: 'none' }}
                onClick={async () => {
                  if (previewBranch === 'post') return;
                  setPreviewBranch('post');
                  await fetch('/api/checkout-preview', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ branch: `ticket/${selectedReviewId}` })
                  });
                }}
                title="Preview after this commit (branch)"
              >
                After
              </button>
            </div>
          )}

          {req.status === 'Conflict' ? (
            <div 
              className="glass-panel" 
              style={{ 
                padding: '0.5rem 1rem', 
                border: '1px solid var(--accent-warning)', 
                background: 'rgba(245, 158, 11, 0.1)', 
                borderRadius: '6px', 
                color: '#fbbf24', 
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <div className="spinner-small" style={{ border: '2px solid rgba(255,255,255,0.1)', borderTopColor: '#fbbf24', borderRadius: '50%', width: '14px', height: '14px', animation: 'spin 1s linear infinite' }}></div>
              <span>Merge conflict detected. Automated agent is resolving...</span>
            </div>
          ) : req.status === 'InProgress' ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div 
                className="glass-panel" 
                style={{ 
                  padding: '0.5rem 1rem', 
                  border: '1px solid var(--accent-primary)', 
                  background: 'rgba(59, 130, 246, 0.1)', 
                  borderRadius: '6px', 
                  color: '#60a5fa', 
                  fontSize: '0.9rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <div className="spinner-small" style={{ border: '2px solid rgba(255,255,255,0.1)', borderTopColor: '#60a5fa', borderRadius: '50%', width: '14px', height: '14px', animation: 'spin 1s linear infinite' }}></div>
                <span>Agent is actively reworking this ticket...</span>
              </div>
              <button 
                className="btn btn-outline" 
                style={{ borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)' }} 
                onClick={() => handleAbandonTicket(req)}
              >
                Abandon
              </button>
            </div>
          ) : req.status === 'Backlog' ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div 
                className="glass-panel" 
                style={{ 
                  padding: '0.5rem 1rem', 
                  border: '1px solid var(--text-muted)', 
                  background: 'rgba(255, 255, 255, 0.05)', 
                  borderRadius: '6px', 
                  color: 'var(--text-muted)', 
                  fontSize: '0.9rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                <span>⌛ Waiting for agent to start reworking...</span>
              </div>
              <button 
                className="btn btn-outline" 
                style={{ borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)' }} 
                onClick={() => handleAbandonTicket(req)}
              >
                Abandon
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-primary" onClick={() => handleApproveCode(req)}>
                Approve (Merge)
              </button>
              <button 
                className="btn btn-outline" 
                onClick={() => handleProvideFeedback(req)}
              >
                Feedback
              </button>
              <button 
                className="btn btn-outline" 
                style={{ borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)' }} 
                onClick={() => handleAbandonTicket(req)}
              >
                Abandon
              </button>
            </div>
          )}
        </div>
      </header>

      {req.feedback && (
        <div 
          style={{ 
            padding: '0.8rem 1rem', 
            border: '1px solid var(--accent-danger)', 
            background: 'rgba(239, 68, 68, 0.1)', 
            borderRadius: '6px', 
            color: '#f87171', 
            fontSize: '0.9rem',
            marginBottom: '1.5rem'
          }}
        >
          <strong>⚠️ Merge Warning:</strong> {req.feedback}
        </div>
      )}
      
      <DiffViewer ticketId={req.id} />
    </div>
  );
};

export default CodeReview;
