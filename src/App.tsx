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

  useEffect(() => {
    const initData = async () => {
      await fetchReqs();
      await fetchCoverage();
    };
    initData();

    const interval = setInterval(() => {
      fetchReqs();
      fetchCoverage();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleProjectSwitch = () => {
    fetchReqs();
    fetchCoverage();
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

      <div style={{ display: 'flex', flex: 1, flexDirection: 'column', width: '100%', minHeight: 0 }}>
        <main className="main-content" style={{ display: 'flex', flexDirection: 'column', flex: 1, width: '100%', minHeight: 0, padding: currentView === 'Preview' ? '1rem 1.5rem' : undefined }}>
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
