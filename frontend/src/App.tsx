import { useState } from 'react';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import KickstartStudio from './components/KickstartStudio';
import ProjectSelector from './components/ProjectSelector';
import LlmKeyButton from './components/LlmKeyButton';
import { AccountButton } from './AuthGate';

export function ProvableApp() {
  const [projectKey, setProjectKey] = useState<number>(0);  // the studio starts over when the project changes

  return (
    <div className="app-container">
      <header className="app-header-nav">
        <div className="nav-logo"><RocketLaunchIcon fontSize="inherit" /><span className="gradient-text">Provable Studio</span></div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12 }}>
          <ProjectSelector onProjectSwitch={() => setProjectKey(k => k + 1)} />
          <LlmKeyButton />
          <AccountButton />
        </div>
      </header>

      <main className="main-content">
        <KickstartStudio key={projectKey} />
      </main>
    </div>
  );
}

export default ProvableApp;
