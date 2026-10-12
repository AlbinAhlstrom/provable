---
paths:
  - "frontend/src/**"
---

# PM Studio rules (frontend/src)

PM Studio is a domain-agnostic projection. It knows nothing about any particular generated app.

- All domain data and forms come from the OpenAPI schema (`/openapi.json`) or engine responses (`/api/onboarding/aggregates`). Forms render through themed `@rjsf/mui` controls, never raw unstyled inputs.
- No hard-coded domain terms (`Pallet`, `Zone`, `Operator`, `Pizza`, `User`, `Order`, `CartItem`, ...) in components.
- No mock or placeholder UI to bypass a rendering problem. If a schema fails to render, show an empty state or a red `ErrorBoundary` with the technical error. Never fake the UI to turn a test green; if a test is stale because the architecture moved on, rewrite or delete it.
- Use relative `/api/...` URLs, never `http://localhost:8000` (Vercel deployment).
- Keep components small and composable: one job per file (`components/specs/` is the pattern), data and handlers in the panel that owns them.
- All UI text is English. No emoji; icons come from `@mui/icons-material`, sparingly, on actions.
- A message's severity is typed (`StatusMessage`), never guessed from its text.
- Layout lives in `index.css` classes, not inline styles, so the narrow-screen media query can restack it. Check both widths after a layout change.

## Verifying UI changes

1. `npm run build` in `frontend/` has zero TypeScript or Vite errors (the commit guard also runs it when `frontend/` is staged).
2. Look at the rendered result: the `take_ui_screenshot` skill, or `logs/latest_ui_render.png` from `python scripts/agent_preflight_check.py` when Studio is up on :5173. Check readable dark-mode contrast for inputs, labels and borders; no dead gray rectangles, clipped overflow or horizontal scroll; the Swagger iframe renders cleanly.
3. If no screenshot could be captured, say plainly that the UI was not visually verified.
