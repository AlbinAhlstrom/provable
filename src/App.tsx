import { useState, useEffect } from 'react';
import KickstartStudio from './components/KickstartStudio';
import RequirementsList from './components/RequirementsList';
import CoverageHub from './components/CoverageHub';
import ProjectSelector from './components/ProjectSelector';
import { Requirement } from './hooks/useRequirements';

export function App() {
  const [currentView, setCurrentView] = useState<string>('Domain');
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [selectedReqId, setSelectedReqId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  const [coverageData, setCoverageData] = useState<any>(null);
  const [agentStatus, setAgentStatus] = useState<any>({
    active: false,
    ticket_id: null,
    step: 'idle',
    attempt: 0,
    max_attempts: 3,
    last_update: ''
  });
  const [backlogAnalysis, setBacklogAnalysis] = useState<any[]>([]);
  const [reviews, setReviews] = useState<any[]>([]);
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  
  const [previewUrl, setPreviewUrl] = useState<string>('http://localhost:5174');
  const [showPreview, setShowPreview] = useState<boolean>(false);
  const [previewBranch, setPreviewBranch] = useState<'post' | 'pre'>('post');
  
  const [agentLogs, setAgentLogs] = useState<string>('');
  const [isTrayExpanded, setIsTrayExpanded] = useState<boolean>(false);
  
  const [isGeneratingTestCase, setIsGeneratingTestCase] = useState<boolean>(false);
  const [generatedTestCode, setGeneratedTestCode] = useState<string | null>(null);

  const fetchReqs = async () => {
    try {
      const res = await fetch('/api/requirements');
      const data = await res.json();
      setRequirements(data);
    } catch (err) {
      console.error("Failed to fetch requirements:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCoverage = async () => {
    try {
      const res = await fetch('/api/coverage');
      const data = await res.json();
      setCoverageData(data);
    } catch (err) {
      console.error("Failed to fetch coverage data:", err);
    }
  };

  const fetchAgentStatus = async () => {
    try {
      const res = await fetch('/api/agent-status');
      const data = await res.json();
      setAgentStatus(data.status);
      setBacklogAnalysis(data.backlog_analysis || []);
    } catch (err) {
      console.error("Failed to fetch agent status:", err);
    }
  };

  const fetchReviews = async () => {
    try {
      const res = await fetch('/api/reviews');
      const data = await res.json();
      setReviews(data);
    } catch (err) {
      console.error("Failed to fetch reviews:", err);
    }
  };

  useEffect(() => {
    const initData = async () => {
      await fetchReqs();
      await fetchCoverage();
      await fetchAgentStatus();
      await fetchReviews();
    };
    initData();

    const interval = setInterval(() => {
      fetchReqs();
      fetchCoverage();
      fetchAgentStatus();
      fetchReviews();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleProjectSwitch = (newPreviewUrl: string) => {
    setPreviewUrl(newPreviewUrl);
    fetchReqs();
    fetchCoverage();
    fetchAgentStatus();
    fetchReviews();
  };

  const handleUpdateReq = async (id: string, updates: Partial<Requirement>) => {
    try {
      const res = await fetch(`/api/requirements/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (res.ok) {
        await fetchReqs();
      }
    } catch (err) {
      console.error("Failed to update requirement:", err);
    }
  };

  const handleCreateTestCase = async (reqId: string) => {
    setIsGeneratingTestCase(true);
    setGeneratedTestCode(null);
    try {
      const res = await fetch(`/api/requirements/${reqId}/generate-test`, {
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

  useEffect(() => {
    if (selectedReviewId === null && previewBranch === 'pre') {
      setPreviewBranch('post');
      fetch('/api/checkout-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ branch: 'main' })
      }).catch(() => {});
    }
  }, [selectedReviewId, previewBranch]);

  useEffect(() => {
    if (!agentStatus.active || !agentStatus.ticket_id) {
      setAgentLogs('');
      return;
    }
    
    const fetchLogs = async () => {
      try {
        const res = await fetch(`/api/logs/${agentStatus.ticket_id}`);
        const data = await res.json();
        if (data.logs) {
          setAgentLogs(data.logs);
        }
      } catch (e) {}
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

  const [resetting, setResetting] = useState<boolean>(false);
  
  const handleResetAllProjects = async () => {
    setResetting(true);
    try {
      const res = await fetch('/api/projects/reset-all', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await fetchReqs();
        await fetchCoverage();
        await fetchAgentStatus();
        await fetchReviews();
      }
    } catch (err) {
      console.error("Error resetting projects:", err);
    } finally {
      setResetting(false);
    }
  };

  const navItems = [
    { id: 'Domain', label: '🚀 Kickstart' },
    { id: 'Requirements', label: 'Requirements' },
    { id: 'Tests', label: 'Tests' }
  ];

  return (
    <div className="app-container">
      <header className="app-header-nav">
        <div className="nav-logo" onClick={() => setCurrentView('Requirements')}>
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
                }}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ProjectSelector onProjectSwitch={handleProjectSwitch} />
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <main className="main-content" style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: currentView === 'Preview' ? '1rem 1.5rem' : undefined }}>
          {loading ? <p style={{ padding: '2rem' }}>Loading data...</p> : (
            <>
              {currentView === 'Domain' && (
                <KickstartStudio onAppSynthesized={async () => {
                  await fetchReqs();
                  await fetchCoverage();
                }} />
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
                  agentStatus={agentStatus}
                  requirements={requirements}
                  setCurrentView={setCurrentView}
                  setSelectedReqId={setSelectedReqId}
                  fetchReqs={fetchReqs}
                  fetchCoverage={fetchCoverage}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
