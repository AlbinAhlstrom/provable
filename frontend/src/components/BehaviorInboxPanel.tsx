import React, { useState, useEffect } from 'react';

export interface BusinessSpecItem {
  spec_id: string;
  title: string;
  description: string;
  given_when_then: string;
  target_aggregate: string;
  is_mathematical_boundary?: boolean;
  priority: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'FULFILLED' | 'REQUIRES_HUMAN_INTERVENTION';
}

export const BehaviorInboxPanel: React.FC = () => {
  const [specs, setSpecs] = useState<BusinessSpecItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newGivenWhenThen, setNewGivenWhenThen] = useState('');
  const [newAggregate, setNewAggregate] = useState('Order');
  const [isMathBoundary, setIsMathBoundary] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  const fetchSpecs = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/specs/inbox');
      if (res.ok) {
        const data = await res.json();
        setSpecs(data);
      }
    } catch (e) {
      console.error('Failed to fetch specs:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSpecs();
  }, []);

  const handleAddSpec = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      const payload = {
        title: newTitle.trim(),
        description: newDescription.trim() || newTitle.trim(),
        given_when_then: newGivenWhenThen.trim() || 'Given preconditions When action Then result',
        target_aggregate: newAggregate.trim() || 'Order',
        is_mathematical_boundary: isMathBoundary,
        priority: 'High'
      };

      const res = await fetch('http://localhost:8000/api/specs/inbox/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setNewTitle('');
        setNewDescription('');
        setNewGivenWhenThen('');
        setIsMathBoundary(false);
        setShowAddForm(false);
        fetchSpecs();
      }
    } catch (e) {
      console.error('Failed to add spec:', e);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'FULFILLED':
        return <span style={{ background: '#059669', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>🟢 FULFILLED</span>;
      case 'IN_PROGRESS':
        return <span style={{ background: '#d97706', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>⚡ TDD RUNNING</span>;
      case 'REQUIRES_HUMAN_INTERVENTION':
        return <span style={{ background: '#dc2626', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>🔴 NEEDS REVIEW</span>;
      default:
        return <span style={{ background: '#475569', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>⏳ PENDING</span>;
    }
  };

  return (
    <div style={{ background: '#1e293b', borderRadius: '8px', padding: '16px', color: '#f8fafc', border: '1px solid #334155' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            📥 Behavior Specs Inbox
            <span style={{ fontSize: '12px', background: '#3b82f6', color: '#fff', padding: '2px 6px', borderRadius: '12px' }}>
              {specs.length}
            </span>
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#94a3b8' }}>
            Atomic business rules driving the deterministic Red-Gate TDD machine.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            style={{ background: '#0284c7', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: 600 }}
          >
            {showAddForm ? '✕ Close' : '➕ Add Spec (CRUD)'}
          </button>
          <button
            onClick={fetchSpecs}
            disabled={loading}
            style={{ background: '#334155', color: '#f8fafc', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddSpec} style={{ background: '#0f172a', padding: '14px', borderRadius: '6px', border: '1px solid #3b82f6', marginBottom: '16px' }}>
          <h4 style={{ margin: '0 0 10px', fontSize: '13px', color: '#38bdf8' }}>Define New Business Specification (No Free-Text Prompting)</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
            <div>
              <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Rule Title</label>
              <input
                type="text"
                placeholder="e.g. Enforce 10% Discount for Loyalty Members"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                required
                style={{ width: '100%', background: '#1e293b', border: '1px solid #475569', color: '#fff', padding: '6px 8px', borderRadius: '4px', fontSize: '12px' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Aggregate Root</label>
              <input
                type="text"
                placeholder="e.g. Pallet or Zone"
                value={newAggregate}
                onChange={(e) => setNewAggregate(e.target.value)}
                required
                style={{ width: '100%', background: '#1e293b', border: '1px solid #475569', color: '#fff', padding: '6px 8px', borderRadius: '4px', fontSize: '12px' }}
              />
            </div>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ fontSize: '11px', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Given / When / Then Specification</label>
            <input
              type="text"
              placeholder="Given customer has loyalty points When placing order Then total is reduced by 10%"
              value={newGivenWhenThen}
              onChange={(e) => setNewGivenWhenThen(e.target.value)}
              style={{ width: '100%', background: '#1e293b', border: '1px solid #475569', color: '#fff', padding: '6px 8px', borderRadius: '4px', fontSize: '12px' }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#cbd5e1', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={isMathBoundary}
                onChange={(e) => setIsMathBoundary(e.target.checked)}
              />
              📐 Mathematical / Capacity Boundary Rule (Triggers Hypothesis)
            </label>
            <button
              type="submit"
              style={{ background: '#10b981', color: '#fff', border: 'none', padding: '6px 14px', borderRadius: '4px', cursor: 'pointer', fontWeight: 600, fontSize: '12px' }}
            >
              Save Specification
            </button>
          </div>
        </form>
      )}

      {specs.length === 0 ? (
        <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
          No pending specifications in inbox. Create one above or discover from pitch.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {specs.map((spec) => (
            <div
              key={spec.spec_id}
              style={{
                background: '#0f172a',
                padding: '12px 14px',
                borderRadius: '6px',
                border: '1px solid #334155',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: '12px'
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ fontFamily: 'monospace', fontSize: '11px', color: '#38bdf8', fontWeight: 600 }}>
                    {spec.spec_id}
                  </span>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#f1f5f9' }}>
                    {spec.title}
                  </span>
                  {spec.is_mathematical_boundary && (
                    <span style={{ fontSize: '10px', background: '#7c3aed', color: '#fff', padding: '1px 5px', borderRadius: '3px' }}>
                      Hypothesis
                    </span>
                  )}
                  <span style={{ fontSize: '11px', background: '#1e293b', color: '#94a3b8', padding: '1px 6px', borderRadius: '4px', border: '1px solid #475569' }}>
                    📦 {spec.target_aggregate}
                  </span>
                </div>
                <p style={{ margin: '0 0 6px', fontSize: '12px', color: '#cbd5e1' }}>
                  {spec.description}
                </p>
                <div style={{ fontSize: '11px', color: '#a5f3fc', background: '#164e63', padding: '4px 8px', borderRadius: '4px', fontFamily: 'monospace' }}>
                  {spec.given_when_then}
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
                {getStatusBadge(spec.status)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BehaviorInboxPanel;
