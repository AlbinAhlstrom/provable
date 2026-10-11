import { useState } from 'react';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import KickstartStudio from './components/KickstartStudio';
import ProjectSelector from './components/ProjectSelector';

export function ProvableApp() {
  const [projectKey, setProjectKey] = useState<number>(0);  // the studio starts over when the project changes

  return (
    <div className="app-container">
      <header className="app-header-nav">
        <div className="nav-logo"><RocketLaunchIcon fontSize="inherit" /><span className="gradient-text">Provable Studio</span></div>
        <div style={{ marginLeft: 'auto' }}>
          <ProjectSelector onProjectSwitch={() => setProjectKey(k => k + 1)} />
        </div>
      </header>

      <main className="main-content">
        <KickstartStudio key={projectKey} />
      </main>
    </div>
  );
}

export default ProvableApp;
