# Build Progress

The Studio shows an app while it is being built. A kickstart answers only when everything is done, but its page is
written well before that: the rules, the QA audit and the visual review come after it (in a 127 s build the page was
there after about 100 s; in a rule-heavy build the gap is minutes).

## How it works

- **Source**: the run recorder already holds every stage of the running build with its status ([[Run Recorder]]).
  `backend/onboarding/build_progress.py` reads that out as a typed `BuildProgress`; nothing is tracked twice.
- **Endpoint**: `GET /api/onboarding/progress`, answered while the kickstart request is still open.
- **`draft_ready`**: true once the skeleton is written. From then on the workspace serves an app that can be shown.
- **`page_ready`**: true once the `presentation` stage delivered: the draft has been replaced by the written page.
- **`rules`**: the spec runner reports `RuleProgress` (done, total, active, the title of the rule that became
  active last, and `waiting`: the ids of the specs in the loop that are not settled yet) before the first behaviour
  spec and after each one; the `behaviour_specs` stage keeps it as its `rules` note.
- **`stages`, `percent`**: every stage of a build from the start, each with its usual share of a build's time and
  how far it has come (`backend/onboarding/stage_timing.py`; see "The build progress bar" in [[Frontend Components]]).
- **Only a kickstart is a build.** A single spec execution changes an app that already exists.

## What the Studio shows (`frontend/src/components/KickstartStudio.tsx`, `BuildProgressPanel.tsx`)

1. From the moment a build starts: the live preview beside the specifications, with a banner above it: the
   percentage, what is being worked on, the weighted progress bar and the stages by name. Until the skeleton is
   written the preview shows the blank workspace page.
2. The preview reloads when the first draft is written and again when the page is written.
3. While the build runs the preview is held back a little: muted, with a slow band of light passing over it. It
   stays usable. The specifications appear in their panel as soon as the rule deck is stored; the ones the build
   is working on pulse, and each turns to its test light as it is settled.
4. When the build ends: the banner goes, the preview reloads and steps forward (full colour, a short pop).

The Studio polls the endpoint, so a build it did not start (a reloaded tab, a kickstart sent to the API) is picked up
the same way. Stage labels come from the backend (`STAGE_LABELS`), so the Studio stays a projection.

## The first draft (`skeleton_builder.py`, `onboarding/draft_theme.py`)

What is on screen before the page is written is the skeleton's stand-in app. It is generated to read as an early
draft of the product, not as an admin tool:

- The product's name, and one tab per entity the audience works with (`presented_entities()`), under plain plural
  names (`SalonService` becomes "Salon services"). Internal entities have no tab.
- Records as cards: the first descriptive field is the title; ids, references (`*_id`) and the class's event list
  are left out. A view with nothing to show asks again every few seconds, because the starting content is written
  a little after the app starts.
- **Colours**: the stand-in is coloured by CSS variables in `src/theme.css`. The skeleton writes neutral values. The
  UX plan ends its visual direction with one token line (`TOKENS background=#... surface=#... text=#... accent=#...
  on_accent=#... heading=serif`); the `ux_plan` stage reads it as a typed `DraftTheme` and rewrites the file, about
  a minute before the page is written. A direction without a complete token line leaves the neutral theme and the
  stage notes it (`draft_theme`). The written page does not depend on the file.
- **Outline of the main view**: the same section states the form of the main view as one layout line
  (`LAYOUT columns=7 rows=5` for a fixed grid, `rows=auto` for a view that grows with its records), read as a typed
  `DraftLayout` and written into the same `src/theme.css`. The stand-in draws it above its records as an empty
  outline in the plan's colours: the view's columns and rows before anything is in them. A fixed grid keeps its
  proportions. A direction without a complete layout line draws no outline and the stage notes it (`draft_layout`).

If the presentation stage fails, the draft stays as the app, so it keeps a working "Add" form.

## Records survive restarts (the generated app's record store adapter, written by `backend/onboarding/skeleton_builder.py`)

The generated API keeps its records in memory and restarts every time the build writes a rule. Each router saves
its collection to `.data/<plural>.json` after every change and reads it back on its first request, so what a user
adds while watching the build is still there afterwards.

- The seed file is applied once per version (its modification time is saved with the records), so a starting record
  a user removed stays removed.
- A saved record the class no longer accepts is reported and left out; the API stays up.
- The generated app's own tests run without the store (`tests/conftest.py` sets `APP_DATA_DIR` to empty).
- A new build (and a workspace reset) deletes `.data`.

## What a user watching the build should know

- Behaviour tightens as rules arrive, and QA or the visual review can still change the page.

Related: [[Run Recorder]], [[Audience Roles and Seed Data]].
