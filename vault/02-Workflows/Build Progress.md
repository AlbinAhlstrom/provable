# Build Progress

The Studio shows an app while it is being built. A kickstart answers only when everything is done, but its page is
written well before that: the rules, the QA audit and the visual review come after it (in a 127 s build the page was
there after about 100 s; in a rule-heavy build the gap is minutes).

## How it works

- **Source**: the run recorder already holds every stage of the running build with its status ([[Run Recorder]]).
  `backend/onboarding/build_progress.py` reads that out as a typed `BuildProgress`; nothing is tracked twice.
- **Endpoint**: `GET /api/onboarding/progress`, answered while the kickstart request is still open.
- **`page_ready`**: true once the `presentation` stage delivered. Until then the workspace serves the skeleton's
  stand-in app (one plain table per entity), which is not what was asked for, so the Studio does not show it.
- **`rules`**: the spec runner reports `RuleProgress` (done, total, active) before the first behaviour spec and after
  each one; the `behaviour_specs` stage keeps it as its `rules` note.
- **Only a kickstart is a build.** A single spec execution changes an app that already exists.

## What the Studio shows (`frontend/src/components/KickstartStudio.tsx`, `BuildProgressPanel.tsx`)

1. Before the page is written: a "Building your app" screen listing each stage in plain words with its status.
2. Once the page is written: the live preview, with a strip above it saying what is still being worked on and how
   many rules are active.
3. When the build ends: the strip goes and the preview reloads.

The Studio polls the endpoint, so a build it did not start (a reloaded tab, a kickstart sent to the API) is picked up
the same way. Stage labels come from the backend (`STAGE_LABELS`), so the Studio stays a projection.

## What a user watching the build should know

- The generated API restarts each time a rule lands and keeps its records in memory: records added during the build
  are cleared. The strip says so.
- Behaviour tightens as rules arrive, and QA or the visual review can still change the page.

Related: [[Run Recorder]].
