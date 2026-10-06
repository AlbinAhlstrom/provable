---
paths:
  - "frontend/src/**"
---

# PM Studio rules (frontend/src)

PM Studio is a domain-agnostic projection. It knows nothing about any particular generated app.

- All domain data and forms come from the OpenAPI schema (`/openapi.json`) or engine responses (`/api/onboarding/aggregates`). Forms render through themed `@rjsf/mui` controls, never raw unstyled inputs.
- No hard-coded domain terms (`Pallet`, `Zone`, `Operator`, `Pizza`, `User`, `Order`, `CartItem`, ...) in components. Known violation to fix: the `'Order'` default in `BehaviorInboxPanel.tsx`.
- No mock or placeholder UI to bypass a rendering problem. If a schema fails to render, show an empty state or a red `ErrorBoundary` with the technical error. Never fake the UI to turn a test green.
- Keep components small and composable. `RequirementControlPanel.tsx` (about 900 lines) and `RequirementsList.tsx` (about 600) are known debts; split along their natural seams when touching them.

## Verifying UI changes

1. `npm run build` in `frontend/` has zero TypeScript or Vite errors.
2. Look at the rendered result (`take-ui-screenshot` skill, or `logs/latest_ui_render.png` from preflight) and check: readable dark-mode contrast for inputs, labels and borders; no dead gray rectangles, clipped overflow or horizontal scroll; the Swagger iframe targets `http://localhost:8001/docs` and renders cleanly.
3. If the browser view needs the stack, ask the user to start `python run.py`; do not start it yourself.
