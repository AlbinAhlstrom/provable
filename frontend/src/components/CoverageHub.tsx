import React from 'react';

interface CoverageHubProps {
  coverageData: any;
  agentStatus?: {
    active: boolean;
    ticket_id: string | null;
    step: string;
    attempt: number;
    max_attempts: number;
    last_update: string;
  };
  requirements: any[];
  setCurrentView: (view: string) => void;
  setSelectedReqId: (id: string | null) => void;
  fetchReqs: () => Promise<void>;
  fetchCoverage: () => Promise<void>;
}

const CoverageHub: React.FC<CoverageHubProps> = ({
  coverageData,
  agentStatus = { active: false, ticket_id: null, step: 'idle', attempt: 0, max_attempts: 3, last_update: '' },
  requirements,
  setCurrentView,
  setSelectedReqId,
  fetchReqs,
  fetchCoverage
}) => {
  if (!coverageData) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 'calc(100vh - 150px)' }}>
        <div className="spinner" style={{ border: '4px solid rgba(255,255,255,0.1)', borderTopColor: 'var(--accent-primary)', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite' }}></div>
        <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>Loading coverage data...</p>
      </div>
    );
  }

  const { summary, requirements: reqList, allure_report_url } = coverageData;

  const isReqFixing = (reqId: string) => {
    if (!agentStatus.active) return false;
    if (agentStatus.ticket_id === reqId) return true;
    
    // Check if the agent is working on a child task of reqId
    const activeTicket = requirements.find((r: any) => r.id === agentStatus.ticket_id);
    if (activeTicket && activeTicket.parentId === reqId) {
      return true;
    }
    return false;
  };

  const [runningTests, setRunningTests] = React.useState<Record<string, boolean>>({});
  const [runningAll, setRunningAll] = React.useState(false);
  const [selectedTestDetails, setSelectedTestDetails] = React.useState<any>(null);
  const [allureKey, setAllureKey] = React.useState(0);

  const handleRerunAll = async () => {
    setRunningAll(true);
    try {
      const res = await fetch('/api/tests/run', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await fetchReqs();
        await fetchCoverage();
        setAllureKey(prev => prev + 1);
      } else {
        console.error('Failed to run all tests:', data.error);
      }
    } catch (e) {
      console.error('Network error running all tests:', e);
    } finally {
      setRunningAll(false);
    }
  };

  const handleRerunTest = async (testId: string) => {
    setRunningTests(prev => ({ ...prev, [testId]: true }));
    try {
      const res = await fetch(`/api/tests/${testId}/run`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        await fetchReqs();
        await fetchCoverage();
        setAllureKey(prev => prev + 1);
      } else {
        console.error(`Failed to run test ${testId}:`, data.error);
      }
    } catch (e) {
      console.error(`Network error running test ${testId}:`, e);
    } finally {
      setRunningTests(prev => ({ ...prev, [testId]: false }));
    }
  };
  const total = summary.total_requirements || 0;
  const passing = summary.passing || 0;
  const failing = summary.failing || 0;
  const uncovered = summary.uncovered || 0;
  const pending = summary.pending || 0;
  
  const passPercent = total > 0 ? Math.round((passing / total) * 100) : 0;
  const failPercent = total > 0 ? Math.round((failing / total) * 100) : 0;
  const uncoverPercent = total > 0 ? Math.round((uncovered / total) * 100) : 0;
  const pendingPercent = total > 0 ? Math.round((pending / total) * 100) : 0;

  return (
    <div className="glass-panel" style={{ padding: '2rem', overflowY: 'auto', height: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2 style={{ margin: 0, fontSize: '1.8rem', background: 'linear-gradient(135deg, #fff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Requirements Coverage Hub</h2>
        <p className="text-muted" style={{ margin: '0.5rem 0 0 0' }}>Track requirement verification, test execution, and history in real-time.</p>
      </div>

      {/* Coverage Progress Bar & Aggregates */}
      <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '2rem' }}>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white' }}>{total}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Total Specs</div>
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-success)' }}>{passing}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Passing</div>
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-danger)' }}>{failing}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Failing</div>
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-primary)' }}>{pending}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Not Run</div>
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--text-muted)' }}>{uncovered}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Uncovered</div>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-primary)' }}>{passPercent}%</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Covered & Passing</div>
          </div>
        </div>

        <div style={{ height: '10px', background: 'rgba(255,255,255,0.05)', borderRadius: '5px', overflow: 'hidden', display: 'flex' }}>
          <div style={{ width: `${passPercent}%`, background: 'var(--accent-success)', height: '100%' }} title={`Passing: ${passPercent}%`}></div>
          <div style={{ width: `${failPercent}%`, background: 'var(--accent-danger)', height: '100%' }} title={`Failing: ${failPercent}%`}></div>
          <div style={{ width: `${pendingPercent}%`, background: 'var(--accent-primary)', height: '100%' }} title={`Not Run: ${pendingPercent}%`}></div>
          <div style={{ width: `${uncoverPercent}%`, background: 'rgba(255,255,255,0.1)', height: '100%' }} title={`Uncovered: ${uncoverPercent}%`}></div>
        </div>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto', flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Coverage Status Matrix</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-glass)', color: 'var(--text-secondary)' }}>
              <th style={{ padding: '0.75rem 1rem' }}>Requirement</th>
              <th style={{ padding: '0.75rem 1rem' }}>Test Case</th>
              <th style={{ padding: '0.75rem 1rem' }}>Coverage State</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {reqList.map((req: any) => {
              const test = req.tests && req.tests[0];
              return (
                <tr key={req.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', background: 'rgba(255,255,255,0.01)' }}>
                  <td style={{ padding: '1rem' }}>
                    <div style={{ fontWeight: 600, color: 'white' }}>{req.id}</div>
                    <div className="text-muted" style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>{req.title}</div>
                  </td>
                  <td style={{ padding: '1rem', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                    {test ? (
                      <div style={{ color: 'var(--accent-primary)' }}>🧪 {test.name}</div>
                    ) : (
                      <div style={{ color: 'var(--text-muted)' }}>None Linked</div>
                    )}
                  </td>
                  <td style={{ padding: '1rem' }}>
                    {req.coverage_state === 'passing' && (
                      <span 
                        className="badge" 
                        style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-success)', cursor: test ? 'pointer' : 'default' }}
                        title={test ? 'Click to view test details' : undefined}
                        onClick={() => test && setSelectedTestDetails({ ...test, coverage_state: 'passing' })}
                      >
                        Passing
                      </span>
                    )}
                    {req.coverage_state === 'failing' && (
                      <span 
                        className="badge" 
                        style={{ background: 'rgba(239, 68, 68, 0.15)', color: 'var(--accent-danger)', cursor: test ? 'pointer' : 'default' }}
                        title={test ? 'Click to view failure details' : undefined}
                        onClick={() => test && setSelectedTestDetails({ ...test, coverage_state: 'failing' })}
                      >
                        Failing
                      </span>
                    )}
                    {req.coverage_state === 'pending' && (
                      <span 
                        className="badge" 
                        style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-primary)', cursor: test ? 'pointer' : 'default' }}
                        title={test ? 'Click to view test details' : undefined}
                        onClick={() => test && setSelectedTestDetails({ ...test, coverage_state: 'pending' })}
                      >
                        Not Run
                      </span>
                    )}
                    {req.coverage_state === 'uncovered' && (
                      <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)' }}>Not Covered</span>
                    )}
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', alignItems: 'center' }}>
                      {test && (
                        <button
                          className="btn btn-outline"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderColor: 'var(--accent-primary)', color: 'var(--accent-primary)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                          onClick={() => handleRerunTest(test.id)}
                          disabled={runningAll || Object.values(runningTests).some(Boolean) || agentStatus.active}
                        >
                          {runningTests[test.id] ? (
                            <>
                              <div className="spinner" style={{ border: '2px solid rgba(255,255,255,0.1)', borderTopColor: 'white', borderRadius: '50%', width: '10px', height: '10px', animation: 'spin 1s linear infinite' }}></div>
                              Running...
                            </>
                          ) : (
                            '🔄 Rerun'
                          )}
                        </button>
                      )}

                      {req.coverage_state === 'uncovered' && (
                        <button 
                          className="btn btn-outline" 
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderColor: 'var(--accent-success)', color: 'var(--accent-success)' }}
                          onClick={() => {
                            setCurrentView('Requirements');
                            setSelectedReqId(req.id);
                          }}
                        >
                          Create Test
                        </button>
                      )}
                      {req.coverage_state === 'failing' && (
                        agentStatus.active ? (
                          isReqFixing(req.id) ? (
                            <button
                              className="btn btn-outline"
                              style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderColor: 'var(--text-muted)', color: 'var(--text-muted)', cursor: 'not-allowed' }}
                              disabled
                            >
                              ⚙️ Fixing...
                            </button>
                          ) : (
                            <button
                              className="btn btn-outline"
                              style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderColor: 'var(--text-muted)', color: 'var(--text-muted)', cursor: 'not-allowed' }}
                              disabled
                              title="Agent is busy working on another ticket"
                            >
                              Fix Failing Test
                            </button>
                          )
                        ) : (
                          <button
                            className="btn btn-outline"
                            style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderColor: 'var(--accent-warning)', color: 'var(--accent-warning)' }}
                            onClick={async () => {
                              try {
                                const res = await fetch(`/api/requirements/${req.id}/fix-test-case`, { method: 'POST' });
                                const data = await res.json();
                                if (data.success) {
                                  await fetchReqs();
                                  await fetchCoverage();
                                } else {
                                  console.error('Failed to fix test case:', data.error);
                                }
                              } catch (e) {
                                console.error('Network error while trying to fix test case:', e);
                              }
                            }}
                          >
                            Fix Failing Test
                          </button>
                        )
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Allure Detail Embed */}
      <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem', flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Allure Test Report Dashboard</h3>
            <p className="text-muted" style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem' }}>View complete test history, execution trends, and screenshots below.</p>
          </div>
          <button
            className="btn btn-outline"
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            onClick={handleRerunAll}
            disabled={runningAll || Object.values(runningTests).some(Boolean) || agentStatus.active}
          >
            {runningAll ? (
              <>
                <div className="spinner" style={{ border: '2px solid rgba(255,255,255,0.1)', borderTopColor: 'white', borderRadius: '50%', width: '12px', height: '12px', animation: 'spin 1s linear infinite' }}></div>
                Running Suite...
              </>
            ) : (
              '🔄 Rerun All Tests'
            )}
          </button>
        </div>
        <div style={{ width: '100%', height: '600px', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-glass)' }}>
          <iframe 
            key={allureKey}
            src={allure_report_url} 
            style={{ width: '100%', height: '100%', border: 'none', background: '#1e293b' }} 
            title="Allure Report" 
          />
        </div>
      </div>
      {/* Test Case Details Modal */}
      {selectedTestDetails && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(5px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            padding: '2rem'
          }}
          onClick={() => setSelectedTestDetails(null)}
        >
          <div 
            className="glass-card" 
            style={{ 
              maxWidth: '800px', 
              width: '100%', 
              maxHeight: '85vh', 
              overflowY: 'auto', 
              padding: '2rem', 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '1.5rem',
              boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'white' }}>{selectedTestDetails.id}</span>
                <span className="badge" style={{ 
                  background: selectedTestDetails.coverage_state === 'passing' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', 
                  color: selectedTestDetails.coverage_state === 'passing' ? 'var(--accent-success)' : 'var(--accent-danger)' 
                }}>
                  {selectedTestDetails.coverage_state === 'passing' ? 'Passing' : 'Failing'}
                </span>
              </div>
              <button 
                onClick={() => setSelectedTestDetails(null)} 
                style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', fontSize: '1.5rem', cursor: 'pointer' }}
              >
                &times;
              </button>
            </div>

            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Test Case Name</div>
              <div style={{ fontWeight: 600, color: 'white', fontFamily: 'monospace' }}>{selectedTestDetails.name}</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <div>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>GIVEN:</span> {selectedTestDetails.given}
              </div>
              <div>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>WHEN:</span> {selectedTestDetails.when}
              </div>
              <div>
                <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold' }}>THEN:</span> {selectedTestDetails.then}
              </div>
            </div>

            {selectedTestDetails.coverage_state === 'failing' && (
              <div>
                <div style={{ fontSize: '0.8rem', color: 'var(--accent-danger)', textTransform: 'uppercase', marginBottom: '0.5rem', fontWeight: 'bold' }}>Failure Details</div>
                <pre 
                  style={{ 
                    background: 'rgba(239, 68, 68, 0.05)', 
                    border: '1px solid rgba(239, 68, 68, 0.2)', 
                    borderRadius: '8px', 
                    padding: '1rem', 
                    color: '#f87171', 
                    fontFamily: 'monospace', 
                    fontSize: '0.8rem', 
                    overflowX: 'auto', 
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-all'
                  }}
                >
                  {selectedTestDetails.failureMessage || "No traceback recorded. Rerun the test to capture details."}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CoverageHub;
