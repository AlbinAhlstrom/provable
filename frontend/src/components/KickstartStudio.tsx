import React, { useState, useEffect, useRef } from 'react';
import { AppPreview } from './AppPreview';
import { BuildProgress, BuildProgressScreen, BuildProgressStrip } from './BuildProgressPanel';
import { StatusMessage, StudioMessage } from './StatusMessage';

const PROGRESS_POLL_MS = 1500;       // while a build runs
const IDLE_PROGRESS_POLL_MS = 4000;  // to notice a build started elsewhere (another tab, the API)

const fetchProgress = async (): Promise<BuildProgress | null> => {
  const res = await fetch('/api/onboarding/progress');
  return res.ok ? res.json() : null;
};

export const KickstartStudio: React.FC = () => {
  const [pitch, setPitch] = useState<string>('');
  const [building, setBuilding] = useState<boolean>(false);
  const [resetting, setResetting] = useState<boolean>(false);
  const [message, setMessage] = useState<StudioMessage | null>(null);
  const [synthesized, setSynthesized] = useState<boolean>(false);
  const [llmConfigured, setLlmConfigured] = useState<boolean>(true);
  const [progress, setProgress] = useState<BuildProgress | null>(null);
  const [reloadToken, setReloadToken] = useState<number>(0);
  const followedBuild = useRef<boolean>(false);  // the running build has been seen at least once

  const checkState = async () => {
    try {
      const res = await fetch('/api/kickstart/state');
      const state = await res.json();
      if (state) {
        if (state.business_pitch) setPitch(state.business_pitch);
        if (typeof state.synthesized === 'boolean') setSynthesized(state.synthesized);
        if (typeof state.llm_configured === 'boolean') setLlmConfigured(state.llm_configured);
      }
    } catch (err) {
      console.error("Failed to fetch kickstart state:", err);
    }
  };

  useEffect(() => {
    checkState();
  }, []);

  // Ask what the running build has delivered so far; the app is shown as soon as its page is written. A build this
  // page did not start (it was reloaded, or the build came from elsewhere) is picked up the same way.
  useEffect(() => {
    const poll = async () => {
      try {
        const next = await fetchProgress();
        if (!next) return;
        if (next.building) {
          followedBuild.current = true;
          setProgress(next);
          setBuilding(true);
        } else if (followedBuild.current) {
          // The build this page was following has ended
          followedBuild.current = false;
          setBuilding(false);
          setProgress(null);
          setReloadToken(t => t + 1);
          checkState();
        }
      } catch (err) {
        console.error("Failed to fetch build progress:", err);
      }
    };
    poll();
    const timer = setInterval(poll, building ? PROGRESS_POLL_MS : IDLE_PROGRESS_POLL_MS);
    return () => clearInterval(timer);
  }, [building]);

  const triggerSynthesis = async () => {
    if (!pitch.trim()) return;
    followedBuild.current = false;
    setBuilding(true);
    setProgress(null);
    setMessage(null);
    try {
      const res = await fetch('/api/onboarding/kickstart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pitch: pitch.trim(),
          mode: 'fast'
        })
      });
      let data: any = {};
      try {
        data = await res.json();
      } catch {
        data = { error: `Server returned HTTP ${res.status}` };
      }

      const run = data.run_id ? ` (run ${data.run_id})` : '';
      if (res.ok && data.success) {
        setSynthesized(true);
        const failures: { stage: string; error: string }[] = data.stage_failures || [];
        setMessage(failures.length
          ? { severity: 'warning', text: `Built with problems. ${failures.map(f => `${f.stage}: ${f.error}`).join(' | ')}${run}` }
          : { severity: 'success', text: `Built${data.timing_breakdown?.total ? ` in ${Math.round(data.timing_breakdown.total)}s` : ''}${run}` });
      } else {
        setMessage({ severity: 'error', text: `Build failed: ${data.error || data.detail || data.message || `HTTP ${res.status}`}` });
      }
    } catch (err: any) {
      console.error("Build failed:", err);
      setMessage({ severity: 'error', text: `Could not reach the server${err?.message ? `: ${err.message}` : ''}` });
    } finally {
      setBuilding(false);
      setProgress(null);
      setReloadToken(t => t + 1);
    }
  };

  const handleResetAllProjects = async () => {
    setResetting(true);
    setMessage(null);
    try {
      const res = await fetch('/api/onboarding/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSynthesized(false);
        setMessage({ severity: 'success', text: 'Workspace reset.' });
        setTimeout(() => setMessage(null), 3000);
      } else {
        setMessage({ severity: 'error', text: `Reset failed: ${data.error || `HTTP ${res.status}`}` });
      }
    } catch (err: any) {
      setMessage({ severity: 'error', text: `Could not reach the server${err?.message ? `: ${err.message}` : ''}` });
    } finally {
      setResetting(false);
    }
  };

  // ── VIEW 0: A BUILD IS RUNNING AND THERE IS NO APP TO SHOW YET ─────────────────
  if (building && !progress?.draft_ready) {
    return <BuildProgressScreen progress={progress} />;
  }

  // ── VIEW 2: LIVE APP VIEW (ALSO WHILE THE BUILD CONTINUES BEHIND IT) ───────────
  if (synthesized || building) {
    return (
      <AppPreview
        onResetWorkspace={handleResetAllProjects}
        resetting={resetting}
        message={message}
        reloadToken={reloadToken}
        banner={building && progress ? <BuildProgressStrip progress={progress} /> : undefined}
      />
    );
  }

  // ── VIEW 1: NOTHING BUILT YET ──────────────────────────────────────────────────
  return (
    <div className="kickstart">
      <h1 className="kickstart-title">Provable</h1>
      {message && <StatusMessage message={message} />}
      {!llmConfigured && (
        <div className="status-message status-message-warning">
          No LLM API key is configured. Set <code>GEMINI_API_KEY</code>, <code>OPENAI_API_KEY</code> or <code>LLM_API_KEY</code> in <code>.env</code> to build.
        </div>
      )}
      <textarea
        className="kickstart-pitch"
        value={pitch}
        onChange={e => setPitch(e.target.value)}
        placeholder="Describe the app you want to build"
        aria-label="Describe the app you want to build"
        rows={4}
      />
      <button className="btn btn-primary kickstart-build" onClick={triggerSynthesis} disabled={building || !pitch.trim()}>
        Build
      </button>
    </div>
  );
};

export default KickstartStudio;
