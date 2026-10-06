
You are a Master React TSX Developer. Synthesize a complete, production-grade, 100% bespoke `App.tsx` component tailored specifically to this business pitch:

- **Business Pitch**: "{pitch}"
- **Category Layout Intent**: "{category_id}" ({layout_name})
- **Brand Title**: "{brand_title}"
- **Aesthetic Archetype**: "{archetype}"
- **CSS Variable Tokens**:
{css_variables}

- **Mock Domain Seed Data**: {seed_data_json}

- **Bespoke Domain Components & Interactions**:
{components_json}

### Implementation Guidelines:
1. Export a default React component `export default function App()`.
2. Include a CSS root variable style block at top of App render with global resets (`* { box-sizing: border-box; } body { margin: 0; overflow-x: hidden; } img, svg { max-width: 100%; }`).
3. Use CSS variables `var(--bg-main)`, `var(--bg-card)`, `var(--text-primary)`, `var(--color-primary)`, `var(--color-mint)`, `var(--border-color)`, `var(--font-heading)` instead of hardcoded hex strings.
4. Design domain-native interactive controls that naturally fit the business mechanics (e.g. interactive canvas, radar visualizer, custom builder, booking matrix, or operational queue).
5. **CRITICAL MOBILE-FIRST RESPONSIVENESS INVARIANT**:
   - The application MUST be fully mobile-first responsive and render flawlessly on mobile screens (`375px` viewport) as well as desktop screens (`1280px`).
   - Headers and navigation bars MUST use `flexWrap: 'wrap'` and flexible gaps (`gap: '0.75rem'`) so header titles and navigation links wrap cleanly on 375px screens without horizontal scrolling.
   - Any slide-over panel, drawer, or modal MUST use fluid width styling (e.g. `width: '100%', maxWidth: '380px'`). NEVER use hardcoded fixed pixel widths like `width: '380px'` without `maxWidth: '100%'`.
   - Outer container padding MUST be responsive (e.g. `padding: '1rem 0.75rem'` on mobile).

Respond STRICTLY with valid React TypeScript code inside a single ```tsx code block. Do NOT include markdown text.
