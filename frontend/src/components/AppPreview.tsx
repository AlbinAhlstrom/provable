import { ReactNode, useEffect, useRef, useState } from 'react';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import RefreshIcon from '@mui/icons-material/Refresh';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { RequirementControlPanel } from './RequirementControlPanel';
import { StatusMessage, StudioMessage } from './StatusMessage';

const PREVIEW_URL = 'http://localhost:5174';  // the generated app's own dev server

export interface AppPreviewProps {
  onResetWorkspace: () => void;
  resetting: boolean;
  message: StudioMessage | null;
  banner?: ReactNode;      // shown above the preview, e.g. what a running build is still working on
  reloadToken?: number;    // the preview reloads when this changes
  building?: boolean;      // a build is running: the preview is shown as being worked on
  testingIds?: string[];   // the specs the running build is working on
}

/** The generated app beside its specifications; stacked, with a square preview, on a narrow screen. */
export function AppPreview({ onResetWorkspace, resetting, message, banner, reloadToken = 0, building = false, testingIds }: AppPreviewProps) {
  const [key, setKey] = useState(0);
  const [justFinished, setJustFinished] = useState(false);  // the build ended a moment ago: the app steps forward
  const wasBuilding = useRef(building);

  useEffect(() => {
    if (wasBuilding.current && !building) setJustFinished(true);
    wasBuilding.current = building;
  }, [building]);

  const frameState = building ? ' preview-frame-building' : justFinished ? ' preview-frame-finished' : '';

  return (
    <div className="app-preview">
      {banner}
      <div className="app-preview-container">
        <section className="preview-pane">
          <div className="preview-toolbar">
            <h3 className="panel-title">Live workspace</h3>
            <div className="preview-toolbar-actions">
              <button className="tool-btn tool-btn-danger" onClick={onResetWorkspace} disabled={resetting} title="Wipe the workspace and reset the database">
                {resetting ? <span className="spinner" /> : <RestartAltIcon fontSize="inherit" />}
                {resetting ? 'Resetting…' : 'Reset'}
              </button>
              <button className="tool-btn" onClick={() => setKey(k => k + 1)} title="Reload the app" aria-label="Reload the app">
                <RefreshIcon fontSize="inherit" />
              </button>
              <button className="tool-btn" onClick={() => window.open(PREVIEW_URL, '_blank')} title="Open the app in a new tab" aria-label="Open the app in a new tab">
                <OpenInNewIcon fontSize="inherit" />
              </button>
            </div>
          </div>
          {message && <StatusMessage message={message} />}
          <div className={`preview-frame${frameState}`} onAnimationEnd={event => { if (event.animationName === 'preview-pop') setJustFinished(false); }}>
            <iframe key={`workspace-iframe-${key}-${reloadToken}`} src={PREVIEW_URL} title="Workspace live app" />
          </div>
        </section>

        <section className="specs-pane">
          <RequirementControlPanel onSpecsChanged={() => setKey(k => k + 1)} building={building} testingIds={testingIds} />
        </section>
      </div>
    </div>
  );
}

export default AppPreview;
