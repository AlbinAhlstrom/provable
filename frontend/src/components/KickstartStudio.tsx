import React, { useState, useEffect, useRef } from 'react';
import { AppPreview } from './AppPreview';
import { BuildOpening } from './BuildOpening';
import { BuildProgress, BuildProgressBanner } from './BuildProgressPanel';
import { LLM_KEY_CHANGED } from './LlmKeyButton';
import { StudioMessage } from './StatusMessage';

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
  const [keyManaged, setKeyManaged] = useState<boolean>(false);  // a hosted engine: each user brings their own key
  const [progress, setProgress] = useState<BuildProgress | null>(null);
  const [reloadToken, setReloadToken] = useState<number>(0);
  const followedBuild = useRef<boolean>(false);  // the running build has been seen at least once
  const shownReady = useRef<boolean>(false);     // the running build's finished app is already on screen

  const checkState = async () => {
    try {
      const res = await fetch('/api/kickstart/state');
      const state = await res.json();
      if (state) {
        if (state.business_pitch) setPitch(state.business_pitch);
        if (typeof state.synthesized === 'boolean') setSynthesized(state.synthesized);
        if (typeof state.llm_configured === 'boolean') setLlmConfigured(state.llm_configured);
        setKeyManaged(Boolean(state.llm_key_managed));
        if (state.llm_key_managed) {
          const key = await (await fetch('/api/llm-key')).json();
          setLlmConfigured(Boolean(key.configured));
        }
      }
    } catch (err) {
      console.error("Failed to fetch kickstart state:", err);
    }
  };

  useEffect(() => {
    checkState();
    const again = () => { checkState(); };
    window.addEventListener(LLM_KEY_CHANGED, again);
    return () => window.removeEventListener(LLM_KEY_CHANGED, again);
  }, []);

  // Ask what the running build has delivered so far. A build this
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
          showFinishedApp();
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

  // The live workspace comes on screen with the build's first draft; show what it has become each time the build
  // delivers something more to look at (the written page, the finished app)
  useEffect(() => {
    if (progress?.draft_ready || progress?.page_ready || progress?.ready) setReloadToken(t => t + 1);
    if (progress?.ready) shownReady.current = true;
  }, [progress?.draft_ready, progress?.page_ready, progress?.ready]);

  // When the build ends the finished app is usually on screen already, and someone may be using it: it is only
  // loaded again if it was never shown as ready. What a final check changes arrives through the app's hot reload.
  const showFinishedApp = () => {
    if (!shownReady.current) setReloadToken(t => t + 1);
    shownReady.current = false;
  };

  const triggerSynthesis = async (asked: string) => {
    if (!asked.trim()) return;
    setPitch(asked.trim());
    followedBuild.current = false;
    shownReady.current = false;
    setBuilding(true);
    setProgress(null);
    setMessage(null);
    try {
      const res = await fetch('/api/onboarding/kickstart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pitch: asked.trim(),
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
      showFinishedApp();
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
        setPitch('');
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

  // The live workspace: the app beside its specifications, or the place to ask for one when nothing is built
  const built = synthesized || building;
  const noKey: StudioMessage = {
    severity: 'warning',
    text: keyManaged ? 'Add your LLM key to build.' : 'No LLM API key is configured. Set GEMINI_API_KEY, OPENAI_API_KEY or LLM_API_KEY in .env to build.',
  };
  return (
    <AppPreview
      built={built}
      onBuild={triggerSynthesis}
      draft={pitch}
      opening={building && !progress?.draft_ready ? <BuildOpening pitch={pitch} progress={progress} /> : undefined}
      onResetWorkspace={handleResetAllProjects}
      resetting={resetting}
      message={message ?? (!built && !llmConfigured ? noKey : null)}
      reloadToken={reloadToken}
      building={building && !progress?.ready}
      testingIds={building && !progress?.ready ? progress?.rules?.waiting : undefined}
      banner={building ? <BuildProgressBanner progress={progress} /> : undefined}
    />
  );
};

export default KickstartStudio;
