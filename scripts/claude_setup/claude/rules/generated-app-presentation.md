---
paths:
  - "backend/onboarding/**"
  - "backend/prompts/**"
  - "backend/service_layer/services.py"
---

# Rules for what the pipeline generates

These describe the target behaviour of the generators. When the output misses them, fix the schema, prompt or contract that produced it (CLAUDE.md rule 2). Describe the wanted behaviour positively in prompts instead of adding prohibitions.

## Language of the generated product

- User-facing copy (titles, headings, badges, buttons, cards) uses the natural vocabulary of the product's own audience. Compiler vocabulary (`AggregateRoot`, `Invariant`, `Action Protocol`, `OCC Version`, ...) never appears in the UI.
- Spec / rule cards (GIVEN / WHEN / THEN / UNLESS) are written for non-technical stakeholders: user actions and observable behaviour in everyday words. Class names, enums, method calls and infrastructure terms belong to the structure, not to the cards.

## Derivation, not classification

- Personas, interactions and layouts are derived from the user's intent. Never sort a pitch into fixed bins (`B2B`, `B2C`, `GAME`, `CRUD`) or key behaviour off hard-coded domain keywords.
- When a domain has several perspectives (client and provider, player and spectator), the presentation supports each journey instead of flattening everything into one operational state view.

## Acceptance every generated app must satisfy

Generated into `tests/unit/test_{domain}_frontend_acceptance.py`:
1. Zero blank screen: `#root` has rendered children.
2. Zero console exceptions: no unhandled script errors, module failures or Vite/React crash overlays.
3. Viewport containment: no unintended horizontal scroll (`scrollWidth <= innerWidth`).
4. Action contract alignment: UI actions dispatch only to the authorised Action Protocol routes on `:8001`.
