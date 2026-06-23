import React, { useState, useEffect } from 'react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-json';

// Types
export type Priority = 'High' | 'Med' | 'Low';
export type TestStatus = 'Passing' | 'Failing' | 'Pending';
export type AgentRole = 'Frontend' | 'Backend' | 'Tester' | 'Coordinator';
export type KanbanStatus = 'Backlog' | 'InProgress' | 'Review' | 'Test' | 'Done' | 'Conflict';

export interface Test { 
  id: string; 
  description: string; 
  status: TestStatus; 
  name?: string;
  title?: string;
  req?: string;
  given?: string;
  when?: string;
  then?: string;
}
export interface Requirement { 
  id: string; 
  title: string; 
  description: string; 
  priority: Priority; 
  status: KanbanStatus; 
  tests: Test[]; 
  assignedAgents: AgentRole[]; 
  proposedCode?: string;
  feedback?: string;
  parentId?: string;
  type?: 'Folder' | 'Epic' | 'Requirement' | 'Task' | 'Bug';
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

export const AGENT_ORDER: AgentRole[] = ['Frontend', 'Backend', 'Tester'];

interface DiffLineHalf {
  lineNum: number | null;
  content: string | null;
}

interface DiffRowPairData {
  type: 'equal' | 'insert' | 'delete' | 'replace';
  left: DiffLineHalf | null;
  right: DiffLineHalf | null;
}

interface DiffFileData {
  filename: string;
  status: 'modified' | 'added' | 'deleted';
  rowPairs: DiffRowPairData[];
  isVirtualTests?: boolean;
}

const getLanguage = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'ts':
    case 'tsx':
      return 'tsx';
    case 'js':
    case 'jsx':
      return 'jsx';
    case 'py':
      return 'python';
    case 'css':
      return 'css';
    case 'json':
      return 'json';
    case 'html':
      return 'markup';
    default:
      return 'javascript';
  }
};

const highlightCode = (content: string | null, lang: string) => {
  if (content === null) return ' ';
  try {
    const grammar = Prism.languages[lang] || Prism.languages.javascript;
    const html = Prism.highlight(content, grammar, lang);
    return <span dangerouslySetInnerHTML={{ __html: html }} />;
  } catch (e) {
    return content;
  }
};

