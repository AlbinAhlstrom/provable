# Frontend Components

PM Studio ([`frontend/src/`](../../frontend/src)) is a React 18 + TypeScript + Vite app. It is one screen: the generated app beside its specifications. It knows nothing about any particular generated app.

## Component map

```mermaid
graph TD
    App["App.tsx shell"] --> ProjectSelector["components/ProjectSelector.tsx"]
    App --> KickstartStudio["components/KickstartStudio.tsx"]
    KickstartStudio --> BuildProgress["components/BuildProgressPanel.tsx"]
    KickstartStudio --> AppPreview["components/AppPreview.tsx"]
    AppPreview --> Panel["components/RequirementControlPanel.tsx"]
    Panel --> SpecTree["components/specs/SpecTree.tsx"]
    Panel --> SpecDetail["components/specs/SpecDetail.tsx"]
    Panel --> SpecFormModal["components/specs/SpecFormModal.tsx"]
    SpecTree --> Light["components/specs/SpecStatusLight.tsx"]
    SpecDetail --> Light
```

## Components

- **`App.tsx`**: the header (product name, project selector) and the studio. Switching project remounts the studio.
- **`components/KickstartStudio.tsx`**: decides which of three views is shown. Nothing built yet: one question as the headline and a composer (text box with a Build button, Ctrl + Enter builds) (`POST /api/onboarding/kickstart`). A build running with no draft yet: the build progress screen. Otherwise: the app preview, with a progress strip above it while the build continues. It also owns the workspace reset (`POST /api/onboarding/reset`).
- **`components/BuildProgressPanel.tsx`**: the stages of a running build, read from `GET /api/onboarding/progress`.
- **`components/AppPreview.tsx`**: the live workspace (an iframe on the generated app's dev server, :5174) beside the specifications panel, always side by side. Its toolbar holds reset, reload and open-in-new-tab.
- **`components/RequirementControlPanel.tsx`**: loads the Living Rule Deck (`GET /api/specs/deck`, polled) and owns add, edit, delete and Run Test (`POST /api/specs/inbox/{id}/execute`). It renders the three `specs/` components.
- **`components/specs/SpecTree.tsx`**: the specifications grouped by chapter, collapsible.
- **`components/specs/SpecDetail.tsx`**: the selected specification: title, behaviour (Given / When / Then / Unless), Edit, Delete and Run Test.
- **`components/specs/SpecFormModal.tsx`**: the add and edit form.
- **`components/specs/SpecStatusLight.tsx`**: the test light (see below).
- **`components/StatusMessage.tsx`**: a short outcome message with a typed severity (`success`, `warning`, `error`). Severity is stated by the code that reports it, never read out of the message text.
- **`components/ProjectSelector.tsx`**: lists, switches and adds projects (`/api/projects`).

## The test light

Every specification shows one light, in the tree and next to its title. It only reports the outcome of the spec's last test run:

| Light | `test_status` | Meaning |
| --- | --- | --- |
| Grey | `not_run` | No run has ended for this spec |
| Green | `pass` | The change was proved |
| Yellow | `broken` | The run stopped before the behaviour could be judged (test rejected, domain did not import, provider error, no view to change) |
| Red | `fail` | A verifying step judged the change and rejected it |

The backend derives the status (`backend/onboarding/spec_test_status.py`) and serves it on every deck card together with `test_reason`, one line shown under the title when the light is yellow or red. The Studio does not interpret pipeline statuses itself.

Editing a spec does not clear its stored result, so the light shows the last run until Run Test is pressed again.

## Layout and styling

- Styles live in `frontend/src/index.css` as classes on CSS variables; components carry no layout in inline styles, so media queries can change it.
- Below 768px the layout stacks: a square preview as wide as the screen, the specifications below it (tree, then detail), and one scroll for both.
- Icons come from `@mui/icons-material`, used sparingly on actions. No emoji in the UI. All UI text is English.

## Related

- [[System Architecture]]
- [[PM-Studio-UX-Architecture-And-Direction]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]
