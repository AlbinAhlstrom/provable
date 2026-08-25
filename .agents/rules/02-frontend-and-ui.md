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
