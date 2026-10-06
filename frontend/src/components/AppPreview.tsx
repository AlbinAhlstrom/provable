import { useState } from 'react';
import { RequirementControlPanel } from './RequirementControlPanel';

export interface AppPreviewProps {
  onResetWorkspace?: () => void;
  resetting?: boolean;
  resetMessage?: string | null;
}

export function AppPreview({ onResetWorkspace, resetting, resetMessage }: AppPreviewProps = {}) {
  const [layoutMode, setLayoutMode] = useState<'full' | 'split'>('split');
  const [deviceMode, setDeviceMode] = useState<'desktop' | 'mobile'>('desktop');
  const [fitToView, setFitToView] = useState<boolean>(false);
  const [key, setKey] = useState(0);
  const [internalResetting, setInternalResetting] = useState<boolean>(false);
  const [internalResetMessage, setInternalResetMessage] = useState<string | null>(null);

  const previewUrl = 'http://localhost:5174';

  const handleReset = async () => {
    if (onResetWorkspace) {
      onResetWorkspace();
      return;
    }
    setInternalResetting(true);
    setInternalResetMessage(null);
    try {
      const res = await fetch('/api/onboarding/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setKey(prev => prev + 1);
        setInternalResetMessage("✨ Active workspace wiped successfully.");
        setTimeout(() => setInternalResetMessage(null), 3000);
      } else {
        setInternalResetMessage("⚠️ Reset notice: " + (data.error || 'Unknown notice'));
      }
    } catch (err) {
      setInternalResetMessage("❌ Network notice resetting projects.");
    } finally {
      setInternalResetting(false);
    }
  };

  const isResettingState = resetting !== undefined ? resetting : internalResetting;
  const activeResetMessage = resetMessage !== undefined ? resetMessage : internalResetMessage;

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0, overflow: 'hidden', boxSizing: 'border-box' }}>
      {/* Main View Container: Dynamic Split or Full View */}
      <div 
        className="app-preview-container"
        style={{ flex: 1, display: 'flex', minHeight: 0, height: '100%', overflow: 'hidden', width: '100%', gap: '0.75rem', boxSizing: 'border-box' }}
      >
        {/* Left Pane: Live Workspace App */}
        <div 
          style={{ 
            flex: layoutMode === 'full' ? '1 1 100%' : '1 1 50%', 
            width: layoutMode === 'full' ? '100%' : '50%',
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column', 
            minHeight: 0, 
            overflow: 'hidden', 
            background: '#0b0f19',
            borderRadius: '0.75rem',
            border: '1px solid #334155',
            transition: 'flex 0.2s ease, width 0.2s ease'
          }}
        >
          {/* Live App Navigation, Device Bar & Reset Workspace */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0.45rem 0.85rem',
            background: '#1e293b',
            borderBottom: '1px solid #334155',
            fontSize: '0.8rem',
            flexShrink: 0
          }}>
            {/* Left: Port indicator & Reset Workspace Action */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ color: '#10b981', fontWeight: 700, fontSize: '0.78rem' }}>🟢 Live Workspace (:5174)</span>
              <button
                onClick={handleReset}
                disabled={isResettingState}
                style={{
                  background: '#991b1b',
                  color: '#fca5a5',
                  border: '1px solid #dc2626',
                  padding: '0.2rem 0.65rem',
                  borderRadius: '0.4rem',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: isResettingState ? 'not-allowed' : 'pointer',
                  opacity: isResettingState ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem'
                }}
                title="Wipe workspace and reset database"
              >
                {isResettingState ? '⏳ Resetting...' : '🗑️ Reset Workspace'}
              </button>
              {activeResetMessage && (
                <span style={{ fontSize: '0.75rem', color: activeResetMessage.includes('✨') ? '#4ade80' : '#f87171' }}>
                  {activeResetMessage}
                </span>
              )}
            </div>

            {/* Right: Layout Switcher, Device Mode, Fit to Viewport, Reload & Open external */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <div style={{ display: 'flex', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '0.1rem', gap: '0.15rem' }}>
                <button
                  onClick={() => { setLayoutMode('full'); setDeviceMode('desktop'); }}
                  style={{
                    background: layoutMode === 'full' && deviceMode === 'desktop' ? '#0284c7' : 'transparent',
                    color: '#fff',
                    border: 'none',
                    padding: '0.2rem 0.45rem',
                    borderRadius: '3px',
                    fontSize: '0.7rem',
                    cursor: 'pointer',
                    fontWeight: 600
                  }}
                  title="Full Desktop Preview (100% width)"
                >
                  🖥️ Full View
                </button>
                <button
                  onClick={() => { setLayoutMode('split'); setDeviceMode('desktop'); }}
                  style={{
                    background: layoutMode === 'split' && deviceMode === 'desktop' ? '#0284c7' : 'transparent',
                    color: '#fff',
                    border: 'none',
                    padding: '0.2rem 0.45rem',
                    borderRadius: '3px',
                    fontSize: '0.7rem',
                    cursor: 'pointer',
                    fontWeight: 600
                  }}
                  title="Split Cockpit (50/50 with BDD Control Panel)"
                >
                  🌗 Split View
                </button>
                <button
                  onClick={() => setDeviceMode('mobile')}
                  style={{
                    background: deviceMode === 'mobile' ? '#0284c7' : 'transparent',
                    color: '#fff',
                    border: 'none',
                    padding: '0.2rem 0.45rem',
                    borderRadius: '3px',
                    fontSize: '0.7rem',
                    cursor: 'pointer',
                    fontWeight: 600
                  }}
                  title="Mobile Preview (375px)"
                >
                  📱 375px
                </button>
              </div>

              <button
                onClick={() => setFitToView(f => !f)}
                style={{
                  background: fitToView ? '#0284c7' : '#0f172a',
                  border: `1px solid ${fitToView ? '#38bdf8' : '#475569'}`,
                  color: fitToView ? '#ffffff' : '#cbd5e1',
                  padding: '0.2rem 0.45rem',
                  borderRadius: '4px',
                  fontSize: '0.7rem',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
                title="Scale canvas to fit viewport without scrollbars"
              >
                🔍 {fitToView ? 'Fit: ON' : 'Fit: OFF'}
              </button>
              <button
                onClick={() => setKey(k => k + 1)}
                style={{
                  background: '#0f172a',
                  border: '1px solid #475569',
                  color: '#f8fafc',
                  padding: '0.2rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.72rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem'
                }}
                title="Reload Live App iframe"
              >
                🔄
              </button>
              <button
                onClick={() => window.open(previewUrl, '_blank')}
                style={{
                  background: '#0284c7',
                  border: 'none',
                  color: '#ffffff',
                  padding: '0.2rem 0.55rem',
                  borderRadius: '4px',
                  fontSize: '0.72rem',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
                title="Open live app in new browser tab"
              >
                ↗
              </button>
            </div>
          </div>

          {/* Embed Workspace Vite App */}
          <div style={{ flex: 1, width: '100%', height: '100%', minHeight: 0, overflow: 'hidden', display: 'flex', justifyContent: 'center', alignItems: 'flex-start', background: '#090d16' }}>
            <iframe
              key={`workspace-iframe-${key}`}
              src="http://localhost:5174"
              title="Workspace Live App"
              style={{
                width: deviceMode === 'mobile' ? '375px' : '100%',
                height: '100%',
                border: deviceMode === 'mobile' ? '1px solid #334155' : 'none',
                boxShadow: deviceMode === 'mobile' ? '0 25px 50px -12px rgba(0, 0, 0, 0.7)' : 'none',
                display: 'block',
                background: '#0f172a',
                transition: 'width 0.2s ease, transform 0.2s ease',
                transform: fitToView ? 'scale(0.85)' : 'none',
                transformOrigin: 'top center'
              }}
            />
          </div>
        </div>

        {/* Right Pane: Domain Specifications (BDD Requirements) - Active only in Split View */}
        {layoutMode === 'split' && (
          <div 
            style={{ 
              flex: '1 1 50%', 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column', 
              minHeight: 0, 
              overflow: 'hidden'
            }}
          >
            <RequirementControlPanel fullWidth={true} onParamUpdated={() => setKey(k => k + 1)} />
          </div>
        )}
      </div>
    </div>
  );
}

export default AppPreview;