const DiffViewer = ({ ticketId }: { ticketId: string }) => {
  const [diffFiles, setDiffFiles] = useState<DiffFileData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFiles, setExpandedFiles] = useState<Record<string, boolean>>({});
  const [visibleLines, setVisibleLines] = useState<Record<string, boolean[]>>({});

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/diff-files/${ticketId}`)
      .then(res => res.json())
      .then((data: { files?: DiffFileData[]; error?: string }) => {
        if (data.error) {
          setError(data.error);
          setLoading(false);
          return;
        }
        const filesData = data.files || [];
        setDiffFiles(filesData);

        const initialVisible: Record<string, boolean[]> = {};

        filesData.forEach((file) => {
          const pairs = file.rowPairs || [];
          const visibility = pairs.map((pair, pairIdx) => {
            if (pair.type !== 'equal') return true;
            
            for (let offset = -10; offset <= 10; offset++) {
              const checkIdx = pairIdx + offset;
              if (checkIdx >= 0 && checkIdx < pairs.length) {
                if (pairs[checkIdx].type !== 'equal') return true;
              }
            }
            return false;
          });
          initialVisible[file.filename] = visibility;
        });

        setVisibleLines(initialVisible);
        setExpandedFiles({}); // Reset expanded states on ticket change
        setLoading(false);
      })
      .catch(e => {
        setError(String(e));
        setLoading(false);
      });
  }, [ticketId]);

  const toggleFileExpand = (filename: string) => {
    setExpandedFiles(prev => {
      const isCurrentlyExpanded = prev[filename] !== undefined
        ? prev[filename]
        : diffFiles.findIndex(f => f.filename === filename) === 0;
      return { ...prev, [filename]: !isCurrentlyExpanded };
    });
  };

  const expandLines = (filename: string, start: number, end: number) => {
    setVisibleLines(prev => {
      const current = prev[filename] ? [...prev[filename]] : [];
      for (let i = start; i <= end; i++) {
        current[i] = true;
      }
      return { ...prev, [filename]: current };
    });
  };

  if (loading) {
    return <div className="text-muted" style={{ padding: '1rem' }}>Loading code diffs...</div>;
  }

  if (error) {
    return (
      <div style={{ color: 'var(--accent-danger)', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '6px', border: '1px solid var(--accent-danger)' }}>
        Error loading diff: {error}
      </div>
    );
  }

  if (diffFiles.length === 0) {
    return <div className="text-muted" style={{ padding: '1rem' }}>No code changes found.</div>;
  }

  return (
    <div className="diff-container" style={{ marginBottom: '1.5rem' }}>
      {diffFiles.map(file => {
        const isExpanded = expandedFiles[file.filename] !== undefined
          ? expandedFiles[file.filename]
          : diffFiles.findIndex(f => f.filename === file.filename) === 0;
        const rowPairs = file.rowPairs || [];
        const visibility = visibleLines[file.filename] || [];
        const lang = getLanguage(file.filename);

        const insertions = rowPairs.filter(p => (p.type === 'insert' || p.type === 'replace') && p.right !== null).length;
        const deletions = rowPairs.filter(p => (p.type === 'delete' || p.type === 'replace') && p.left !== null).length;

        const getStatusBadge = () => {
          switch (file.status) {
            case 'added':
              return <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#4ade80', border: '1px solid #10b981' }}>Added</span>;
            case 'deleted':
              return <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid #ef4444' }}>Deleted</span>;
            default:
              return <span className="badge" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', border: '1px solid #6366f1' }}>Modified</span>;
          }
        };

        return (
          <div key={file.filename} className={`diff-file-section ${isExpanded ? 'expanded' : ''}`}>
            <div className="diff-file-bar" onClick={() => toggleFileExpand(file.filename)}>
              <div className="diff-file-info">
                <span className="diff-file-toggle">{isExpanded ? '▼' : '▶'}</span>
                <span className="diff-file-name">{file.filename}</span>
                {getStatusBadge()}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', fontSize: '0.85rem' }}>
                {insertions > 0 && <span style={{ color: '#4ade80', fontWeight: 'bold' }}>+{insertions}</span>}
                {deletions > 0 && <span style={{ color: '#f87171', fontWeight: 'bold' }}>-{deletions}</span>}
              </div>
            </div>

            {isExpanded && (
              <div className="diff-table-wrapper">
                <table className="diff-table">
                  <tbody>
                    {(() => {
                      const rows: React.ReactNode[] = [];
                      for (let i = 0; i < rowPairs.length; i++) {
                        if (visibility[i]) {
                          const pair = rowPairs[i];
                          const left = pair.left;
                          const right = pair.right;

                          let leftClass = 'diff-cell-equal';
                          if (pair.type === 'delete' || pair.type === 'replace') {
                            if (left) leftClass = 'diff-cell-delete';
                          }
                          
                          let rightClass = 'diff-cell-equal';
                          if (pair.type === 'insert' || pair.type === 'replace') {
                            if (right) rightClass = 'diff-cell-insert';
                          }

                          rows.push(
                            <tr key={i} className="diff-row-pair">
                              <td className={`diff-line-num ${leftClass}-num`}>{left?.lineNum ?? ''}</td>
                              <td className={`diff-line-code ${leftClass}-code`}>
                                <pre className="diff-pre">{left ? highlightCode(left.content, lang) : ' '}</pre>
                              </td>
                              <td className={`diff-line-num ${rightClass}-num`}>{right?.lineNum ?? ''}</td>
                              <td className={`diff-line-code ${rightClass}-code`}>
                                <pre className="diff-pre">{right ? highlightCode(right.content, lang) : ' '}</pre>
                              </td>
                            </tr>
                          );
                        } else {
                          let start = i;
                          while (i < rowPairs.length && !visibility[i]) {
                            i++;
                          }
                          const end = i - 1;
                          const count = end - start + 1;
                          i--;

                          const isAtTop = start === 0;
                          const isAtBottom = end === rowPairs.length - 1;

                          let showTopBar = false;
                          let showBottomBar = false;
                          let showPlaceholder = false;

                          if (isAtTop && isAtBottom) {
                            showTopBar = true;
                          } else if (isAtTop) {
                            showBottomBar = true;
                          } else if (isAtBottom) {
                            showTopBar = true;
                          } else {
                            showTopBar = true;
                            showBottomBar = true;
                            showPlaceholder = true;
                          }

                          rows.push(
                            <tr key={`expand-${start}`} className="diff-expand-row">
                              <td colSpan={4} className="diff-expand-cell">
                                <div className="diff-expand-container">
                                  {showTopBar && (
                                    <div className="diff-expand-bar diff-expand-bar-down">
                                      {count > 10 && (
                                        <button 
                                          className="btn-expand"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, start, start + 9);
                                          }}
                                        >
                                          ▼ +10 lines
                                        </button>
                                      )}
                                      {count > 0 && (
                                        <button 
                                          className="btn-expand btn-expand-all"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, start, end);
                                          }}
                                        >
                                          ▼ +{count} common lines
                                        </button>
                                      )}
                                    </div>
                                  )}

                                  {showPlaceholder && (
                                    <div className="diff-expand-placeholder">
                                      ↕ {count} common lines hidden
                                    </div>
                                  )}

                                  {showBottomBar && (
                                    <div className="diff-expand-bar diff-expand-bar-up">
                                      {count > 0 && (
                                        <button 
                                          className="btn-expand btn-expand-all"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, start, end);
                                          }}
                                        >
                                          ▲ +{count} common lines
                                        </button>
                                      )}
                                      {count > 10 && (
                                        <button 
                                          className="btn-expand"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            expandLines(file.filename, end - 9, end);
                                          }}
                                        >
                                          ▲ +10 lines
                                        </button>
                                      )}
                                    </div>
                                  )}
                                </div>
                              </td>
                            </tr>
                          );
                        }
                      }
                      return rows;
                    })()}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('Kanban');
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState<boolean>(true);
  const [previewBranch, setPreviewBranch] = useState<'pre' | 'post'>('post');

  useEffect(() => {
    const inReview = requirements.some(r => r.status === 'Review');
    if (!inReview) {
      setReviews([]);
      return;
    }
    fetch('/api/reviews')
      .then(res => res.json())
      .then(data => setReviews(data))
      .catch(err => console.error(err));
  }, [requirements]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newType, setNewType] = useState<'Folder' | 'Requirement'>('Folder');

  // Edit state
  const [isEditingReq, setIsEditingReq] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editPrio, setEditPrio] = useState<Priority>('Med');

  // Bug reporting state
  const [isReportingBug, setIsReportingBug] = useState(false);
  const [bugTitle, setBugTitle] = useState('');
  const [bugSteps, setBugSteps] = useState('');
  const [bugExpected, setBugExpected] = useState('');
  const [bugActual, setBugActual] = useState('');

  // Agent live logs state
  const [agentLogs, setAgentLogs] = useState<string>('');



  // Requirements Tree State
  const [selectedReqId, setSelectedReqId] = useState<string | null>(null);
  const selectedNode = requirements.find(r => r.id === selectedReqId);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['FLD-CORE']));
  
  const toggleNode = (id: string) => {
    const next = new Set(expandedNodes);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpandedNodes(next);
  };

  const fetchReqs = async () => {
    try {
      const res = await fetch('/api/requirements');
      const data = await res.json();
      setRequirements(data);
      setLoading(false);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReqs();
    const interval = setInterval(fetchReqs, 5000);
    return () => clearInterval(interval);
  }, []);

  // When leaving a review detail, reset branch and workspace to main
  useEffect(() => {
    if (selectedReviewId === null && previewBranch === 'pre') {
      setPreviewBranch('post');
      fetch('/api/checkout-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ branch: 'main' })
      }).catch(() => {/* ignore */});
    }
  }, [selectedReviewId]);

  useEffect(() => {
    const inProgress = requirements.filter(r => r.status === 'InProgress');
    if (inProgress.length === 0) {
      setAgentLogs('');
      return;
    }
    
    const ticketId = inProgress[0].id;
    const fetchLogs = async () => {
      try {
        const res = await fetch(`/api/logs/${ticketId}`);
        const data = await res.json();
        if (data.logs) {
          setAgentLogs(data.logs);
        }
      } catch (e) {
        // ignore log fetch errors
      }
    };
    
    fetchLogs();
    const logInterval = setInterval(fetchLogs, 2000);
    return () => clearInterval(logInterval);
  }, [requirements]);

  const handleCreateReq = async (req: Requirement) => {
    const updated = [...requirements, req];
    setRequirements(updated);
    await fetch('/api/requirements', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated) 
    });
  };

  const handleUpdateReq = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReqId) return;
    
    const updated = requirements.map(r => 
      r.id === selectedReqId 
        ? { ...r, title: editTitle, description: editDesc, priority: editPrio } 
        : r
    );
    setRequirements(updated);
    setIsEditingReq(false);
    
    await fetch('/api/edit-requirement', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: selectedReqId, title: editTitle, description: editDesc, priority: editPrio }) 
    });
  };

  const handleDeleteReq = async (id: string) => {
    const isFolder = requirements.find(r => r.id === id)?.type === 'Folder';
    const message = isFolder 
      ? "Are you sure you want to delete this folder and ALL its contents (nested folders, requirements, and tasks)?"
      : "Are you sure you want to delete this requirement and its sub-tasks?";
      
    if (!window.confirm(message)) return;
    
    // Recursive helper to collect all descendant IDs
    const getDescendantIds = (targetId: string, reqs: Requirement[]): Set<string> => {
      const ids = new Set<string>([targetId]);
      let sizeBefore: number;
      do {
        sizeBefore = ids.size;
        reqs.forEach(r => {
          if (r.parentId && ids.has(r.parentId)) {
            ids.add(r.id);
          }
        });
      } while (ids.size > sizeBefore);
      return ids;
    };
    
    const descendants = getDescendantIds(id, requirements);
    const updated = requirements.filter(r => !descendants.has(r.id));
    
    setRequirements(updated);
    setSelectedReqId(null);
    setIsEditingReq(false);
    
    await fetch('/api/requirements', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated) 
    });
  };

  const handleReportBug = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReqId) return;
    
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
        type: 'Folder',
        parentId: undefined
      };
      const updated = [...requirements, newReq];
      setRequirements(updated);
      await fetch('/api/requirements', { method: 'POST', body: JSON.stringify(updated), headers: { 'Content-Type': 'application/json' } });
    }

    await fetchReqs();
    setNewTitle('');
    setNewDesc('');
  };



  const inProgressReqs = requirements.filter(r => r.status === 'InProgress');

  const renderKanban = () => (
    <section className="kanban-board">
      {inProgressReqs.length > 0 && (
        <div className="active-agent-banner" style={{ gridColumn: '1 / -1', background: 'rgba(0,0,0,0.4)', border: '1px solid var(--accent-primary)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="spinner" style={{ border: '3px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-primary)', borderRadius: '50%', width: '20px', height: '20px', animation: 'spin 1s linear infinite' }}></div>
            <div>
              <div style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>Agent Active</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Working on {inProgressReqs.map(r => r.id).join(', ')}...</div>
            </div>
          </div>
          <div className="agent-terminal" style={{ background: '#0d1117', padding: '0.8rem', borderRadius: '4px', border: '1px solid #30363d', maxHeight: '150px', overflowY: 'auto' }}>
            <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.75rem', color: '#c9d1d9', whiteSpace: 'pre-wrap' }}>
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
          <div key={col.id} className="kanban-column">
            <div className="kanban-column-header">
              <span>{col.title}</span>
              <span className="badge" style={{ background: 'rgba(255,255,255,0.1)' }}>{columnReqs.length}</span>
            </div>
            <div className="kanban-column-content">
              {columnReqs.map(req => {
                const passingTests = req.tests?.filter(t => t.status === 'Passing').length || 0;
                const totalTests = req.tests?.length || 0;
                const isBug = req.type === 'Bug';
                return (
                  <div key={req.id} className={`kanban-card ${isBug ? 'kanban-card-bug' : ''}`}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className="text-muted" style={{ fontSize: '0.7rem' }}>{req.id}</span>
                      <span className={`badge ${isBug ? 'badge-bug' : getBadgeClass(req.priority)}`}>
                        {isBug ? 'Bug' : req.priority}
                      </span>
                    </div>
                    <h4 className="card-title">{req.title}</h4>
                    {req.status === 'Conflict' && (
                      <div className="kanban-card-conflict-badge" style={{ color: '#fbbf24', fontSize: '0.75rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
                        ⚠️ Conflict (Resolving...)
                      </div>
                    )}
                    <div className="card-meta">
                      <span style={{ fontSize: '0.8rem' }}>{passingTests}/{totalTests} Tests</span>
                      <div style={{ display: 'flex', gap: '0.2rem' }}>
                        {req.assignedAgents?.map(agent => (
                          <div key={agent} title={agent} style={{ width: '20px', height: '20px', borderRadius: '50%', background: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 'bold' }}>
                            {agent.charAt(0)}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
              
              {/* Backlog creation form removed from Kanban */}
            </div>
          </div>
        );
      })}
    </section>
  );

  const renderTreeNodes = (parentId?: string, depth = 0) => {
    const nodes = requirements.filter(r => r.parentId === parentId || (!r.parentId && !parentId));
    if (nodes.length === 0) return null;

    return (
      <div style={{ paddingLeft: depth === 0 ? 0 : '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
        {nodes.map(node => {
          const isFolder = node.type === 'Folder' || node.type === 'Epic';
          const isExpanded = expandedNodes.has(node.id);
          const isSelected = selectedReqId === node.id;
          const hasChildren = requirements.some(r => r.parentId === node.id);

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
                  setIsEditingReq(false);
                }}
              >
                <span 
                  onClick={(e) => { e.stopPropagation(); toggleNode(node.id); }}
                  style={{ width: '20px', textAlign: 'center', marginRight: '0.5rem', cursor: 'pointer', opacity: (isFolder || hasChildren) ? 1 : 0 }}
                >
                  {(isFolder || hasChildren) ? (isExpanded ? '▼' : '▶') : '•'}
                </span>
                <span style={{ marginRight: '0.5rem' }}>
                  {isFolder ? '📁' : (node.type === 'Bug' ? '🐛' : (node.type === 'Task' ? '📝' : '📄'))}
                </span>
                <span style={{ flex: 1, fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.title}</span>
              </div>
              {isExpanded && renderTreeNodes(node.id, depth + 1)}
            </div>
          );
        })}
      </div>
    );
  };

  const renderRequirements = () => {
    const childNodes = selectedNode ? requirements.filter(r => r.parentId === selectedNode.id) : requirements.filter(r => !r.parentId);
    
    return (
      <div style={{ display: 'flex', gap: '2rem', height: '100%' }}>
        {/* Left Pane: Tree Explorer */}
        <div className="glass-panel" style={{ flex: '0 0 300px', overflowY: 'auto', padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Explorer</h3>
            <button className="btn btn-primary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => setSelectedReqId(null)}>➕ New</button>
          </div>
          {renderTreeNodes()}
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
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                        <div>
                          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>📁 {selectedNode.title}</h2>
                          {selectedNode.description && <p className="text-muted" style={{ marginTop: '0.5rem' }}>{selectedNode.description}</p>}
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                          <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => {
                            setEditTitle(selectedNode.title);
                            setEditDesc(selectedNode.description || '');
                            setEditPrio(selectedNode.priority); // Not used for folder form, but safe
                            setIsEditingReq(true);
                          }}>✏️ Edit</button>
                          <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)' }} onClick={() => handleDeleteReq(selectedNode.id)}>🗑️ Delete</button>
                        </div>
                      </div>
                      
                      <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>Children Items</h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '2rem' }}>
                        {childNodes.length === 0 ? <p className="text-muted">No items found.</p> : childNodes.map(child => (
                          <div key={child.id} onClick={() => setSelectedReqId(child.id)} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.8rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', cursor: 'pointer' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                              <span>{child.type === 'Folder' ? '📁' : (child.type === 'Task' ? '📝' : '📄')}</span>
                              <span>{child.title}</span>
                            </div>
                            {child.type === 'Task' && (
                               <span className={`badge ${getBadgeClass(child.priority)}`}>{child.priority}</span>
                            )}
                          </div>
                        ))}
                      </div>

                      <h3 style={{ marginBottom: '1rem' }}>Add Child Item</h3>
                      <form onSubmit={async (e) => {
                        e.preventDefault();
                        if (newType === 'Requirement') {
                          await fetch('/api/create-requirement', { 
                            method: 'POST', 
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ title: newTitle, description: newDesc, parentId: selectedNode.id }) 
                          });
                          await fetchReqs();
                        } else {
                          handleCreateReq({
                            id: `FLD-${Math.floor(Math.random() * 1000)}`,
                            title: newTitle,
                            description: newDesc,
                            priority: 'Med',
                            status: 'Backlog',
                            tests: [],
                            assignedAgents: [],
                            type: 'Folder',
                            parentId: selectedNode.id
                          });
                        }
                        setNewTitle('');
                        setNewDesc('');
                        setExpandedNodes(new Set([...expandedNodes, selectedNode.id]));
                      }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px' }}>
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
                          <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Description / Spec {newType === 'Folder' && '(Optional)'}</label>
                          <textarea required={newType === 'Requirement'} value={newDesc} onChange={e => setNewDesc(e.target.value)} rows={4} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
                        </div>
                        <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }}>Create Child</button>
                      </form>
                    </>
                  )}
                </div>
              ) : (
                <div className="glass-card" style={{ padding: '2rem' }}>
                  {isEditingReq ? (
                    <form onSubmit={handleUpdateReq} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                         <h2 style={{ margin: 0 }}>Edit Requirement</h2>
                         <div style={{ display: 'flex', gap: '1rem' }}>
                            <button type="submit" className="btn btn-primary">Save Changes</button>
                            <button type="button" className="btn btn-outline" onClick={() => setIsEditingReq(false)}>Cancel</button>
                         </div>
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Title</label>
                        <input required value={editTitle} onChange={e => setEditTitle(e.target.value)} type="text" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', fontSize: '1.2rem' }} />
                      </div>
                      
                      {selectedNode.type === 'Task' && (
                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Priority</label>
                          <select value={editPrio} onChange={e => setEditPrio(e.target.value as Priority)} style={{ width: '200px', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: '#1e293b', color: 'white' }}>
                            <option value="High">High</option>
                            <option value="Med">Medium</option>
                            <option value="Low">Low</option>
                          </select>
                        </div>
                      )}

                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Description</label>
                        <textarea required value={editDesc} onChange={e => setEditDesc(e.target.value)} rows={8} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', color: 'white', resize: 'vertical' }} />
                      </div>
                    </form>
                  ) : (
                    <>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>{selectedNode.type === 'Task' ? '📝' : '📄'} {selectedNode.title}</h2>
                        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                          {selectedNode.type === 'Task' && (
                             <span className={`badge ${getBadgeClass(selectedNode.priority)}`}>{selectedNode.priority}</span>
                          )}
                          {selectedNode.type === 'Requirement' && (
                            <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', borderColor: 'var(--accent-warning)', color: 'var(--accent-warning)' }} onClick={() => setIsReportingBug(true)}>🐛 Report Bug</button>
                          )}
                          <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }} onClick={() => {
                            setEditTitle(selectedNode.title);
                            setEditDesc(selectedNode.description);
                            setEditPrio(selectedNode.priority);
                            setIsEditingReq(true);
                          }}>✏️ Edit</button>
                          <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem', borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)' }} onClick={() => handleDeleteReq(selectedNode.id)}>🗑️ Delete</button>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                         <span className="text-muted" style={{ fontSize: '0.85rem' }}>ID: {selectedNode.id}</span>
                         <span className="text-muted" style={{ fontSize: '0.85rem' }}>Status: {selectedNode.status}</span>
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>Description</label>
                        <div style={{ padding: '1rem', borderRadius: '4px', border: '1px solid var(--border-glass)', background: 'rgba(0,0,0,0.2)', minHeight: '150px' }}>
                          <textarea value={selectedNode.description} readOnly style={{ width: '100%', height: '100%', minHeight: '130px', background: 'transparent', border: 'none', color: 'white', resize: 'vertical', outline: 'none' }} />
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    );
  };

  const renderTestSuite = () => {
    const testItems = requirements.filter(r => r.tests && r.tests.length > 0);
    
    return (
      <div className="glass-panel" style={{ padding: '2rem', overflowY: 'auto', height: 'calc(100vh - 150px)' }}>
        <h2>Pytest Suite (Live Results)</h2>
        <p className="text-muted">Automated test cases and execution status for tasks.</p>
        
        <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {testItems.map(req => {
            const passingTests = req.tests?.filter(t => t.status === 'Passing').length || 0;
            const totalTests = req.tests?.length || 0;
            return (
              <div key={req.id} className="glass-card" style={{ borderLeft: `4px solid ${passingTests === totalTests ? 'var(--accent-success)' : 'var(--accent-danger)'}` }}>
                 <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                   <h4 style={{ margin: 0 }}>{req.id}: {req.title}</h4>
                   <span className="text-muted" style={{ fontSize: '0.85rem' }}>Status: {req.status}</span>
                 </div>
                 
                 <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', margin: '1rem 0', background: 'rgba(0,0,0,0.1)', padding: '0.8rem', borderRadius: '4px' }}>
                   {req.tests.map((test, idx) => (
                     <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', padding: '0.8rem', background: 'rgba(255,255,255,0.02)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontFamily: 'monospace', fontWeight: 'bold', fontSize: '0.85rem' }}>🧪 {test.name}</span>
                          <span style={{ color: test.status === 'Passing' ? '#4ade80' : '#f87171', fontWeight: 'bold', fontSize: '0.85rem' }}>{test.status}</span>
                        </div>
                        {test.title && <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent-primary)', marginTop: '0.2rem' }}>{test.title}</div>}
                        {test.id && (
                         <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                           <span>ID: {test.id}</span> | <span>Req: {test.req}</span>
                         </div>
                       )}
                       {test.given && (
                         <div style={{ fontSize: '0.75rem', color: '#cbd5e1', marginLeft: '0.5rem', borderLeft: '2px solid rgba(255,255,255,0.1)', paddingLeft: '0.5rem', marginTop: '0.2rem' }}>
                           <div><strong>Given:</strong> {test.given}</div>
                           <div><strong>When:</strong> {test.when}</div>
                           <div><strong>Then:</strong> {test.then}</div>
                         </div>
                       )}
                     </div>
                   ))}
                 </div>
              </div>
            );
          })}
          {testItems.length === 0 && <p className="text-muted">No test results available.</p>}
        </div>
      </div>
    );
  };

  const handleApproveCode = async (req: Requirement) => {
    try {
      const res = await fetch('/api/merge-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: req.id, code: "" })
      });
      const data = await res.json();
      if (data.success) {
        setSelectedReviewId(null);
      } else {
        alert(`Merge failed: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error(err);
      alert("Network error occurred during merge.");
    }
    await fetchReqs();
  };

  const handleRejectCode = async (req: Requirement) => {
    const feedback = prompt("Provide feedback to the agent on why this code was rejected:");
    if (!feedback) return;
    setSelectedReviewId(null);
    const updated = requirements.map(r => r.id === req.id ? { ...r, status: 'Backlog' as KanbanStatus, feedback } : r);
    setRequirements(updated);
    await fetch('/api/requirements', { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updated) 
    });
    
    // Trigger agents again to process the feedback
    await fetch('/api/trigger-agents', { method: 'POST' });
    await fetchReqs();
  };

  const renderCodeReview = () => {
    if (selectedReviewId === null) {
      return (
        <div className="gerrit-dashboard">
          <div className="gerrit-dashboard-title">Incoming Reviews</div>
          {reviews.length === 0 ? (
            <p className="text-muted" style={{ padding: '1rem', textAlign: 'center' }}>No reviews pending.</p>
          ) : (
            <table className="gerrit-table">
              <thead>
                <tr>
                  <th className="gerrit-header-cell" style={{ width: '120px' }}>ID</th>
                  <th className="gerrit-header-cell">Subject</th>
                  <th className="gerrit-header-cell" style={{ width: '100px' }}>Size</th>
                  <th className="gerrit-header-cell" style={{ width: '120px' }}>Wait Time</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map(review => (
                  <tr 
                    key={review.id} 
                    className="gerrit-row"
                    onClick={() => setSelectedReviewId(review.id)}
                  >
                    <td className="gerrit-cell" style={{ fontFamily: 'monospace' }}>{review.id}</td>
                    <td className="gerrit-cell gerrit-subject">
                      {review.title}
                      {review.status === 'Conflict' && (
                        <span className="badge badge-conflict-resolving" style={{ marginLeft: '0.5rem', background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)', verticalAlign: 'middle', textTransform: 'none' }}>
                          ⚠️ Conflict (Resolving...)
                        </span>
                      )}
                    </td>
                    <td className="gerrit-cell">
                      <span className={`gerrit-size-badge gerrit-size-${review.size.toLowerCase()}`}>
                        {review.size}
                      </span>
                    </td>
                    <td className="gerrit-cell" style={{ color: 'var(--text-muted)' }}>
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
      <div className="gerrit-detail-container">
        {req.status === 'Review' && req.feedback && (
          <div 
            style={{ 
              padding: '0.8rem 1rem', 
              border: '1px solid var(--accent-danger)', 
              background: 'rgba(239, 68, 68, 0.1)', 
              borderRadius: '6px', 
              color: '#f87171', 
              fontSize: '0.9rem',
              marginBottom: '0.5rem'
            }}
          >
            <strong>⚠️ Merge Warning:</strong> {req.feedback}
          </div>
        )}
        <DiffViewer ticketId={req.id} />
      </div>
    );
  };


  const reviewCount = requirements.filter(r => (r.status === 'Review' || r.status === 'Conflict') && (r.type === 'Task' || r.type === 'Bug')).length;

  const navItems = [
    { id: 'Kanban', label: 'Kanban' },
    { id: 'Requirements', label: 'Requirements' },
    { id: 'Tests', label: 'Tests' },
    { id: 'Review', label: 'Review', badge: reviewCount }
  ];

  return (
    <div className="app-container">
      <header className="app-header-nav">
        <div className="nav-logo" onClick={() => setCurrentView('Kanban')}>
          🚀 Provable
        </div>
        <div className="nav-links">
          {navItems.map(item => {
            const isActive = currentView === item.id;
            return (
              <button 
                key={item.id} 
                onClick={() => {
                  setCurrentView(item.id);
                  if (item.id === 'Review') {
                    setSelectedReviewId(null);
                  }
                }}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                {item.label}
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="nav-badge">{item.badge}</span>
                )}
              </button>
            );
          })}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            id="toggle-preview-btn"
            className={`btn ${showPreview ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '0.35rem 0.9rem', fontSize: '0.85rem', gap: '0.4rem' }}
            onClick={() => setShowPreview(p => !p)}
            title={showPreview ? 'Hide Live Preview' : 'Show Live Preview'}
          >
            <span style={{ fontSize: '1rem' }}>{showPreview ? '🖥️' : '📺'}</span>
            {showPreview ? 'Hide Preview' : 'Show Preview'}
          </button>
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <main className="main-content">
          {currentView === 'Review' && selectedReviewId !== null && (
            <header className="header" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              {(() => {
                const req = requirements.find(r => r.id === selectedReviewId);
                return (
                  <>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                        <button 
                          className="btn btn-outline" 
                          style={{ padding: '0.25rem 0.6rem', fontSize: '0.8rem' }} 
                          onClick={() => {
                            setSelectedReviewId(null);
                            // Reset preview to main/post when going back
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
                      <p className="text-muted" style={{ margin: 0, paddingLeft: '4.8rem' }}>{req?.title}</p>
                    </div>
                    {req && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        {/* Pre/Post branch toggle — only shown when preview is visible */}
                        {showPreview && (
                          <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '3px', border: '1px solid var(--border-glass)' }}>
                            <button
                              id="preview-pre-btn"
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
                              id="preview-post-btn"
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
                            <span>Merge conflict detected. Automated agent is resolving and running pytest...</span>
                          </div>
                        ) : (
                          <div style={{ display: 'flex', gap: '0.75rem' }}>
                            <button className="btn btn-primary" onClick={() => handleApproveCode(req)}>
                              Approve (Merge)
                            </button>
                            <button 
                              className="btn btn-outline" 
                              style={{ borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)' }} 
                              onClick={() => handleRejectCode(req)}
                            >
                              Reject
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                );
              })()}
            </header>
          )}

          {loading ? <p>Loading data...</p> : (
            <>
              {currentView === 'Kanban' && renderKanban()}
              {currentView === 'Requirements' && renderRequirements()}
              {currentView === 'Tests' && renderTestSuite()}
              {currentView === 'Review' && renderCodeReview()}
            </>
          )}
        </main>

        <aside className="preview-sidebar" style={{ display: showPreview ? undefined : 'none' }}>
          <iframe src="http://localhost:5174" style={{ width: '100%', height: '100%', border: 'none', background: '#fff' }} title="Workspace Preview" />
        </aside>
      </div>

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

export default App;
