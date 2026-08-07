import React from 'react';
import DiffViewer from './DiffViewer';
import { Requirement } from '../hooks/useRequirements';

interface CodeReviewProps {
  reviews: any[];
  selectedReviewId: string | null;
  setSelectedReviewId: (id: string | null) => void;
  requirements: Requirement[];
  showPreview?: boolean;
  previewBranch?: 'post' | 'pre';
  setPreviewBranch?: (branch: 'post' | 'pre') => void;
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
      <div className="review-empty-state">
        <h2>🔍 Code Review Queue</h2>
        <p>Select a ticket submission from the list to inspect code diffs and test results.</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1.5rem', maxWidth: '600px', margin: '1.5rem auto 0' }}>
          {reviews.map(item => (
            <div key={item.id} onClick={() => setSelectedReviewId(item.id)} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '1rem', cursor: 'pointer', textAlign: 'left' }}>
              <div style={{ fontWeight: 'bold', color: '#60a5fa' }}>{item.id}: {item.title}</div>
              <div style={{ fontSize: '0.85rem', opacity: 0.8, marginTop: '0.25rem' }}>{item.description}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const selectedReq = requirements.find(r => r.id === selectedReviewId);
  const reviewData = reviews.find(r => r.id === selectedReviewId) || selectedReq;

  if (!reviewData) {
    return <div>Review item not found.</div>;
  }

  return (
    <div className="code-review-detail" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <button onClick={() => setSelectedReviewId(null)} style={{ background: '#334155', color: '#fff', border: 'none', padding: '0.4rem 0.8rem', borderRadius: '4px', cursor: 'pointer', marginBottom: '0.5rem' }}>← Back to Review List</button>
          <h2 style={{ margin: 0 }}>[{reviewData.id}] {reviewData.title}</h2>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button onClick={() => handleApproveCode(reviewData)} style={{ background: '#10b981', color: '#fff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>✓ Approve & Merge to Main</button>
          <button onClick={() => handleProvideFeedback(reviewData)} style={{ background: '#f59e0b', color: '#fff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>💬 Provide Feedback</button>
          <button onClick={() => handleAbandonTicket(reviewData)} style={{ background: '#ef4444', color: '#fff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>✗ Reject / Abandon</button>
        </div>
      </div>

      <DiffViewer ticketId={reviewData.id} />
    </div>
  );
};

export default CodeReview;
