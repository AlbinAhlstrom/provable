# PM Studio UX Architecture, Design Guidelines & Strategic Direction

This document captures the UX philosophy, component layout hierarchy, design invariants, and strategic product direction for **Provable PM Studio**.

---

## 🏛️ 1. Core UX Philosophy: 3-Pillar Architecture

PM Studio moves away from cluttered dashboard overlays and text-heavy sub-requirements, organizing the application management workflow into **3 clear pillars**:

### Pillar 1: Top Pages & Views Selector Bar (`PageSelectorBar.tsx`)
- **Location**: Top section of the application preview canvas.
- **Function**: Displays all active views/routes in the synthesized application (`🏠 Home Page (/)`, `💳 Checkout Page (/checkout)`, `📦 Order Tracking View (/tracking)`).
- **Interactions**:
  - Click any page chip to switch active preview view.
  - Click `➕ Add Page` to define a new custom page route inline (`Page Name` + `Route`).
  - Click `✕` to delete custom non-home pages.

### Pillar 2: Executable Test Spec Cards (`RequirementControlPanel.tsx` ➔ `Tab 1: 🧪 Executable Tests`)
- **Location**: Tab 1 inside each expanded component card in the right/bottom sidebar.
- **Function**: Replaces plain-text sub-requirements with **Executable Test Specs**.
- **Visual Spec Cards**:
  - `🟢 PASS` / `🔴 FAIL` status badges.
  - Interactive BDD Builder Action Chips (`+ GIVEN`, `+ WHEN`, `+ THEN`) pre-filling assertion prefixes with 1 click.
  - Context-aware behavioral example placeholders (e.g., `e.g. When item added, update subtotal & badge count...`).
  - Explicit `➕ Add Test` action button.
  - Trash bin `🗑️` button to delete test specs.

### Pillar 3: Domain Entities CRUD & Universal Entity Graph (`RequirementControlPanel.tsx` ➔ `Tab 2: 🧬 Entities`)
- **Location**: Tab 2 inside each expanded component card.
- **Function**: Directly binds Domain Entities (e.g. `MenuItem`, `CartItem`, `Order`) to the component cards they belong to, avoiding separate messy floating overlays.
- **Terminology**: Migrated from legacy "Data Fixtures" to **Domain Entities**.
- **Universal Entity Graph & Linking Invariant**:
  - **Master Catalog Components** (`catalog`, `menu`, `services`, `tutors`): Define root items (`Name` + `Price/Rate` + `Description`).
  - **Selection/Basket Components** (`cart`, `basket`): Do NOT use arbitrary freeform string inputs. Instead, they provide a **Dropdown Selector of Master Catalog Entities** + Quantity input (`[ Dropdown: Select Catalog Item ▼ ] [ Qty: 1 ] [ ➕ Add to Cart ]`).
  - **Transaction/Tracking Components** (`tracking`, `orders`, `bookings`): Provide a **Dropdown Selector of Master Catalog Entities** + Status enum (`[ Dropdown: Select Item ▼ ] [ Status: Received ▼ ] [ ➕ Create Test Order ]`).
- **Full Inline CRUD**:
  - **Create**: Add new entity items via role-aware forms (text fields for catalog roots, dropdown selectors for dependent carts/orders).
  - **Read**: Display seed items bound to the component with price/status formatting.
  - **Update**: Click `✏️ Edit` to modify entity name/price/status inline.
  - **Delete**: Click `🗑️` to remove entity items from the active dataset.


---

## 📱 2. Mobile-First Responsive Design Invariants

All PM Studio features and backend UI generators MUST adhere to the following mobile-first layout invariants:

1. **Mobile Default Preview**:
   - `AppPreview.tsx` defaults `deviceMode` to `'mobile'` (`375px`).
   - Keeps preview focused on touch/mobile layout and maximizes horizontal space for the component inspector.

2. **Tight Frame Container Flex**:
   - In mobile mode, the preview frame flex wrapper collapses to `0 0 375px` (`width: 375px`).
   - **Zero Black Side Bars**: Eliminates dark empty padding around the mobile canvas.

3. **Responsive Vertical Stacking (`@media (max-width: 960px)`)**:
   - On screens `< 960px` (or mobile viewports), `.app-preview-split` stacks vertically (`flex-direction: column`):
     - Mobile preview frame on top (`height: 500px`).
     - Component Inspector below (`width: 100%`, `flex: 1`).
   - On desktop screens (`>= 961px`), side-by-side split row layout is rendered.

4. **Zero Horizontal Scrollbar Invariant**:
   - `RequirementControlPanel` and cards MUST use `flex: 1`, `minWidth: 0`, and `overflowX: 'hidden'`.
   - Text, badges, and input forms wrap fluidly (`wordBreak: 'break-word'`, `flexWrap: 'wrap'`) so the component inspector NEVER requires a horizontal scrollbar.

---

## 🧪 3. Test Pyramid Invariant & Benchmark Prompt

- **Official QA Benchmark Prompt**: `"An app to order pizzas"` is the established baseline reference prompt for quality assurance, automated synthesis verification, and visual regression testing across all sessions.
- **Only 1 Heavy E2E Test**: `backend/tests/test_e2e_pizza_prompt_sanity.py` is the SINGLE heavy browser E2E test executing this benchmark prompt end-to-end.
- **Fast Unit Tests**: All AST compilation, schema validation, and JSX integrity tests reside in `backend/tests/unit/` (including `test_jsx_compilation_integrity.py`), running in `< 1.5s`.

---

## 💾 4. Persistence & Memory Channels

To ensure these decisions persist across future agent chat sessions:
1. **`vault/HANDOVER.md`**: Updated at the end of every turn to pass live architectural state to the next session.
2. **`.agents/AGENTS.md`**: Codifies mandatory rules and layout invariants into the agent's system prompt.
3. **`/learn` Slash Command**: Used to save user preferences as workspace rules.
