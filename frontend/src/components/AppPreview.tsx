import { useState, useEffect } from 'react';
import { RequirementControlPanel } from './RequirementControlPanel';
import { PageSelectorBar } from './PageSelectorBar';
import { PageDTO } from '../types/api';

export interface AppPreviewProps {
  onResetWorkspace?: () => void;
  resetting?: boolean;
  resetMessage?: string | null;
}

export function AppPreview({ onResetWorkspace, resetting, resetMessage }: AppPreviewProps = {}) {
  const [targetPort, setTargetPort] = useState<'5174' | '8000'>('5174');
  const [deviceMode, setDeviceMode] = useState<'desktop' | 'tablet' | 'mobile'>('mobile');
  const [key, setKey] = useState(0);
  const [isSynthesized, setIsSynthesized] = useState<boolean>(false);
  const [internalResetting, setInternalResetting] = useState<boolean>(false);
  const [internalResetMessage, setInternalResetMessage] = useState<string | null>(null);

  // Pages & Views Navigation State
  const [pages, setPages] = useState<PageDTO[]>([
    { id: 'home', name: 'Home Page', route: '/', icon: '🏠', is_home: true },
    { id: 'checkout', name: 'Checkout Page', route: '/checkout', icon: '💳' },
    { id: 'tracking', name: 'Order Tracking View', route: '/tracking', icon: '📦' }
  ]);
  const [activePageId, setActivePageId] = useState<string>('home');

  const previewUrl = targetPort === '5174' ? 'http://localhost:5174' : 'http://localhost:8000/';

  const handleAddPage = (name: string, route: string) => {
    const newPage: PageDTO = {
      id: name.toLowerCase().replace(/[^a-z0-9_]/g, '_'),
      name,
      route,
      icon: '📄'
    };
    setPages(prev => [...prev, newPage]);
    setActivePageId(newPage.id);
  };

  const handleDeletePage = (pageId: string) => {
    setPages(prev => prev.filter(p => p.id !== pageId));
    if (activePageId === pageId) {
      setActivePageId('home');
    }
  };

  useEffect(() => {
    const fetchState = async () => {
      try {
        const res = await fetch('/api/kickstart/state');
        const data = await res.json();
        if (data && typeof data.synthesized === 'boolean') {
          setIsSynthesized(data.synthesized);
        }
      } catch (err) {
        console.error("Failed to fetch kickstart state in AppPreview:", err);
      }
    };
    fetchState();
    const interval = setInterval(fetchState, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleReset = async () => {
    if (onResetWorkspace) {
      onResetWorkspace();
      return;
    }
    setInternalResetting(true);
    setInternalResetMessage(null);
    try {
      const res = await fetch('/api/projects/reset-all', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
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

  const getWidth = () => {
    switch (deviceMode) {
      case 'mobile': return '375px';
      case 'tablet': return '768px';
      default: return '100%';
    }
  };

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', flex: 1, boxSizing: 'border-box' }}>
      {/* Workspace Control Bar */}
      <div 
        className="app-preview-controls-bar"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#0f172a',
          border: '1px solid #334155',
          borderRadius: '0.75rem',
          padding: '0.5rem 1rem',
          marginBottom: '1rem',
          gap: '1rem',
          flexWrap: 'wrap'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {activeResetMessage && (
            <span style={{ fontSize: '0.8rem', color: activeResetMessage.includes('✨') ? '#4ade80' : '#f87171' }}>
              {activeResetMessage}
            </span>
          )}
          <button
            onClick={handleReset}
            disabled={isResettingState}
            style={{
              background: '#991b1b',
              color: '#fca5a5',
              border: '1px solid #dc2626',
              padding: '0.4rem 0.85rem',
              borderRadius: '0.5rem',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: isResettingState ? 'not-allowed' : 'pointer',
              opacity: isResettingState ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            {isResettingState ? '⏳ Resetting...' : '🗑️ Reset Workspace'}
          </button>
        </div>

        {/* Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Target Port Selector */}
          <div style={{ display: 'flex', background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.2rem' }}>
            <button
              onClick={() => setTargetPort('5174')}
              style={{
                background: targetPort === '5174' ? '#0284c7' : 'transparent',
                color: '#f8fafc',
                border: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Preview
            </button>
            <button
              onClick={() => setTargetPort('8000')}
              style={{
                background: targetPort === '8000' ? '#0284c7' : 'transparent',
                color: '#f8fafc',
                border: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              API
            </button>
          </div>

          {/* Device Frame Selector */}
          <div style={{ display: 'flex', background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.2rem' }}>
            <button
              onClick={() => setDeviceMode('desktop')}
              style={{ background: deviceMode === 'desktop' ? '#334155' : 'transparent', color: '#f8fafc', border: 'none', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer' }}
              title="Desktop View"
            >
              🖥️
            </button>
            <button
              onClick={() => setDeviceMode('tablet')}
              style={{ background: deviceMode === 'tablet' ? '#334155' : 'transparent', color: '#f8fafc', border: 'none', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer' }}
              title="Tablet View"
            >
              📱
            </button>
            <button
              onClick={() => setDeviceMode('mobile')}
              style={{ background: deviceMode === 'mobile' ? '#334155' : 'transparent', color: '#f8fafc', border: 'none', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer' }}
              title="Mobile View"
            >
              📲
            </button>
          </div>

          {/* Action Buttons */}
          <button
            onClick={() => setKey(k => k + 1)}
            style={{ background: '#334155', color: '#f8fafc', border: 'none', padding: '0.45rem 0.85rem', borderRadius: '0.5rem', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
            title="Refresh Preview"
          >
            🔄
          </button>
          <button
            onClick={() => window.open(previewUrl, '_blank')}
            style={{ background: '#0284c7', color: 'white', border: 'none', padding: '0.45rem 0.85rem', borderRadius: '0.5rem', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
          >
            ↗ Open in New Tab
          </button>
        </div>
      </div>

      {/* Pillar 1: Top Pages & Views Selector Bar */}
      {isSynthesized && (
        <PageSelectorBar
          pages={pages}
          activePageId={activePageId}
          onSelectPage={setActivePageId}
          onAddPage={handleAddPage}
          onDeletePage={handleDeletePage}
        />
      )}

      {/* Main Container: Live Preview Iframe + Conditional Side Requirement Control Panel */}
      <div 
        className="app-preview-split"
        style={{ flex: 1, display: 'flex', gap: '1rem', minHeight: 0, overflow: 'hidden', width: '100%' }}
      >
        {/* Frame Container */}
        <div 
          className="app-preview-frame-container"
          style={{
            width: deviceMode === 'desktop' ? '100%' : getWidth(),
            flex: deviceMode === 'desktop' ? 1 : `0 0 ${getWidth()}`,
            maxWidth: deviceMode === 'desktop' ? '100%' : getWidth(),
            display: 'flex',
            justifyContent: 'center',
            background: '#090d16',
            borderRadius: '0.75rem',
            border: '1px solid #334155',
            padding: '0.5rem',
            overflow: 'hidden',
            transition: 'all 0.3s ease',
            boxSizing: 'border-box'
          }}
        >
          <iframe
            key={key}
            src={previewUrl}
            title="Live Application Preview"
            style={{
              width: '100%',
              height: '100%',
              border: '1px solid #334155',
              borderRadius: '0.5rem',
              background: '#0f172a'
            }}
          />
        </div>

        {/* Render Side Control Panel ONLY when an application has been synthesized */}
        {isSynthesized && (
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <RequirementControlPanel onParamUpdated={() => setKey(k => k + 1)} />
          </div>
        )}
      </div>
    </div>
  );
}


