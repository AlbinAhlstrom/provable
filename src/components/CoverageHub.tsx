import React from 'react';
import { Requirement } from '../hooks/useRequirements';

interface CoverageHubProps {
  coverageData: any;
  requirements: Requirement[];
  setCurrentView: (view: string) => void;
  setSelectedReqId: (id: string | null) => void;
  fetchReqs: () => Promise<void>;
  fetchCoverage: () => Promise<void>;
}

const CoverageHub: React.FC<CoverageHubProps> = ({
  coverageData,
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
  const total = summary.total_requirements || 0;
  const passing = summary.passing || 0;
  const failing = summary.failing || 0;
  const uncovered = summary.uncovered || 0;
  
  const passPercent = total > 0 ? Math.round((passing / total) * 100) : 0;
  const failPercent = total > 0 ? Math.round((failing / total) * 100) : 0;
  const uncoverPercent = total > 0 ? Math.round((uncovered / total) * 100) : 0;

  return (
    <div className="glass-panel" style={{ padding: '2rem', overflowY: 'auto', height: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2 style={{ margin: 0, fontSize: '1.8rem', background: 'linear-gradient(135deg, #fff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Requirements Coverage Hub</h2>
        <p className="text-muted" style={{ margin: '0.5rem 0 0 0' }}>Track requirement verification, test execution, and history in real-time.</p>
      </div>

      {/* Coverage Progress Bar & Aggregates */}
      <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
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
          <div style={{ width: `${uncoverPercent}%`, background: 'rgba(255,255,255,0.1)', height: '100%' }} title={`Uncovered: ${uncoverPercent}%`}></div>
        </div>
      </div>

      {/* Coverage Grid Table */}
      <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
        <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem' }}>Coverage Status Matrix</h3>
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
                      <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-success)' }}>Passing</span>
                    )}
                    {req.coverage_state === 'failing' && (
                      <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.15)', color: 'var(--accent-danger)' }}>Failing</span>
                    )}
                    {req.coverage_state === 'uncovered' && (
                      <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)' }}>Not Covered</span>
                    )}
                  </td>
                  <td style={{ padding: '1rem', textAlign: 'right' }}>
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
                      <button 
                        className="btn btn-outline" 
                        style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', borderColor: 'var(--accent-warning)', color: 'var(--accent-warning)' }}
                        onClick={async () => {
                          alert(`Creating Jira ticket and dispatching Agent to fix failing test for {req.id}...`);
                          try {
                            const res = await fetch(`/api/requirements/${req.id}/fix-test-case`, { method: 'POST' });
                            const data = await res.json();
                            if (data.success) {
                              alert(`Successfully created Jira ticket ${data.jira_key}! Agent dispatched.`);
                              await fetchReqs();
                              await fetchCoverage();
                            } else {
                              alert(`Failed to fix test case: ${data.error}`);
                            }
                          } catch (e) {
                            console.error(e);
                            alert("Network error while trying to fix test case.");
                          }
                        }}
                      >
                        Fix Failing Test
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Allure Detail Embed */}
      <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Allure Test Report Dashboard</h3>
        <p className="text-muted" style={{ margin: 0, fontSize: '0.85rem' }}>View complete test history, execution trends, and screenshots below.</p>
        <div style={{ width: '100%', height: '600px', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-glass)' }}>
          <iframe 
            src={allure_report_url} 
            style={{ width: '100%', height: '100%', border: 'none', background: '#1e293b' }} 
            title="Allure Report" 
          />
        </div>
      </div>
    </div>
  );
};

export default CoverageHub;
