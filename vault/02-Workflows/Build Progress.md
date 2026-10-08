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
- **`rules`**: the spec runner reports `RuleProgress` (done, total, active, and the title of the rule that became
  active last) before the first behaviour spec and after each one; the `behaviour_specs` stage keeps it as its
  `rules` note.
- **Only a kickstart is a build.** A single spec execution changes an app that already exists.

## What the Studio shows (`frontend/src/components/KickstartStudio.tsx`, `BuildProgressPanel.tsx`)

1. Until the skeleton is written (about 20 s): a "Building your app" screen listing each stage with its status.
2. From then on: the live preview, with a strip above it saying what is being worked on, how many rules are active
   and which rule was enforced last. The strip reads "First draft" until the page is written.
3. When the build ends: the strip goes and the preview reloads.

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
