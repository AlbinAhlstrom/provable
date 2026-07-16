import React, { useState, useEffect } from 'react';
import { useRequirements, Requirement } from './hooks/useRequirements';
import KanbanBoard from './components/KanbanBoard';
import RequirementsList from './components/RequirementsList';
import CodeReview from './components/CodeReview';
import CoverageHub from './components/CoverageHub';
import AgentTray from './components/AgentTray';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('Kanban');
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState<boolean>(true);
  const [previewBranch, setPreviewBranch] = useState<'pre' | 'post'>('post');

  // Custom hook for requirements state
  const {
    requirements,
    loading,
    fetchReqs,
    handleUpdateReq
  } = useRequirements();

  // Agent Status & Backlog states
  const [agentStatus, setAgentStatus] = useState<any>({
    active: false,
    ticket_id: null,
    step: 'Idle',
    attempt: 0,
    max_attempts: 3,
    last_update: ''
  });
  const [backlogAnalysis, setBacklogAnalysis] = useState<any[]>([]);
  const [isTrayExpanded, setIsTrayExpanded] = useState<boolean>(false);
  const [agentLogs, setAgentLogs] = useState<string>('');

  // Test case generation states
  const [isGeneratingTestCase, setIsGeneratingTestCase] = useState(false);
  const [generatedTestCode, setGeneratedTestCode] = useState<string | null>(null);
  const [selectedReqId, setSelectedReqId] = useState<string | null>(null);

  // Test coverage states
  const [coverageData, setCoverageData] = useState<any>(null);
  const [loadingCoverage, setLoadingCoverage] = useState(false);

  const fetchAgentStatus = async () => {
    try {
      const res = await fetch('/api/agent-status');
      const data = await res.json();
      if (data.status) {
        setAgentStatus(data.status);
      }
      if (data.backlog_analysis) {
        setBacklogAnalysis(data.backlog_analysis);
      }
    } catch (e) {
      console.error("Error fetching agent status:", e);
    }
  };

  useEffect(() => {
    fetchAgentStatus();
    const interval = setInterval(fetchAgentStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchReviews = () => {
    fetch('/api/reviews')
      .then(res => res.json())
      .then(data => setReviews(data))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchReviews();
    const interval = setInterval(fetchReviews, 5000);
    return () => clearInterval(interval);
  }, [requirements]);

  const fetchCoverage = async () => {
    setLoadingCoverage(true);
    try {
      const res = await fetch('/api/coverage');
      const data = await res.json();
      setCoverageData(data);
    } catch (err) {
      console.error("Failed to fetch coverage details", err);
    } finally {
      setLoadingCoverage(false);
    }
  };

  useEffect(() => {
    if (currentView === 'Tests') {
      fetchCoverage();
    }
  }, [currentView]);

  useEffect(() => {
    setGeneratedTestCode(null);
  }, [selectedReqId]);

  const handleCreateTestCase = async (reqId: string) => {
    setIsGeneratingTestCase(true);
    setGeneratedTestCode(null);
    try {
      const res = await fetch(`/api/requirements/${reqId}/create-test-case`, {
        method: 'POST'
      });
      const data = await res.json();
      if (data.success) {
        setGeneratedTestCode(data.test_code);
        await fetchReqs();
        await fetchCoverage();
      } else {
        alert("Failed to generate test case: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      console.error(err);
      alert("Error calling test case generation API.");
    } finally {
      setIsGeneratingTestCase(false);
    }
  };

  // Reset branch preview state when leaving review detail
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

  // Log streaming effect
  useEffect(() => {
    if (!agentStatus.active || !agentStatus.ticket_id) {
      return;
    }
    
    const fetchLogs = async () => {
      try {
        const res = await fetch(`/api/logs/${agentStatus.ticket_id}`);
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
  }, [agentStatus.active, agentStatus.ticket_id]);

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

  const handleProvideFeedback = async (req: Requirement) => {
    const feedback = prompt("Provide feedback to the agent on why this code is not accepted:");
    if (!feedback) return;
    setSelectedReviewId(null);
    
    await handleUpdateReq(req.id, { status: 'Backlog', feedback });
    
    // Trigger agents again to process the feedback
    await fetch('/api/trigger-agents', { method: 'POST' });
    await fetchReqs();
  };

  const handleAbandonTicket = async (req: Requirement) => {
    if (!confirm(`Are you sure you want to abandon ticket ${req.id}? This will discard the agent's changes and delete the branch.`)) {
      return;
    }
    setSelectedReviewId(null);
    try {
      const res = await fetch(`/api/abandon-ticket/${req.id}`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await fetchReqs();
      } else {
        alert(`Failed to abandon ticket: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error(err);
      alert("Network error occurred while abandoning the ticket.");
    }
  };

  const reviewCount = reviews.length;

  const navItems = [
    { id: 'Kanban', label: 'Kanban' },
    { id: 'Requirements', label: 'Requirements' },
    { id: 'Tests', label: 'Tests' },
    { id: 'Review', label: 'Review', badge: reviewCount }
  ];

  const activeReview = requirements.find(r => r.id === selectedReviewId);

  // Contextualize preview window: only show in Review or dedicated states
  const isReviewActive = currentView === 'Review' && selectedReviewId !== null;
  const shouldRenderPreview = showPreview && (isReviewActive || currentView === 'Kanban');

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
          {(isReviewActive || currentView === 'Kanban') && (
            <button
              id="toggle-preview-btn"
              className={`btn ${shouldRenderPreview ? 'btn-primary' : 'btn-outline'}`}
              style={{ padding: '0.35rem 0.9rem', fontSize: '0.85rem', gap: '0.4rem' }}
              onClick={() => setShowPreview(p => !p)}
              title={shouldRenderPreview ? 'Hide Live Preview' : 'Show Live Preview'}
            >
              <span style={{ fontSize: '1rem' }}>{shouldRenderPreview ? '🖥️' : '📺'}</span>
              {shouldRenderPreview ? 'Hide Preview' : 'Show Preview'}
            </button>
          )}
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <main className="main-content">
          {loading ? <p style={{ padding: '2rem' }}>Loading data...</p> : (
            <>
              {currentView === 'Kanban' && (
                <KanbanBoard 
                  requirements={requirements}
                  agentLogs={agentLogs}
                  fetchReqs={fetchReqs}
                />
              )}
              {currentView === 'Requirements' && (
                <RequirementsList 
                  requirements={requirements}
                  selectedReqId={selectedReqId}
                  setSelectedReqId={setSelectedReqId}
                  fetchReqs={fetchReqs}
                  isGeneratingTestCase={isGeneratingTestCase}
                  generatedTestCode={generatedTestCode}
                  handleCreateTestCase={handleCreateTestCase}
                />
              )}
              {currentView === 'Tests' && (
                <CoverageHub 
                  coverageData={coverageData}
                  requirements={requirements}
                  setCurrentView={setCurrentView}
                  setSelectedReqId={setSelectedReqId}
                  fetchReqs={fetchReqs}
                  fetchCoverage={fetchCoverage}
                />
              )}
              {currentView === 'Review' && (
                <CodeReview 
                  reviews={reviews}
                  selectedReviewId={selectedReviewId}
                  setSelectedReviewId={setSelectedReviewId}
                  requirements={requirements}
                  showPreview={shouldRenderPreview}
                  previewBranch={previewBranch}
                  setPreviewBranch={setPreviewBranch}
                  handleApproveCode={handleApproveCode}
                  handleProvideFeedback={handleProvideFeedback}
                  handleAbandonTicket={handleAbandonTicket}
                />
              )}
            </>
          )}
        </main>

        {shouldRenderPreview && (
          <aside className="preview-sidebar">
            <iframe src={`${window.location.protocol}//${window.location.hostname}:5174`} style={{ width: '100%', height: '100%', border: 'none', background: '#fff' }} title="Workspace Preview" />
          </aside>
        )}
      </div>

      <AgentTray 
        agentStatus={agentStatus}
        backlogAnalysis={backlogAnalysis}
        agentLogs={agentLogs}
        isTrayExpanded={isTrayExpanded}
        setIsTrayExpanded={setIsTrayExpanded}
        fetchAgentStatus={fetchAgentStatus}
      />
    </div>
  );
};

export default App;
