# 02 - Frontend & UI Rules

## 1. Pure Schema-Driven Dynamic Projection (Dumb Projection Invariant)
The PM Studio frontend (`frontend/src/`) is a 100% domain-agnostic projection engine.
- All domain data, forms, and entities MUST flow dynamically from the OpenAPI schema (`/openapi.json`) or backend API responses (`/api/onboarding/aggregates`).
- **BAN ON HARDCODED DOMAIN TERMS**: You are strictly forbidden from hardcoding specific domain entities or terminology (e.g. `Pallet`, `Zone`, `Operator`, `Pizza`, `User`, `Order`, `CartItem`) into React components.
- Any form generation must use themed JSON schema form projection (via `@rjsf/mui` and Material UI ThemeProvider) rather than static, unstyled, or domain-specific hardcoded forms.

---

## 2. Zero-Mock Tolerance & Fail-Loud Error Invariants
- **ZERO-MOCK TOLERANCE**: You are strictly forbidden from hardcoding static UI elements (e.g. mock product cards, static fake lists, hardcoded domain cards) to bypass rendering issues. Real LLM calls route to OpenAI/Gemini SDK.
- **FAIL LOUDLY**: If a dynamic schema (OpenAPI/JSON) fails to render in the frontend, you must render an empty state or a red `<ErrorBoundary>` with the technical error. You must never resurrect legacy code or fake the UI to make a test pass visually.
- **TEST EVOLUTION OVER REGRESSION**: If a test fails because the fundamental architecture or Bounded Context has evolved (e.g. moving from static UI to schema-driven UI), you must DELETE OR REWRITE THE TEST. You are strictly forbidden from reverting architectural progress or hardcoding data just to turn a failing legacy test green.

---

## 3. Visual CI & Visual Analysis Mandate
**If you modify React code (`frontend/src/`), the preflight check will generate `logs/latest_ui_render.png`. You MUST use your visual analysis skills to review this image to ensure styling is correct, text is readable, and no dead artifacts exist before concluding your task.**

### Visual QA Checklist:
- **Dark Mode Palette Sanity**: Form inputs, labels, placeholders, borders, and background containers must be readable and maintain high-contrast dark-mode elegance.
- **Themed Component Standards**: No raw, unstyled HTML inputs (e.g. default browser textboxes/checkboxes). All form inputs must render via themed `@rjsf/mui` Material UI controls.
- **No Dead Visual Artifacts**: Iframes, accordions, and tables must be cleanly bounded with zero broken gray rectangles, unhandled overflows, or horizontal clipping.
- **Swagger Documentation**: Swagger `/docs` iframes must display clean, un-inverted, responsive Swagger UI documentation.

---

## 4. Wayfinder UX: Human Behavior Over Technical Plumbing
- **Zero Presumptive Branching**: Never assume basic capabilities (like multiplayer, chat, clocks, payment systems) from high-level user pitches. The Frontier MUST only present foundational user-experience questions. All conditional or dependent features remain locked in the Fog of War.
- **BDD Plain-English Accessibility**: BDD exists for non-technical domain stakeholders. Strictly ban engineering plumbing (databases, OCC, WebSockets, Event Sourcing, REST APIs) in Wayfinder BDD cards. Describe user actions and observable behavior in plain, everyday English (`GIVEN / WHEN / THEN / UNLESS`).
- **User Experience > Implementation Details**: The user cares about how something works from a human perspective, not how it is built under the hood.

---

## 5. Workspace App Synthesizer (Generated Presentation Layer Rules)
These rules apply to the backend compiler engines (`presentation_projection_synthesizer.py`, `prompt_expander.py`) when synthesizing user workspace applications:
- **Zero Plumbing Leakage in Presentation Layer**: User-facing copy (titles, subheadings, badges, buttons, cards) must strictly reflect the natural domain language of the target personas. Compiler abstractions (`AggregateRoot`, `Invariant`, `Action Protocol`, `Audit Ledger`, `Boundary Guards`, `Session Lifecycle`, `OCC Version`) are strictly forbidden in user-facing UI text.
- **Dual-Perspective / Persona-Aware Generation**: When a domain naturally involves multiple interaction perspectives (e.g. consumer/client and provider/operator, player and spectator), the presentation layer must support their natural journeys rather than flattening everything into a single operational state-machine view.
- **Dynamic Derivation Over Pigeonholing**: The compiler pipeline must NEVER classify user prompts into hardcoded bins (`B2B`, `B2C`, `GAME`, `CRUD`). All personas, interaction affordances, and presentation layouts must be derived dynamically from the user's intent.

---

## 6. Universal Frontend Acceptance Invariants (Applicable to All Generated Apps)
Every generated application's presentation layer must automatically satisfy four universal acceptance specifications, generated as part of the domain's test suite (`tests/unit/test_{domain}_frontend_acceptance.py`):
1. **Zero Blank Screen Invariant**: When loaded in browser/headless environment, `#root` must contain rendered DOM children (`childElementCount > 0`). Empty roots and white screens are treated as critical specification failures.
2. **Zero Console Exceptions Invariant**: The browser console must be free of unhandled script errors, module import failures, and Vite/React crash overlays.
3. **Viewport Containment Invariant**: Interactive boards, layouts, and cards must not induce unwanted horizontal scrollbars (`scrollWidth <= innerWidth`).
4. **Action Contract Alignment Invariant**: UI interactive buttons and actions must dispatch strictly to the authorized backend Action Protocol routes on `:8001`.

