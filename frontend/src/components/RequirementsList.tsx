import React, { useState, useEffect } from 'react';
import { Requirement, Priority } from '../hooks/useRequirements';

interface RequirementsListProps {
  requirements: Requirement[];
  selectedReqId: string | null;
  setSelectedReqId: (id: string | null) => void;
  fetchReqs: () => Promise<void>;
  isGeneratingTestCase: boolean;
  generatedTestCode: string | null;
  handleCreateTestCase: (reqId: string) => Promise<void>;
}

const getBadgeClass = (priority: Priority) => {
  switch (priority) {
    case 'High': return 'badge-high';
    case 'Med': return 'badge-med';
    case 'Low': return 'badge-low';
    default: return '';
  }
};

const RequirementsList: React.FC<RequirementsListProps> = ({
  requirements,
  selectedReqId,
  setSelectedReqId,
  fetchReqs,
  isGeneratingTestCase,
  generatedTestCode,
  handleCreateTestCase
}) => {
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const pendingDeleteTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null);

  // Tree state persisted in localStorage
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem('provable_expanded_requirements');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          return new Set(parsed);
        }
      }
    } catch (e) {
      console.error("Failed to load expanded requirements state:", e);
    }
    return new Set(['FLD-CORE']);
  });

  // Persist expandedNodes to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('provable_expanded_requirements', JSON.stringify(Array.from(expandedNodes)));
    } catch (e) {
      console.error("Failed to save expanded requirements state:", e);
    }
  }, [expandedNodes]);
  
  // Creation form state
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newType, setNewType] = useState<'Folder' | 'Requirement'>('Folder');

  // Edit form state
  const [isEditingReq, setIsEditingReq] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editPrio, setEditPrio] = useState<Priority>('Med');

  // Bug report state
  const [isReportingBug, setIsReportingBug] = useState(false);
  const [bugTitle, setBugTitle] = useState('');
  const [bugSteps, setBugSteps] = useState('');
  const [bugExpected, setBugExpected] = useState('');
  const [bugActual, setBugActual] = useState('');

  // Add-child state
  const [isAddingChild, setIsAddingChild] = useState(false);
  const [addChildType, setAddChildType] = useState<'Folder' | 'Requirement'>('Requirement');
  const [addChildTitle, setAddChildTitle] = useState('');
  const [addChildDesc, setAddChildDesc] = useState('');
  const [isSubmittingChild, setIsSubmittingChild] = useState(false);
  const [selectedLayerFilter, setSelectedLayerFilter] = useState<string>('ALL');

  const selectedNode = requirements.find(r => r.id === selectedReqId);
  const childNodes = selectedNode ? requirements.filter(r => r.parentId === selectedNode.id || r.parent_id === selectedNode.id) : [];

  // Initialize edit form when selectedNode changes
  useEffect(() => {
    if (selectedNode) {
      setEditTitle(selectedNode.title);
      setEditDesc(selectedNode.description);
      setEditPrio(selectedNode.priority);
      setIsEditingReq(false);
    }
  }, [selectedReqId, selectedNode]);

  const toggleNode = (id: string) => {
    const next = new Set(expandedNodes);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpandedNodes(next);
  };

  const handleCreateRootReq = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    
    if (newType === 'Requirement') {
      await fetch('/api/create-requirement', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, description: newDesc }) 
      });
    } else {
      const newReq: Requirement = {
        id: `FLD-${Math.floor(Math.random() * 1000)}`,
        title: newTitle,
        description: newDesc,
        priority: 'Med',
        status: 'Backlog',
        tests: [],
        assignedAgents: [],
        assigned_agents: [],
        dependencies: [],
        type: 'Folder',
        parentId: null,
        parent_id: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      const updated = [...requirements, newReq];
      await fetch('/api/requirements', { 
        method: 'POST', 
        body: JSON.stringify(updated), 
        headers: { 'Content-Type': 'application/json' } 
      });
    }

    await fetchReqs();
    setNewTitle('');
    setNewDesc('');
  };

  const handleUpdateReq = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReqId) return;
    
    setIsEditingReq(false);
    await fetch('/api/edit-requirement', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: selectedReqId,
        title: editTitle,
        description: editDesc,
        priority: editPrio
      }) 
    });
    await fetchReqs();
  };

  const handleDeleteReq = async (targetId?: string) => {
    const idToDelete = targetId || selectedReqId;
    if (!idToDelete) return;
    await fetch('/api/delete-requirement', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: idToDelete }) 
    });
    if (selectedReqId === idToDelete) setSelectedReqId(null);
    await fetchReqs();
  };

  const handleDeleteWithConfirmation = (id: string) => {
    if (pendingDeleteId === id) {
      if (pendingDeleteTimer.current) clearTimeout(pendingDeleteTimer.current);
      setPendingDeleteId(null);
      handleDeleteReq(id);
    } else {
      setPendingDeleteId(id);
      if (pendingDeleteTimer.current) clearTimeout(pendingDeleteTimer.current);
      pendingDeleteTimer.current = setTimeout(() => {
        setPendingDeleteId(null);
      }, 3000);
    }
  };

  const handleAddChild = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReqId || !addChildTitle.trim()) return;
    setIsSubmittingChild(true);
    try {
      if (addChildType === 'Folder') {
        await fetch('/api/create-folder', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: addChildTitle, description: addChildDesc, parentId: selectedReqId }),
        });
      } else {
        await fetch('/api/create-requirement', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: addChildTitle, description: addChildDesc, parentId: selectedReqId }),
        });
      }
      setAddChildTitle('');
      setAddChildDesc('');
      setIsAddingChild(false);
      await fetchReqs();
    } finally {
      setIsSubmittingChild(false);
    }
  };

  const handleRemoveChild = async (childId: string) => {
    await fetch(`/api/requirements/${childId}/move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ parentId: null }),
    });
    await fetchReqs();
  };

  const handleReportBug = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReqId || !bugTitle.trim()) return;

    await fetch('/api/report-bug', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: bugTitle,
        parentId: selectedReqId,
        steps: bugSteps,
        expected: bugExpected,
        actual: bugActual
      })
    });
    
    setIsReportingBug(false);
    setBugTitle('');
    setBugSteps('');
    setBugExpected('');
    setBugActual('');
    await fetchReqs();
  };

  const renderTreeNodes = (parentId: string | null = null, depth = 0): React.ReactNode => {
    let nodes = requirements.filter(r => (r.parentId === parentId || r.parent_id === parentId || (!r.parentId && !r.parent_id && parentId === null)));
    if (selectedLayerFilter !== 'ALL' && parentId === null) {
      nodes = nodes.filter(r => (r.layer || 'LOGIC') === selectedLayerFilter || r.type === 'Folder' || r.type === 'Epic');
    }
    if (nodes.length === 0) return null;

    return (
      <div style={{ paddingLeft: depth === 0 ? 0 : '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
        {nodes.map(node => {
          const isFolder = node.type === 'Folder' || node.type === 'Epic';
          const isExpanded = expandedNodes.has(node.id);
          const isSelected = selectedReqId === node.id;
          const hasChildren = requirements.some(r => r.parentId === node.id || r.parent_id === node.id);
          const layerLabel = node.layer === 'PRESENTATION' ? '🎨 UI' : (node.layer === 'INFRASTRUCTURE' ? '💾 API' : '⚡ Logic');
          const layerColor = node.layer === 'PRESENTATION' ? '#38bdf8' : (node.layer === 'INFRASTRUCTURE' ? '#a855f7' : '#f59e0b');

          return (
            <div key={node.id}>
              <div 
                style={{ 
                  display: 'flex', alignItems: 'center', padding: '0.4rem', 
                  background: isSelected ? 'rgba(100, 108, 255, 0.2)' : 'transparent',
                  borderRadius: '4px', cursor: 'pointer',
                  border: isSelected ? '1px solid var(--accent-primary)' : '1px solid transparent'
                }}
                onClick={() => {
                  setSelectedReqId(node.id);
                }}
              >
                <span 
                  onClick={(e) => { e.stopPropagation(); toggleNode(node.id); }}
                  style={{ width: '20px', textAlign: 'center', marginRight: '0.5rem', cursor: 'pointer', opacity: (isFolder || hasChildren) ? 1 : 0 }}
                >
                  {(isFolder || hasChildren) ? (isExpanded ? '▼' : '▶') : '•'}
                </span>
                <span style={{ marginRight: '0.4rem' }}>
                  {isFolder ? '📁' : (node.type === 'Bug' ? '🐛' : (node.type === 'Task' ? '📝' : '📄'))}
                </span>
                <span style={{ flex: 1, fontSize: '0.85rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.title}</span>
                {!isFolder && (
                  <span style={{ fontSize: '0.7rem', padding: '0.1rem 0.35rem', borderRadius: '4px', background: 'rgba(255,255,255,0.06)', color: layerColor, border: `1px solid ${layerColor}44`, marginLeft: '0.3rem' }}>
                    {layerLabel}
                  </span>
                )}
              </div>
              {isExpanded && renderTreeNodes(node.id, depth + 1)}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', gap: '2rem', height: '100%', padding: '2rem' }}>
      {/* Left Pane: Tree Explorer */}
      <div className="glass-panel" style={{ flex: '0 0 320px', overflowY: 'auto', padding: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>3-Layer Explorer</h3>
          <button className="btn btn-primary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => setSelectedReqId(null)}>➕ New</button>
        </div>

        {/* 3-Layer Filter Bar */}
        <div style={{ display: 'flex', gap: '0.3rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
          {[
            { id: 'ALL', label: 'All' },
            { id: 'PRESENTATION', label: '🎨 UI' },
            { id: 'LOGIC', label: '⚡ Logic' },
            { id: 'INFRASTRUCTURE', label: '💾 API' },
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setSelectedLayerFilter(f.id)}
              style={{
                fontSize: '0.75rem',
                padding: '0.2rem 0.5rem',
                borderRadius: '4px',
                border: selectedLayerFilter === f.id ? '1px solid var(--accent-primary)' : '1px solid var(--border-glass)',
                background: selectedLayerFilter === f.id ? 'var(--accent-primary)' : 'rgba(0,0,0,0.2)',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        {renderTreeNodes(null)}
      </div>

      {/* Right Pane: Contextual Content */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {!selectedNode ? (
          <div className="glass-card" style={{ padding: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>Create New Root Item</h2>
            <form onSubmit={handleCreateRootReq} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Type</label>
                <select value={newType} onChange={e => setNewType(e.target.value as 'Folder' | 'Requirement')} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: '#1e293b', color: 'white' }}>
                  <option value="Folder">Folder (Structural)</option>
                  <option value="Requirement">Requirement (Auto-splits into Tasks)</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Title</label>
                <input required value={newTitle} onChange={e => setNewTitle(e.target.value)} type="text" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Description {newType === 'Folder' && '(Optional)'}</label>
                <textarea required={newType === 'Requirement'} value={newDesc} onChange={e => setNewDesc(e.target.value)} rows={4} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
              </div>
              <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>Create Item</button>
            </form>
          </div>
        ) : (
          <>
            {(selectedNode.type === 'Folder' || selectedNode.type === 'Epic') ? (
              // Folder View
              <div className="glass-card" style={{ padding: '2rem' }}>
                {isEditingReq ? (
                  <form onSubmit={handleUpdateReq} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                       <h2 style={{ margin: 0 }}>Edit Folder</h2>
                       <div style={{ display: 'flex', gap: '1rem' }}>
                          <button type="submit" className="btn btn-primary">Save Changes</button>
                          <button type="button" className="btn btn-outline" onClick={() => setIsEditingReq(false)}>Cancel</button>
                       </div>
                    </div>
                    
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Title</label>
                      <input required value={editTitle} onChange={e => setEditTitle(e.target.value)} type="text" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', fontSize: '1.2rem' }} />
                    </div>
                    
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Description</label>
                      <textarea value={editDesc} onChange={e => setEditDesc(e.target.value)} rows={4} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
                    </div>
                  </form>
                ) : (
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
                      <h2 style={{ margin: 0 }}>📁 {selectedNode.title}</h2>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => setIsEditingReq(true)}>✏️ Edit</button>
                        <button
                          className="btn btn-outline"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)', transition: 'background 0.15s', ...(pendingDeleteId === selectedNode.id ? { background: 'var(--accent-danger)', color: '#fff' } : {}) }}
                          onClick={() => handleDeleteWithConfirmation(selectedNode.id)}
                        >
                          {pendingDeleteId === selectedNode.id ? '⚠️ Confirm Delete' : '🗑️ Delete'}
                        </button>
                      </div>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{selectedNode.description || 'No description provided.'}</p>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                      <h3 style={{ margin: 0 }}>Nested Items</h3>
                      <button
                        className="btn btn-primary"
                        style={{ padding: '0.3rem 0.7rem', fontSize: '0.8rem' }}
                        onClick={() => { setIsAddingChild(v => !v); setAddChildTitle(''); setAddChildDesc(''); }}
                      >
                        {isAddingChild ? '✕ Cancel' : '➕ Add Child'}
                      </button>
                    </div>

                    {isAddingChild && (
                      <form onSubmit={handleAddChild} style={{ background: 'rgba(0,0,0,0.25)', border: '1px solid var(--border-glass)', borderRadius: '8px', padding: '1rem', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button type="button" onClick={() => setAddChildType('Requirement')} className={`btn ${addChildType === 'Requirement' ? 'btn-primary' : 'btn-outline'}`} style={{ flex: 1, fontSize: '0.8rem', padding: '0.3rem' }}>📄 Requirement</button>
                          <button type="button" onClick={() => setAddChildType('Folder')} className={`btn ${addChildType === 'Folder' ? 'btn-primary' : 'btn-outline'}`} style={{ flex: 1, fontSize: '0.8rem', padding: '0.3rem' }}>📁 Sub-Folder</button>
                        </div>
                        <input
                          required
                          value={addChildTitle}
                          onChange={e => setAddChildTitle(e.target.value)}
                          placeholder={addChildType === 'Folder' ? 'Folder name...' : 'Requirement title...'}
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', boxSizing: 'border-box' }}
                        />
                        <textarea
                          value={addChildDesc}
                          onChange={e => setAddChildDesc(e.target.value)}
                          placeholder="Description (optional for folders, required for requirements)..."
                          required={addChildType === 'Requirement'}
                          rows={3}
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical', boxSizing: 'border-box' }}
                        />
                        <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start', fontSize: '0.85rem' }} disabled={isSubmittingChild}>
                          {isSubmittingChild ? 'Creating...' : `Create ${addChildType}`}
                        </button>
                      </form>
                    )}

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {childNodes.map(child => (
                        <div key={child.id} className="glass-card" style={{ padding: '0.75rem 1rem', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: 0 }} onClick={() => setSelectedReqId(child.id)}>
                            <span>{child.type === 'Folder' ? '📁' : (child.type === 'Bug' ? '🐛' : '📄')}</span>
                            <strong style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{child.id}: {child.title}</strong>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
                            <span className={`badge ${getBadgeClass(child.priority)}`}>{child.priority}</span>
                            <button
                              className="btn btn-outline"
                              title="Remove from this folder (moves to root)"
                              style={{ padding: '0.15rem 0.4rem', fontSize: '0.75rem', borderColor: 'rgba(255,255,255,0.2)', color: 'var(--text-muted)' }}
                              onClick={e => { e.stopPropagation(); handleRemoveChild(child.id); }}
                            >✕</button>
                          </div>
                        </div>
                      ))}
                      {childNodes.length === 0 && !isAddingChild && <p className="text-muted">This folder is empty. Add a child above.</p>}
                    </div>
                  </>
                )}
              </div>
            ) : (
              // Requirement/Task/Bug detail view
              <div className="glass-card" style={{ padding: '2rem' }}>
                {isEditingReq ? (
                  <form onSubmit={handleUpdateReq} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                       <h2 style={{ margin: 0 }}>Edit Specification</h2>
                       <div style={{ display: 'flex', gap: '1rem' }}>
                          <button type="submit" className="btn btn-primary">Save Changes</button>
                          <button type="button" className="btn btn-outline" onClick={() => setIsEditingReq(false)}>Cancel</button>
                       </div>
                    </div>
                    
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Title</label>
                      <input required value={editTitle} onChange={e => setEditTitle(e.target.value)} type="text" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', fontSize: '1.2rem' }} />
                    </div>
                    
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <div style={{ flex: 1 }}>
                        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Priority</label>
                        <select value={editPrio} onChange={e => setEditPrio(e.target.value as Priority)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: '#1e293b', color: 'white' }}>
                          <option value="High">High</option>
                          <option value="Med">Medium</option>
                          <option value="Low">Low</option>
                        </select>
                      </div>
                    </div>
                    
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Description</label>
                      <textarea required value={editDesc} onChange={e => setEditDesc(e.target.value)} rows={6} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
                    </div>
                  </form>
                ) : (
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{ fontSize: '1.5rem' }}>{selectedNode.type === 'Bug' ? '🐛' : '📄'}</span>
                        <h2 style={{ margin: 0 }}>{selectedNode.title}</h2>
                        <span className={`badge ${getBadgeClass(selectedNode.priority)}`}>{selectedNode.priority}</span>
                      </div>
                      
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {selectedNode.type === 'Requirement' && (
                          <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', borderColor: 'var(--accent-warning)', color: 'var(--accent-warning)' }} onClick={() => setIsReportingBug(true)}>
                            🐛 Report Bug
                          </button>
                        )}
                        {selectedNode.type === 'Requirement' && (!selectedNode.tests || selectedNode.tests.length === 0) && (
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', borderColor: 'var(--accent-success)', color: 'var(--accent-success)' }} 
                            onClick={() => handleCreateTestCase(selectedNode.id)}
                            disabled={isGeneratingTestCase}
                          >
                            {isGeneratingTestCase ? '🧪 Generating...' : '🧪 Create Test Case'}
                          </button>
                        )}
                        <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => setIsEditingReq(true)}>✏️ Edit</button>
                        <button
                          className="btn btn-outline"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)', transition: 'background 0.15s', ...(pendingDeleteId === selectedNode.id ? { background: 'var(--accent-danger)', color: '#fff' } : {}) }}
                          onClick={() => handleDeleteWithConfirmation(selectedNode.id)}
                        >
                          {pendingDeleteId === selectedNode.id ? '⚠️ Confirm Delete' : '🗑️ Delete'}
                        </button>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', marginTop: '0.5rem' }}>
                       <span className="text-muted" style={{ fontSize: '0.85rem' }}>ID: {selectedNode.id}</span>
                       <span className="text-muted" style={{ fontSize: '0.85rem' }}>Status: {selectedNode.status}</span>
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Description</label>
                      <div style={{ padding: '1rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', minHeight: '150px' }}>
                        <textarea value={selectedNode.description} readOnly style={{ width: '100%', height: '100%', minHeight: '130px', background: 'transparent', border: 'none', color: 'white', resize: 'vertical', outline: 'none' }} />
                      </div>
                    </div>

                    {/* Linked Test Cases */}
                    {selectedNode.tests && selectedNode.tests.length > 0 && (
                      <div style={{ marginTop: '1.5rem' }}>
                        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Linked Test Cases</label>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {selectedNode.tests.map((test: any, idx: number) => (
                            <div key={idx} style={{ padding: '0.8rem', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'white' }}>{test.name || test.title}</h4>
                                <span className="badge" style={{ fontSize: '0.75rem', background: test.status === 'Passing' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)', color: test.status === 'Passing' ? 'var(--accent-success)' : 'var(--accent-danger)' }}>
                                  {test.status}
                                </span>
                              </div>
                              {test.given && (
                                <div style={{ fontSize: '0.85rem', marginTop: '0.4rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                                  <strong>Given:</strong> {test.given} <br/>
                                  <strong>When:</strong> {test.when} <br/>
                                  <strong>Then:</strong> {test.then}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Generated Code Preview */}
                    {generatedTestCode && (
                      <div style={{ marginTop: '1.5rem' }}>
                        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Generated Test Code</label>
                        <pre style={{ padding: '1rem', background: '#1e293b', border: '1px solid var(--border-glass)', borderRadius: '4px', overflowX: 'auto', fontSize: '0.85rem', maxHeight: '300px' }}>
                          <code style={{ color: '#38bdf8' }}>{generatedTestCode}</code>
                        </pre>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Report Bug Modal */}
      {isReportingBug && selectedNode && (
        <div className="modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-panel" style={{ width: '550px', padding: '2rem', borderRadius: '12px', border: '1px solid var(--border-glass)', background: 'var(--bg-secondary)', position: 'relative' }}>
            <h2 style={{ marginBottom: '1.5rem' }}>🐛 Report Bug for Requirement</h2>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-glass)' }}>
              <strong>Requirement:</strong> {selectedNode.title}
            </div>
            <form onSubmit={handleReportBug} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Bug Title</label>
                <input required value={bugTitle} onChange={e => setBugTitle(e.target.value)} type="text" placeholder="e.g., Header text overlaps logo" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Steps to Reproduce</label>
                <textarea required value={bugSteps} onChange={e => setBugSteps(e.target.value)} rows={3} placeholder="1. Go to page X&#10;2. Click on Z&#10;3. See error" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Expected Behavior</label>
                <textarea required value={bugExpected} onChange={e => setBugExpected(e.target.value)} rows={2} placeholder="Header should align to the center with adequate padding" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Actual Behavior</label>
                <textarea required value={bugActual} onChange={e => setBugActual(e.target.value)} rows={2} placeholder="Header overlaps and overflows on smaller screen widths" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button type="submit" className="btn btn-primary">Submit Bug Report</button>
                <button type="button" className="btn btn-outline" onClick={() => setIsReportingBug(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default RequirementsList;
