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

## 🧪 3. Test Pyramid Invariant & The Gibberish Strategy

- **Industrial WMS Domain Benchmark**: The official QA benchmark is an industrial domain context (e.g. Warehouse Management System tracking `Pallet`, `Zone`, and `Operator`).
- **The Gibberish Strategy (`backend/tests/e2e/test_ui_dynamic_projection.py`)**: UI dynamic purity is mathematically verified by feeding synthetic nonsense schemas (`TestFlorg` / `Zorp`) and asserting that the presentation layer projects them dynamically without fallback to hardcoded words.
- **Fast Unit Tests**: All skeleton generation, router derivation, and LibCST splicing tests reside in `backend/tests/unit/`, running in `< 1.0s`.

---

## 🧭 4. Wayfinder UX & BDD Invariants: Behavior Over Technical Plumbing

Wayfinder exists to guide non-technical stakeholders and domain experts from an ambiguous idea to a verified domain model. To prevent technical alienation and premature architectural lock-in, the Wayfinder UX must strictly adhere to the following invariants:

### 1. Behavior Over Implementation (User Experience > Plumbing)
- **The Core Rule**: The user cares about **how the product works and feels**, not how it is built.
- **Strict Ban on Engineering Jargon in BDD & Wayfinder UI**: Never present choices or BDD clauses mentioning databases, storage strategies (e.g. `Event Sourcing`, `FEN snapshots`, `SQLite vs Postgres`), concurrency models (e.g. `OCC`, `Last-Write-Wins`), network protocols (`WebSockets`, `SSE`, `REST`), or backend patterns (`UnitOfWork`, `FastAPI routers`, `asynchronous messagebus`).
- **User-Centric Framing**:
  - ❌ *Bad*: "Optimistic Concurrency Control with version checks to resolve mutation collisions."
  - ✅ *Good*: "If two people edit the same document at once, prompt the user to review changes before overwriting."

### 2. Non-Technical Accessibility (The BDD Plain-English Invariant)
- **The Dan North Principle**: BDD was created specifically to eliminate the communication gap between business stakeholders and developers. If a non-technical founder, product manager, or 10-year-old cannot understand a BDD clause instantly, the clause has failed.
- **Stupid Simple Language**: Use everyday conversational language in `GIVEN / WHEN / THEN / UNLESS`:
  - ❌ *Bad*: "GIVEN active GameSession WHEN move is dispatched THEN fold sequence of MoveMade events to project board state UNLESS optimistic concurrency version mismatch occurs."
  - ✅ *Good*: "GIVEN it is my turn WHEN I drag a piece to a valid square THEN the piece moves there UNLESS the king would be left in check."

### 3. Zero Presumptive Branching & True Fog of War
- **Never Assume Basic Capabilities**: Do NOT assume multiplayer, social feeds, payment gateways, clocks, or complex backend infrastructure from a high-level pitch like *"a chess app"*.
- **The Fog of War Holds All Conditional Features**: Downstream capabilities that depend on unmade choices must remain locked in the Fog of War. If an upstream decision rejects a path (e.g. user chooses "Solo play vs. Computer"), all multiplayer questions (rooms, matchmaking, clocks, disconnect grace periods) must NEVER appear on the Frontier.
- **Root Frontier Focus**: The initial Frontier must only ask foundational human-experience questions: *Who is using this, and how are they interacting with it?*

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original document outlined a 3-pillar UX connecting domain entities through universal entity graphs (Master -> Selection -> Tracking). While the frontend has been updated to render domain aggregate trees, full dynamic form auto-generation from OpenAPI schema definitions directly in PM Studio remains a key roadmap item.]

---

## 💾 5. Persistence & Memory Channels

To ensure these decisions persist across future agent chat sessions:
1. **`vault/HANDOVER.md`**: Updated at the end of every turn to pass live architectural state to the next session.
2. **`.agents/AGENTS.md`**: Codifies mandatory rules and layout invariants into the agent's system prompt.

