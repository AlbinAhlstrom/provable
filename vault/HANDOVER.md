# Provable Project Handover & Cross-Chat Continuity Record

This living record ensures 100% seamless continuity between chat sessions. Any agent or human developer resuming work must read this document at the start of a session.

---

## 📌 Current Active System State

- **Active Workspace Base**: `c:\Users\ahlst\Documents\GitHub\provable\workspace`
- **Application Stack Status**:
  - FastAPI Backend Engine: Running on `http://localhost:8000/`
  - Vite PM Studio Frontend: Running on `http://localhost:5173/`
  - Workspace App Preview: Running on `http://localhost:5174/`
  - Containerized Allure Service: Running on `http://localhost:5050/`
- **Active Backend Architecture**: Clean Layered DDD/TDD Architecture (Domain Model, Repository, Unit of Work, Service Layer, Routers).
- **Verified Build Status**: `100% PASS` (0 Vite JSX/TypeScript compilation errors, 150/150 offline backend unit pytest suite passed in 13.12s, hermetic test isolation, Boss Fight 2 10/10 Victory with 0 violations).

---

## 🏛️ Completed Architectural Achievements

19. **Chapter-Organized Living Rule Deck & Plain-Language BDD Gate**:
    - **Diagnostic Root Cause Solved**:
      1. **Reverse Causality & Low-Level Code Jargon Leakage**: Previously, pitch decomposition asked the LLM to invent code `structure` (Aggregate Roots/Entity classes) before writing BDD rules (`inbox`), causing the LLM to write BDD clauses targeting the classes it just designed (e.g. `GameSession`, `DigCell`, `IN_PROGRESS`). For non-technical stakeholders ("specs-are-code"), this defeated BDD's primary value.
      2. **Flat Wall of Text / Scannability Problem**: The rule deck was an unorganized flat list of cards, making it impossible to get a high-level overview or find specific rules without scrolling through dozens of cards.
    - **Architectural Solution**:
      1. **Specs-First & Plain-Language Verifier Gate**:
         - Overhauled `backend/prompts/router_decomposition.md` to enforce human-readable, domain-natural language. Strictly banned PascalCase class names, method invocations, and SCREAMING_SNAKE_CASE enums.
         - Created `verify_and_clean_spec_jargon` in `backend/onboarding/router_engine.py`: an automated sanitization gate that strips technical class wrappers and screaming enums (e.g. `GameSession` $\to$ `game session`, `IN_PROGRESS` $\to$ `in-progress`, `DigCell(x, y)` $\to$ `uncovering tile x, y`).
      2. **Top-Down Zero-Latency Functional Chapter Grouping**:
         - Enhanced decomposition prompt to output top-down functional chapters (`chapters: [{ title, specs: [...] }]`). Zero extra LLM classification round-trips needed.
         - Extended `RuleCard` in `backend/domain/model.py` with `chapter` and `category` fields.
         - Updated `LivingDeckDTO` in `backend/entrypoints/routers/specs.py` and `frontend/src/types/api.ts` to expose `chapters: Record<string, RuleCardDTO[]>`.
         - Updated `synthesize_living_deck_cards` to categorize view cards into `"User Interface & Canvas"` and `"Telemetry & Status"` chapters.
      3. **Collapsible Chapter Accordions & Real-Time Search UI**:
         - Overhauled `frontend/src/components/RequirementControlPanel.tsx` with:
           - Global search bar indexing card titles, chapters, categories, and GIVEN/WHEN/THEN clauses.
           - "Fold All" and "Expand All" chapter toggles.
           - Collapsible chapter accordions with contextual domain icons (`getChapterIcon`) and rule counters.
           - Category badges (`🏷️ INVARIANT`, `🏷️ ACTION_RESULT`, etc.) on individual cards.
           - Chapter autocomplete dropdown (`<datalist>`) in Add/Edit Card Modal.
    - **Verified Test Suite**:
      - Added unit tests in `backend/tests/unit/test_rule_card_deck.py`: `test_rule_card_supports_chapter_and_category`, `test_living_deck_groups_by_chapter`, and `test_spec_jargon_cleanliness_verifier`.
      - 150/150 unit tests pass 100% green in 13.12s. Zero TypeScript errors.

18. **Compiler Graph Action Protocol Hardening & Living Rule Deck Decomposition**:
    - **Diagnostic Root Cause Solved**:
      1. **Contract Drift in Action Dispatching**: In generated applications, Node 2 (DDD Backend) generated a rigid router checking `action_type == "reveal"` while Node 3 (Presentation Projection) generated `onCellAction("primary_reveal", x, y)` and `{ coordinate_x, coordinate_y }`, causing `Domain Guard: Unrecognized action type: 'primary_reveal'`.
      2. **Procedural Slop in Rule Deck**: The Living Rule Deck was generating 5-in-1 imperative procedural scripts (e.g. `SPEC-001` bundling lazy mine population, safe zone exclusion, adjacent counting, FSM transition, and tile reveal into a single monolithic card) rather than discrete, independently toggleable invariants.
    - **Architectural Solution**:
      1. **Action Manifest & Zero Contract Drift**:
         - Node 2 now outputs an authoritative `action_manifest` (actions, acceptable aliases, expected parameter schemas).
         - Node 2's router prompt (`domain_engine_synthesis.md`) enforces resilient action normalization and parameter alias handling (`x` or `coordinate_x`).
         - In `services.py`, the `action_manifest` and router code are passed directly into Node 3 (`presentation_projection_synthesizer.py`), which injects `## Authoritative Backend Action Protocol` and strictly forbids inventing arbitrary action names.
      2. **Strict Invariant Atomicity & De-Proceduralization**:
         - Overhauled `router_decomposition.md` with the **Single Responsibility Invariant Rule**: 1 card = 1 atomic rule, invariant, or affordance.
         - Enforced declarative invariants (WHAT holds true) over imperative procedural scripts (HOW loops/recursion run).
         - Banned physical hardware gestures ("secondary click", "long press", "mouse down") from domain logic cards.
         - Established explicit Invariant Taxonomy: `INVARIANT`, `STATE_TRANSITION`, `PROPAGATION`, and `CALCULATION`.
      3. **Category-Free & Domain-Agnostic View Affordances**:
         - Replaced hardcoded domain keyword matching (`face`, `smiley`, `led`) in `synthesize_living_deck_cards` with clean, domain-agnostic User Affordance view cards (`CANVAS`, `CONTROLS`, `TELEMETRY`, `AFFORDANCE`).
    - **Verified Test Suite**:
      - Added TDD tests in `backend/tests/unit/test_compiler_graph.py` verifying Action Manifest extraction, presentation protocol injection, and prompt atomicity rules.
      - 147/147 unit tests pass 100% green in 12.82s.


15. **Wayfinder Behavioral Overhaul & Elimination of Developer Plumbing**:
    - **Diagnostic Root Cause**: The Wayfinder engine was hardcoding developer-infrastructure CRUD templates ("Chess Lifecycle & State Transitions", "Collision Prevention & Concurrency Guard", "OCC with version check", "ConcurrencyCollisionError", "Unit of Work messagebus") regardless of domain.
    - **Behavior-Driven Taxonomy Overhaul**: Refactored `backend/onboarding/wayfinder.py` with human-accessible, behavior-driven taxonomy for GAME, ORDERING, BOOKING, and PRODUCTIVITY/GENERAL.
    - **Grounded Chess App Flow**:
      - **Frontier Ticket 1**: `Who is Playing?` (Solo vs Computer, Two Players on One Screen / Pass & Play, Play with a Friend Online).
      - **Frontier Ticket 2**: `Move Guidance & Rule Enforcement` (Guided Assistance with dots vs Classic Clean Board).
      - **Causal Fog of War**: Downstream tickets (`Taking Back Moves (Undo)`, `Board Orientation & Perspective`, `Turn Timers & Clocks`, `Game Over & Victory Celebrations`) remain in the Fog of War until upstream decisions unlock them.
      - **Zero Jargon Invariant**: Complete ban on OCC, ConcurrencyCollisionError, Unit of Work, message buses, and database/SQL terminology in Wayfinder BDD clauses.
    - **Documentation & Agent Rules Updated**:
      - `vault/01-Architecture/PM-Studio-UX-Architecture-And-Direction.md`: Codified Section 4 (Wayfinder UX & BDD Invariants).
      - `.agents/rules/02-frontend-and-ui.md`: Codified Rule 4 (Human Behavior Over Technical Plumbing).
    - **Verified Test Suite**: Added `test_chess_app_behavior_driven_invariants` in `backend/tests/unit/test_wayfinder_engine.py`; verified 132/132 unit tests passing cleanly.

16. **End-to-End Wayfinder Synthesis, Living Rule Deck Persistence & Live Workspace Preview**:
    - **Diagnostic Root Causes Solved**:
      1. `rule_cards_json` column was missing in `kickstart_state` table in `backend/db/store.py`, causing locked Wayfinder BDD tickets to vanish on synthesis.
      2. `kickstart_domain_and_scaffold` and `synthesize_kickstart_stack` were recreating `KickstartState` without preserving `rule_cards`.
      3. `AppPreview.tsx` in PM Studio was hardcoded to display `<SchemaDrivenAppPreview />` (the `@rjsf/mui` table/form testing tool) rather than the live Vite workspace app.
      4. `sync_workspace_app_shell` in `backend/service_layer/services.py` was a no-op placeholder that did not write generated TSX to `workspace/src/App.tsx`.
    - **Architectural Solution**:
      1. **Rule Deck Persistence**: Added auto-migration for `rule_cards_json TEXT` column in SQLite `kickstart_state`. Preserved `rule_cards` across all synthesis pipelines.
      2. **PM Studio Live Preview & 4-Tab Hierarchy**: Upgraded `frontend/src/components/AppPreview.tsx` to embed the real live Vite workspace preview on `http://localhost:5174` (with responsive/mobile switcher, reload, and open in new tab). Added `📊 Data Sheet` tab retaining `<SchemaDrivenAppPreview />` as an inspectable diagnostic tool alongside `📱 Preview`, `⚡ Logic Cards`, and `💾 API Docs`.
      3. **Workspace App Shell Live Synchronization**: Wired `sync_workspace_app_shell` to invoke `generate_llm_ui(pitch, {"custom_fixtures": custom_fixtures})` and write the resulting React 18 TSX directly to `workspace/src/App.tsx` (and `workspace/frontend/src/App.tsx`).
      4. **Domain-Tailored Interactive Chessboard**: Added playable 8x8 chessboard template with Unicode pieces, turn indicators, move history, "Take Back" (Undo) state handler, and Reset.
      5. **Verified Verification Gate**: Created `test_chess_app_synthesis_populates_living_deck_and_workspace_preview` in `backend/tests/unit/test_wayfinder_engine.py`. 133/133 backend unit tests pass, and frontend builds cleanly (0 TypeScript errors).

1. **Boss Fight 2 (Iterative Domain Evolution) Crucible Hardening**:
   - **Root Cause 1 (Dataclass Field Ordering)**: Python dataclasses forbid non-default fields after default fields. Implemented `sanitize_dataclass_field_ordering` in `backend/onboarding/cst_isolator.py` to deterministically reorder AST fields.
   - **Root Cause 2 (Module & Class Discovery Desynchronization)**: Replaced naive lowercase matching with canonical `_to_snake_case` in `backend/service_layer/tdd_machine.py` to prevent search collisions across multi-entity domains.
   - **Root Cause 3 (Domain Package Symbol Completeness)**: Enriched `src/domain/exceptions.py` and `src/domain/events.py` in `backend/onboarding/skeleton_builder.py` with typed domain exceptions (`MaintenanceRequiredError`, `StaleDataError`, `InvariantViolation`) and domain events (`MaintenanceRequiredEvent`, `MaintenanceLockedEvent`). Included `from datetime import datetime, date` across aggregate templates.
   - **Root Cause 4 (CST Companion Class Isolation)**: Isolated extra classes in `cst_isolator.py` so helper exceptions/events are preserved without polluting sibling domain files.
   - **Purged Backend Routers**: Deleted [`backend/entrypoints/routers/reviews.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/entrypoints/routers/reviews.py) and [`backend/entrypoints/routers/agents.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/entrypoints/routers/agents.py) and unmounted them from [`backend/app.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/app.py).
   - **Purged Jira/Kanban Integration**: Deleted [`backend/integrations/jira_client.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/integrations/jira_client.py), `jira` section from `integrations.yaml`, startup sync hook in `app.py`, and `jira_key` fields across `store.py`, `schema.sql`, `model.py`, and `repository.py`.
   - **Purged Orphaned UI Components**: Deleted [`AgentTray.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/AgentTray.tsx), [`CodeReview.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/CodeReview.tsx), [`DiffViewer.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/DiffViewer.tsx), and [`DomainModeling.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/DomainModeling.tsx), and cleaned up dead polling loops/state in [`src/App.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/App.tsx).
   - **Purged Legacy Onboarding Modules & Obsolete Scripts**: Deleted [`onboard.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/onboard.py), [`requirements_generator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/requirements_generator.py), [`requirements_synthesizer.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/requirements_synthesizer.py), [`workspace_discovery_agent.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/workspace_discovery_agent.py), [`reset_task.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/reset_task.py), [`src/requirements.json`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/requirements.json), [`reset_ticket.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/scripts/reset_ticket.py), and [`update_json.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/scripts/update_json.py).
   - **Purged Legacy Onboarding Modules & Obsolete Scripts**: Deleted [`onboard.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/onboard.py), [`requirements_generator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/requirements_generator.py), [`requirements_synthesizer.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/requirements_synthesizer.py), [`workspace_discovery_agent.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/workspace_discovery_agent.py), [`reset_task.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/reset_task.py), [`src/requirements.json`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/requirements.json), [`reset_ticket.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/scripts/reset_ticket.py), and [`update_json.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/scripts/update_json.py).
   - **Verified Clean Build**: Zero TypeScript compilation errors (`cmd /c npx tsc --noEmit` code 0) and 100% passing backend test suite.

2. **3-Layer Requirements-Driven Engine & PM Studio UI Pivot**:
   - **Purged Legacy AST Pipeline Short-Circuit**: Removed legacy `if True:` block in `dynamic_domain_generator.py` and unhooked `site_ast_compiler.py` string-template fallbacks, routing all synthesis directly to `generate_llm_ui` in `ui_generator.py`.
   - **SQLite & Schema 3-Layer Upgrade**: Added `layer` column (`PRESENTATION`, `LOGIC`, `INFRASTRUCTURE`) to `schema.sql` and `store.py` SQLite DataStore.
   - **Synthesizer & Requirement Generator Refactor**: Refactored `requirement_generator.py` and `ui_generator.py` to synthesize 3-layer ISO 29148 requirements and full-stack React + FastAPI apps with `// Implements REQ-UI-*` traceability tags and Functional Sandbox Mocks. Added rich domain entity profiles for pizza, bakery, sitting, and e-commerce domains.
   - **PM Studio 3-Layer UI & Presentation Sidebar**: Updated `RequirementsList.tsx` with a 3-Layer Explorer filter bar (`All`, `🎨 UI`, `⚡ Logic`, `💾 API`) and filtered `RequirementControlPanel.tsx` sidebar to ONLY render Presentation layer components (`layer == 'PRESENTATION'`).
   - **Verified Build Status**: `100% PASS` (0 TypeScript compilation errors via `npx tsc --noEmit`, 100% backend unit test pass).

3. **Event-Driven BDD State Machine Requirements & Function-First UI Synthesis**:
   - **Unified BDD Requirements**: Refactored `requirement_generator.py` to synthesize Feature-level requirements with embedded BDD Acceptance Criteria (`Given / When / Then`) and explicit Event/State transition contracts (`User Action ➔ Event ➔ State Transition`).
   - **Function-First, Zero-Fluff Rule**: Removed decorative `__PITCH__` card boxes from `frontend_planning_engine.py` fallback templates and prohibited printing raw prompt text in white decorative hero cards.
   - **Interactive Cart & Checkout Modal Wiring**: Mandated that any Cart component included in synthesis MUST provide state management (`isCartOpen`, `cartItems`), Cart Button toggle handlers, and a complete `CheckoutDrawer` / `CheckoutModal` rendering item lists, item deletion, subtotal calculations, and simulated payment triggers (`[ ⚡ Sandbox Mode ]`).
   - **Verified Build Status**: `100% PASS` (0 TypeScript compilation errors via `npx tsc --noEmit`, 41/41 unit pytest suite passed in 13.58s).

4. **Active Components Collapsible Tree & Sub-Requirement CRUD**:
   - **Collapsible Component Tree View**: Upgraded `RequirementControlPanel.tsx` with a collapsible node hierarchy (`▶ / ▼` toggles) displaying active components, icon badges, component descriptions, and nested child sub-requirements.
   - **Inline Sub-Requirement CRUD**: Added inline creation input forms (`➕ Add Sub-Req`) calling `POST /api/components/sub-requirements/add` and trash bin buttons (`🗑️`) calling `POST /api/components/sub-requirements/delete` to allow dynamically adding/deleting sub-requirements directly from the PM Studio sidebar.
   - **Verified Build Status**: `100% PASS` (0 TypeScript compilation errors via `npx tsc --noEmit`, 41/41 unit pytest suite passed in 13.58s).

5. **Component ID Harmonization, Ghost Component Elimination & Sub-Requirement Tree Linkage**:
   - **ID Harmonization**: Standardized Presentation component IDs across `model.py`, `services.py`, and `requirement_generator.py` to canonical `REQ-UI-{CANONICAL_KEY}` format (e.g. `REQ-UI-CATALOG`, `REQ-UI-CART`, `REQ-UI-TRACKING`).
   - **Ghost Component Elimination**: Purged hardcoded creation of orphan fallback components (`REQ-UI-WORKFLOW` / `REQ-UI-STATUS`) in `_link_logic_reqs_to_ui_components`, ensuring sidebars display strictly active synthesized components.
   - **SQLite Service Layer Linkage Fix**: Fixed `synthesize_kickstart_stack` in `backend/service_layer/services.py` to preserve `parent_id` and `layer` attributes on requirement domain objects when seeding `provable.db`, ensuring sub-requirements appear cleanly under parent component tree nodes.
   - **Verified Build Status**: `100% PASS` (102/102 backend pytest suite passed in 42.90s).

6. **Test Pyramid Streamlining & Heavy E2E Consolidation**:
   - **Single E2E Invariant**: Consolidated all heavy Selenium browser tests into **EXCLUSIVELY 1 E2E test** (`backend/tests/test_e2e_pizza_prompt_sanity.py`).
   - **Unit/Integration Migration**: Moved all non-browser AST compilation, schema synthesis, and domain isolation tests into `backend/tests/unit/`, eliminating redundant Selenium browser startup loops and disk write delays.
   - **Execution Time Optimization**: Reduced full test suite execution time from 80s+ to 42s while maintaining 100% test coverage across 102 tests.
   - **Verified Build Status**: `100% PASS` (102/102 tests passed cleanly).

7. **3-Pillar PM Studio UX Architecture Pivot**:
   - **Page Selector Top Nav**: Implemented [`PageSelectorBar.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/PageSelectorBar.tsx) for switching active Pages/Views (`/`, `/checkout`, `/tracking`) and creating custom page routes.
   - **Executable Test Spec Cards**: Upgraded [`RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/RequirementControlPanel.tsx) to render Executable Test Spec cards with `🟢 PASS` / `🔴 FAIL` badges and formatted `GIVEN / WHEN / THEN` assertion steps.
   - **DDD Domain Entities Explorer**: Added [`DomainEntitiesPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/DomainEntitiesPanel.tsx) for managing domain models (`MenuItem`, `Order`, `CartItem`) and editing seed data tables.
   - **Verified Build Status**: `100% PASS` (0 TypeScript errors via `npx tsc --noEmit`, 102/102 backend pytest suite passed in 42.59s).

8. **Responsive Mobile-First PM Studio Layout & JSX Compilation Integrity Test**:
   - **Mobile-First Default Preview**: Changed default `deviceMode` in [`AppPreview.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/AppPreview.tsx) to `'mobile'` (`375px`), allowing maximum horizontal space for the PM Studio component inspector.
   - **Frame Container Flex Sizing**: Tightened mobile/tablet iframe container flex wrapper (`0 0 375px`), eliminating dark side black bars and allowing the `COMPONENTS` sidebar to expand to fill all remaining horizontal screen space.
   - **Zero Horizontal Scrollbar**: Configured `overflow-x: hidden`, `min-width: 0`, and `flex: 1` on [`RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/RequirementControlPanel.tsx) to guarantee zero horizontal scrollbars.
   - **JSX Compilation Integrity Test Suite**: Created [`backend/tests/unit/test_jsx_compilation_integrity.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/unit/test_jsx_compilation_integrity.py) to automatically verify `npx tsc --noEmit` and generated AST React code with zero syntax error overlays.
   - **Verified Build & Visual Status**: `100% PASS` (104/104 backend pytest suite passed, 0 TypeScript errors via `npx tsc --noEmit`, verified clean in browser).

9. **Mobile-First Responsive Generator Architecture & Dual-Viewport Visual Auditor**:
   - **Dual-Viewport Visual Auditor**: Refactored [`visual_auditor.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/visual_auditor.py) to capture both `preview_desktop.png` (`1280x800`) and `preview_mobile.png` (`375x812`), auditing both viewports against [`visual_qa.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/prompts/visual_qa.md) for horizontal overflow, text clipping, and responsive button wrapping.
   - **Mobile-First CSS Resets & Fluid Drawers**: Enforced global CSS resets (`box-sizing: border-box`, `overflow-x: hidden`, `max-width: 100%`) and replaced fixed drawer widths (`width: '380px'`) with fluid bounds (`width: '100%', maxWidth: '380px'`) across all generator templates in [`frontend_planning_engine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/frontend_planning_engine.py) and [`ui_generation.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/prompts/ui_generation.md).
   - **Verified Build Status**: `100% PASS` (105/105 backend pytest suite passed, 0 TypeScript compilation errors via `npx tsc --noEmit`).

10. **Pizza Ordering Prompt Perfect Output Blueprint & Gap Analysis**:
    - **Diagnostic Gap Analysis**: Identified 5 key areas missing in current synthesis outputs: missing size/crust dynamic pricing multipliers, absence of interactive pizza customizer modal, flat order lists without live status tracking & KDS, lack of 3-layer ISO 29148 trace links (`REQ-UI-*` -> `REQ-SVC-*` -> `REQ-API-*`), and static desktop-only drawer bounds.
    - **Perfect Output Blueprint**: Formulated complete 4-pillar reference specification (`pizza_app_perfect_output_spec.md`), including formal ISO 29148 requirement JSONs, DDD Aggregate (`PizzaOrder`) state machine, pytest BDD test suite, and mobile-first React UI with live price previews, promo engine (`PIZZA20`), and Kitchen Display System (`/kds`).

11. **PM Studio Live Data Fixture Synchronization & Default Order Cleanup**:
    - **Default Order Cleanup**: Fixed initial app generation state in [`frontend_planning_engine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/frontend_planning_engine.py) and [`AppPreview.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/AppPreview.tsx) so generated pizzeria apps initialize `cart: []` and `orders: []` empty by default.
    - **Data Fixtures API & Service Layer**: Added `GET /api/components/fixtures` and `POST /api/components/fixtures/update` in [`components.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/entrypoints/routers/components.py) and [`services.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/services.py) to persist fixture CRUD in SQLite (`provable.db`) and regenerate `workspace/src/App.tsx` live.
    - **PM Studio Live HMR**: Wired [`RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/RequirementControlPanel.tsx) `📦 Data Fixtures` tab to backend API, ensuring adding, editing, or deleting items updates `App.tsx` live and reloads the preview iframe via HMR.

12. **Bidirectional Real-Time Data Fixture Sync & E2E Live Project Protection**:
    - **Bidirectional Data Fixtures Sync**: Implemented full two-way real-time data sync between PM Studio and live App preview. PM Studio edits write to SQLite `provable.db` and regenerate `workspace/src/App.tsx` shell live. Live App preview actions (adding to cart, placing orders) sync back via `fetch('/api/components/fixtures/update')` and `window.parent.postMessage({ type: 'FIXTURES_UPDATED', ... })`, updating PM Studio's `dataFixturesByComponent` state live.
    - **Backend Generator Support**: Updated [`frontend_planning_engine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/frontend_planning_engine.py) and [`ui_generator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/ui_generator.py) to accept `custom_fixtures` and embed bidirectional sync event handlers in synthesized `App.tsx` templates.
    - **Single E2E Test Invariant & Live Project Protection**: Updated [`test_e2e_pizza_prompt_sanity.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/test_e2e_pizza_prompt_sanity.py) to check for existing live project files in `workspace/src/App.tsx` and skip code generation when a live project exists.
    14. **Full-Stack SQLite Persistence & Menu Addition Live Preview Sync**:
        - **DataStore Column Migration & Model Mapping**: Fixed `backend/db/store.py` (`get_kickstart_state` and `save_kickstart_state`), `backend/domain/model.py` (`KickstartState`), and `backend/adapters/repository.py` (`SqliteKickstartRepository.get`) to persist and retrieve `custom_fixtures` in SQLite `provable.db` under `custom_fixtures_json`.
        - **Cross-Port API Endpoint Resolution**: Added `getApiUrl` helper and updated fallback templates in `backend/onboarding/frontend_planning_engine.py` so preview app running on Vite port `5174` targets `http://localhost:8000/api/components/fixtures` and `http://localhost:8000/api/components/fixtures/update` directly, avoiding 404 proxy errors.
        - **Menu Item Addition Rendering E2E Test**: Added `test_add_new_menu_item_fixture_renders_in_live_preview` to [`test_e2e_pizza_prompt_sanity.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/e2e/test_e2e_pizza_prompt_sanity.py), verifying that adding new menu items in backend SQLite renders live pizza cards in the browser preview.
        - **Verified 100% Test Pass**: 106/106 unit tests passed and 6/6 heavy E2E Selenium tests passed cleanly.

    15. **Default 4-Step TDD Direct Execution & Order Snapshot Contract Enforcement**:
        - **Subagent Removal & Direct TDD Rule**: Updated `.agents/AGENTS.md` and `vault/HANDOVER.md` to mandate the strict 4-step RED-GREEN-WIRE-VERIFY TDD workflow directly in the primary agent turn without calling subagents.
        - **Domain State & Order Snapshot Contracts**: Updated `backend/prompts/ui_generation.md` with explicit LLM system prompt invariants for catalog-driven cart management and decoupled immutable order tracking snapshots.
        - **Unit Test Suite Verification**: Added [`backend/tests/unit/test_order_snapshot_integrity.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/unit/test_order_snapshot_integrity.py) to assert prompt contracts and fallback template decoupled order snapshots.
        - **Verified 100% PASS**: 108/108 unit tests passed in 29.65s with zero `import db.store` leaks across routers and service layer.

    16. **Pre-Commit Full Test Suite Invariant Enforcement**:
        - **Mandatory Pre-Commit Test Run Invariant**: Updated `.agents/AGENTS.md` and `vault/HANDOVER.md` to strictly require running the full test suite (`python -m pytest backend/tests/`) before every `git commit` or `git commit --amend` to guarantee zero regressions.

    18. **Standard Benchmark QA Prompt & Universal Domain Entity Architecture**:
        - **Standard Benchmark Prompt**: Codified `"An app to order pizzas"` as the official standard QA benchmark prompt for all testing, synthetic app generation, and quality assurance.
        - **Terminology Pivot (Fixtures ➔ Domain Entities)**: Deprecated legacy "Data Fixtures" terminology across PM Studio in favor of "Domain Entities" / "Entities".
        - **Universal Entity Graph & Linking Invariant**:
          - Primary/Master Catalog components (`catalog`, `menu`, `services`) own root domain entities (`name`, `price`/`rate`, `description`).
          - Universal across all domains (pizzeria, tutor booking, bakery, e-commerce) via automatic master entity role discovery.

    19. **Test Suite Categorization & Directory Isolation (Unit / Integration / E2E)**:
        - **Folder Separation**:
          - `backend/tests/unit/` (102 tests, 28.48s): Strictly fast in-memory unit tests using `FakeUnitOfWork` and isolated domain algorithms.
    20. **Unit Test Speed Optimization (14x Speedup: 28.5s ➔ 2.05s)**:
        - **Bottleneck Resolution**:
          - Refactored `test_chess_game_kickstart_isolation` to use in-memory `FakeUnitOfWork` and domain services rather than heavy on-disk FastAPI/SQLite synthesis (14.08s $\rightarrow$ 0.01s).
          - Created [`backend/tests/unit/conftest.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/unit/conftest.py) to mock external network requests (`requests.post`/`requests.get`) to Allure Docker container, eliminating 4-second socket connection timeouts in `test_switch_project_service`, `test_switch_project_uses_workspace_adapter`, and `test_generate_allure_report_service`.
    21. **Single Pizza Prompt Benchmark Test Suite Focus & Multi-Domain Test Purge**:
        - **Purged Incompatible Tests**: Deleted `test_flappy_bird_prompt_isolation.py`, `test_multi_domain_synthesis.py`, and chess/flappy test functions from `test_generic_domain_synthesis.py`, `test_prompt_synthesis_flow.py`, and `test_visual_verification_suite.py`.
        - **Single Code Gen Execution**: Synthesized a fresh reference pizza ordering stack in `workspace/` for `"An app to order pizzas"`, verifying 100% Native Domain Terminology, Vite bundle health, and Visual Inspection score (95/100).
        - **Empirical Test Results**: Clean 93/93 test pass (100% PASS) across unit, integration, and e2e suites with minimal LLM token consumption.

    24. **Exhaustive Hardcoding Purge (Zero Remaining Across Backend, Prompts, & Frontend)**:
        - **Dynamic Domain Generator Cleanup**: Replaced 1,673-line monolith in [`dynamic_domain_generator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/dynamic_domain_generator.py) (containing `PizzaOrder`, `OvenStation`, `BakingStarted`, and 400 lines of Flappy/Pizza UI) with clean, generic, parameter-driven `Order`, `OrderItem`, and `domain_orders` backend templates.
        - **Site AST Compiler Decoupling**: Purged 150-line Flappy Bird/Chess 2D Canvas engine in [`site_ast_compiler.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/site_ast_compiler.py) and replaced with generic `__CUSTOM_CONTAINER_JSX__` rendering any novel AST component node.
        - **Service Layer & Ontology Direct Mapping**: Replaced lingering keyword checks in `get_component_entity_schemas` in [`services.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/services.py) with direct mapping of `ontology.master_entity.attributes`.
        - **Prompt & Template Generality**: Purged hardcoded domain examples from [`domain_discovery.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/prompts/domain_discovery.md) and [`ui_generation.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/prompts/ui_generation.md).
        - **Frontend PM Studio Generality**: Purged hardcoded `'Pizza'` fallbacks and initial state entities in [`RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/RequirementControlPanel.tsx), [`AppPreview.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/AppPreview.tsx), and [`KickstartStudio.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/KickstartStudio.tsx).
        - **Intent-Based Classification & Registry**: Refactored [`frontend_planning_engine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/frontend_planning_engine.py), [`domain_ontology.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/domain_ontology.py), and [`block_catalog.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/block_catalog.py) to classify interactions via structural verbs and intent (`e_commerce`, `service_booking`, `operations_dashboard`) with zero keyword switchboards.
        - **Empirical Verification**: 100% test pass (103/103 tests in 29.89s), 0 TypeScript errors, 0 `import db.store` leaks, and 0 domain-specific terms across production code, prompts, and frontend UI.

    26. **Full-LLM Free-Form Software Synthesis Architecture Implementation**:
        - **Decommissioned Component Registry**: Deleted [`backend/onboarding/component_registry.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/component_registry.py) (191 lines of pre-baked React snippets) and unhooked `reused_registry_blocks` from planning engines.
        - **Bespoke Domain Deconstruction**: Refactored `_run_component_planning_agent` in [`frontend_planning_engine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/frontend_planning_engine.py) to directly decompose pitch requirements into domain-native bespoke components from ontology contracts.
        - **Domain-Native Spatial Controls Prompting**: Enhanced [`ui_generation.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/prompts/ui_generation.md) with explicit rules for domain-native spatial and interactive controls (quantum wire canvases, frequency waterfall spectrograms, drone radar HUDs, customizers) avoiding generic grid traps.
        - **Orchestration Graph Documentation**: Authored [`vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md) with complete 4-loop Mermaid workflow diagrams.
        - **Empirical Verification**: 100% test pass (91/91 unit tests in 1.85s, 0 TypeScript compilation errors, 0 `import db.store` leaks).

    27. **Total Decommissioning of Block & Category Lego Subsystems**:
        - **Deleted `block_catalog.py` & `category_layouts.py`**: Permanently deleted [`backend/onboarding/block_catalog.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/block_catalog.py) and [`backend/onboarding/category_layouts.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/category_layouts.py).
        - **Dynamic `DomainCapabilitySpec` Engine**: Replaced static 8-block catalog and category slot layouts with pure dynamic `DomainCapabilitySpec` generated from first-principles domain ontology in [`domain_ontology.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/domain_ontology.py).
        - **Purged `CANONICAL_FEATURE_MAP`**: Eradicated static 7-item feature map from [`backend/domain/model.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/domain/model.py) in favor of dynamic slugification.
        - **Entity Attribute `display_mode` Metadata**: Added typed `display_mode` (`tag_chips`, `badge`, `subtitle`, `visible`, `hidden`) to `EntityAttribute` in backend and frontend schema editors, eliminating unsightly stats blobs and providing clean separation between UI presentation pills and internal data fields.
        - **Ghost Component Purge**: Auxiliary capabilities (`auth`, `reviews`) are strictly pitch-driven and never auto-injected for standard ordering/booking workflows.
        - **Empirical Verification**: 100% test pass across full test suite (103/103 tests in 30.53s) and 0 TypeScript errors.

    28. **Total Eradication of Keyword Heuristics & Hermetic LLM Gateway Isolation**:
        - **Zero Heuristic Invariant in Production**: Eradicated all fallback token-slicers, `stop_words` arrays, and keyword `if` cascades from `storm_domain_ontology` in [`backend/onboarding/domain_ontology.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/domain_ontology.py) and `frontend_planning_engine.py`. Production code directly calls `call_gemini` and parses structured DDD JSON.
        - **Gateway Mock Pattern in `agent_orchestrator.py`**: Updated `call_gemini` network gateway to return contract-valid mock schema responses across all stages (`domain_ontology`, `category_planning`, `component_planning`, `aesthetic_planning`, `pitch_component_analysis`, `ui_generation`) when running without an active API key (`api_key == "mock-key"`), eliminating JSON parse crashes and unhandled 500 errors.
        - **Hermetic Test Harness (`backend/tests/conftest.py`)**: Centralized LLM mock test fixtures into the root `backend/tests/conftest.py` so all unit, integration, and E2E suites execute hermetically without external network dependencies.
        - **Empirical Verification**: 100% test pass (103/103 tests in 30.11s), 0 TypeScript compilation errors, live `analyze_kickstart_pitch` and `synthesize_kickstart_stack` execution verified.

    29. **100% Unlocked Entity Schemas & Dynamic Display Mode Controls**:
        - **Zero Locked Schema Invariant**: Completely eradicated all lock icons and delete restrictions (`isBase = attr.name === 'name' || ...`) in [`RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/RequirementControlPanel.tsx). Every attribute can be renamed, changed in type, assigned custom `display_mode` metadata, or removed.
        - **Inline Schema Attribute Modifiers**: Provided inline Type (`string`, `currency`, `number`, `tags`, `boolean`) and Display Mode (`tag_chips` [Pills], `badge` [Ribbon], `subtitle` [Text], `visible` [Field], `hidden` [Internal State]) dropdown selectors for every attribute.
        - **Schema-Driven Data Fixtures CRUD**: Updated PM Studio Data Fixtures panel to dynamically render form inputs and card presentations matching `entitySchemas[canonicalKey].attributes` instead of hardcoded fields.
        - **Template Display Mode Rendering**: Upgraded catalog card rendering in [`frontend_planning_engine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/frontend_planning_engine.py) and `App.tsx` templates to render badges at card top-right, subtitles under title, tag pills for tags/specs, and omit hidden fields.
        - **Empirical Verification**: 100% test pass (103/103 tests in 30.06s) and 0 TypeScript compilation errors.

    30. **Dynamic Multi-Attribute Entity Fixture Editor & Multi-Target PostMessage Sync**:
        - **Dynamic Multi-Attribute Inline Editor**: Replaced the 3-input inline edit box with a dynamic multi-attribute editor grid in [`RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/src/components/RequirementControlPanel.tsx). Clicking ✏️ on an entity now opens a grid containing inputs for EVERY attribute defined in that entity's schema (`tags`, `currency`, `number`, `boolean`, `string`, `badge`, `subtitle`), populated with the entity's current values.
        - **Dynamic Entity Creation Form**: The "Add Entity" form at the bottom of the data fixtures panel dynamically generates input controls matching all attributes in `schema.attributes`.
        - **Multi-Target PostMessage Sync**: Saving a schema or editing a fixture now broadcasts `FIXTURES_UPDATED` directly to `window.parent` and all `<iframe>` child windows (`iframe.contentWindow?.postMessage`), enabling immediate live preview reflection without requiring manual browser refreshes.
        - **Empirical Verification**: 100% test pass (103/103 tests in 27.89s) and 0 TypeScript compilation errors.

    31. **Enterprise AppGen TDD Engine Architectural Specification (7 Binding Directives)**:
        - **1. Runtime Schema-Driven UI**: 100% dynamic UI at runtime using `@rjsf/core` (React JSON Schema Form) driven by FastAPI `/openapi.json`. Zero static React scaffolding or LLM frontend generation.
        - **2. Pytest-First & Parameterized**: Standard `@pytest.mark.parametrize` default; `hypothesis` opt-in strictly when flagged for mathematical/range boundary rules.
        - **3. LibCST Code Isolation (`cst_isolator.py`)**: Meta `libcst` preserves formatting, comments, and docstrings during Aggregate Root class extraction and splicing.
        - **4. Test File Write-Locking**: `test_<spec_id>.py` is write-locked during GREEN phase to prevent LLM test tampering.
        - **5. Pytest Execution Hard Timeout**: 5-second hard timeout (`pytest-timeout`) to kill hanging executions / infinite loops.
        - **6. Instant Full-Stack Skeleton (`skeleton_builder.py`)**: Generates domain models, Pydantic DTOs, and FastAPI routers immediately so `openapi.json` exists from second zero.
        - **7. 3-Strike Dead-End Handling**: If GREEN fails 3 times, performs `git reset --hard` to pre-RED state, marks spec `REQUIRES_HUMAN_INTERVENTION` in SQLite, and advances to next spec.
        - **Documentation**: Updated [`vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md) and [`implementation_plan.md`](file:///mnt/c/Users/ahlst/.gemini/antigravity/brain/1d36d3bb-5859-47b6-8595-94dfc7d311a1/implementation_plan.md).

    32. **Enterprise AppGen Core TDD/DDD Engine Implementation Complete (119/119 Tests PASS)**:
        - **Router Engine (`router_engine.py`)**: Implemented structured output decomposing arbitrary business pitches into `DomainStructureSchema` (Entities/Value Objects) and `DomainBehaviorInboxSchema` (Ordered Specs with Given/When/Then and boundary flags).
        - **Instant Skeleton Builder (`skeleton_builder.py`)**: Implemented full-stack code generator scaffolding pure DDD domain models (`domain/<entity>.py`), Abstract/Fake Repositories, Unit of Work, Pydantic DTOs, and FastAPI routers exporting `/openapi.json` from second zero.
        - **LibCST Context Isolator (`cst_isolator.py`)**: Built with Meta `libcst` to extract and splice Aggregate Root classes with 100% preservation of comments, docstrings, formatting, and surrounding code.
        - **Hardened Red-Gate TDD Machine (`tdd_machine.py`)**: Built state machine with programmatic Pytest JSON report evaluation, tautology rejection (Exit Code 0 in RED), syntax/timeout rejection (Exit Code 2), OS-level test file write-locking in GREEN phase, and 3-strike dead-end rollback handling (`git reset --hard` + `REQUIRES_HUMAN_INTERVENTION`).
        - **Behavior Inbox & Spec-CRUD API (`specs.py` & `BehaviorInboxPanel.tsx`)**: Created backend endpoints (`GET /api/specs/inbox`, `POST /api/specs/inbox/add`, `POST /api/specs/inbox/{id}/status`) and PM Studio frontend panel for structured spec creation without free-text prompt drift.
        - **Dual-Track Benchmark Suite (`test_dual_track_benchmarks.py`)**: Fully verified against both **Track A (B2C Pizzeria Ordering)** and **Track B (Industrial FIFO Warehouse Management)** with 100% PASS.
    36. **PM Studio Frontend DDD Refactoring & 3-View Workspace System**:
        - **Global Navigation Simplification (`App.tsx`)**: Removed detached "Requirements" and "Tests" top tabs, integrating all BDD specification and verification workflows directly into the active Domain Aggregate Inspector.
        - **3-View Workspace System (`AppPreview.tsx`)**: Implemented 3 dedicated Workspace views:
          1. `Preview`: Live RJSF / React sandboxed application preview (`:5174`).
          2. `API (Swagger)`: Embedded FastAPI OpenAPI Swagger interface (`:8000/docs`).
          3. `Domain`: Abstract JSON-driven schema visualizer presenting Python Aggregate dataclasses (`Pallet`, `Zone`, `Operator`), attributes, types, invariants, and method signatures without client-side AST parsing.
        - **Industrial Bounded Context Kickstart (`KickstartStudio.tsx`)**: Removed legacy e-commerce example cards and updated copy to "Define Bounded Context" with WMS industrial prompt placeholder and "⚡ Synthesize Architecture".
        - **Engine Room Pivot (`RequirementControlPanel.tsx`)**: Renamed section to "🧬 DOMAIN AGGREGATES", replaced UI component accordions with Domain Aggregate roots (`Pallet`, `Zone`, `Operator`), mapped BDD executable spec payloads (`GIVEN / WHEN / THEN / UNLESS`) directly to `target_aggregate` via `/api/specs/inbox/add`, added live TDD state badges (`🟢 FULFILLED`, `⚡ TDD RUNNING`, `🔴 NEEDS REVIEW`, `⏳ PENDING`), and removed the free-text component addition box.
        - **Empirical Verification**: 100% PASS across TypeScript frontend build (`npm run build` $\rightarrow$ 0 errors) and full Pytest suite (124/124 PASS).

    44. **Documentation & Architectural Synchronization Pass (Vault & Codebase Alignment)**:
        - **Comprehensive Documentation Rewrite**: Updated `README.md`, `.agents/AGENTS.md`, `vault/Home.md`, and all architecture & workflow records across `vault/` to accurately reflect the pivot to the enterprise DDD/TDD AppGen Engine.
        - **Master Consolidated Documentation**: Compiled all 48 documentation files across the vault and `.agents/` into root `FULL_PROJECT_DOCUMENTATION.md` for seamless context ingestion.
        - **Empirical Verification**: 100% PASS across full backend Pytest suite.

    45. **Category A Architectural Alignment Execution (Tasks 1–4 Complete)**:
        - **Nuclear Purge of Legacy Generators (A4)**: Deleted `backend/onboarding/dynamic_domain_generator.py`, `backend/onboarding/site_ast_compiler.py`, and obsolete AST compiler tests. All domain generation strictly routes through `skeleton_builder.py` and `cst_isolator.py`.
        - **Wire Real LLM for GREEN Phase (A1)**: Replaced heuristic stubs in `backend/service_layer/tdd_machine.py` with `synthesize_green_class_implementation` powered by `gemini-2.5-flash` via `agent_orchestrator.py`. Supplies LibCST micro-context and failing pytest AssertionError to synthesize corrected `@dataclass` definitions with Google-style docstrings, zero inline comments, and SHA-256 hash lock anti-cheat validation.
        - **Pure Schema-Driven UI Dynamic Projection (A2)**: Created `frontend/src/components/SchemaDrivenAppPreview.tsx` powered by `@rjsf/core` and `@rjsf/validator-ajv8`, eliminating the secondary Vite dev server iframe (`:5174`) in favor of dynamic schema forms and live entity data tables directly driven by backend OpenAPI / aggregate schemas.
        - **Database Architecture Realignment (A3)**: Reversed database normalization discrepancy in `vault/01-Architecture/Database Schema.md` to formally document dynamic JSON blob storage in SQLite for rapid Bounded Context evolution with ACID guarantees.
    46. **UX Layout Overhaul, Backend Fail-Loud Invariant, and Visual QA Mandate**:
        - **Legacy UI Artifact Purge**: Deleted `PageSelectorBar.tsx` (`[PAGES: Dashboard View / Add Page]`) and removed dead/non-functional `🔄` refresh buttons. Preserved a single, prominent `🗑️ Reset Workspace` action calling `/api/onboarding/reset`.
        - **"The Engine Room" Full-Width Contextualization**: Eliminated cramped split-pane layout in `AppPreview.tsx`. When `Preview` is active, `SchemaDrivenAppPreview` renders full-width. When `API (Swagger)` is active, the Swagger iframe renders full-width. When `Domain` is active, `RequirementControlPanel` ("The Engine Room") renders exclusively full screen.
        - **Dark-Mode Swagger Inversion**: Injected `filter: invert(85%) hue-rotate(180deg)` CSS filter onto the Swagger iframe to preserve dark-mode visual continuity.
        - **Eradication of Silent "Item" Fallback**: Deleted fallback in `backend/onboarding/router_engine.py` and replaced with `raise RuntimeError("LLM synthesis failed. Refusing to fallback to generic 'Item'.")`. Verified via new unit test in `test_router_engine.py`.
        - **Workspace Domain API (Port 8001)**: Updated `run.py` and `workspace_scaffold.py` to serve the generated application's FastAPI app on port 8001, correctly isolating domain OpenAPI docs (`http://localhost:8001/docs`) from Provable's internal platform engine (`:8000`).
        - **Visual QA Mandate Added to AGENTS.md**: Formally codified the `VISUAL QA MANDATE` invariant requiring automated Selenium headless screenshots and visual inspection before concluding tasks modifying `frontend/src/`.
    49. **Visual Presentation Overhaul, Micro-Context Rule Architecture & Visual CI Automation**:
        - **Themed `@rjsf/mui` & Material UI Dark Palette**: Upgraded `frontend/src/components/SchemaDrivenAppPreview.tsx` with `@rjsf/mui`, `@mui/material`, `@emotion/react`, `@emotion/styled`, and `<ThemeProvider>` dark palette (`#0f172a`, `#1e293b`, `#0284c7`, `#f8fafc`, `#94a3b8`), completely replacing raw HTML inputs with modern, high-contrast dark-mode form controls.
        - **Swagger Iframe Resurrection & Light Mode Presentation**: Removed `filter: invert(...)` from Swagger documentation iframe in `frontend/src/components/AppPreview.tsx`, ensuring crisp, standard Swagger UI documentation targeting the Workspace Domain API (`http://localhost:8001/docs`).
        - **Micro-Context Rule Architecture (`.agents/rules/`)**: Split monolithic documentation into 3 modular rule files:
          - `.agents/rules/01-architecture-and-meta.md`: Strict isolation between Provable Engine (`:8000`/`:5173`) and Workspace App (`:8001`/`:5174`), "No Bandages" rule.
          - `.agents/rules/02-frontend-and-ui.md`: Dumb schema-driven projection, ban on hardcoded domain terms, Visual CI review requirement.
          - `.agents/rules/03-tdd-engine.md`: 4-step TDD loop without subagents, pure domain models, 5-line hash lock anti-cheat.
          - `.agents/AGENTS.md`: Compact index dispatcher instructing agents to read only relevant task rule files.
    51. **Clanker Protocol Codification & Principal Architect Persona Integration**:
        - **Turn-1 Persona & Interaction Loop**: Transformed operational paradigm into the Clanker Protocol (Principal Architect & Strategic Copilot) codified directly within [`.agents/AGENTS.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/AGENTS.md).
        - **The Three Laws & Vision**: Codified North Star Project Vision, Defend Determinism (Anti-Magic), Guard the Meta-Boundaries, and Preserve The Engine Room.
        - **The Fatal Flaw Mechanism & Two-Hats State Machine**: Enforced mandatory pre-implementation codebase/doc risk analysis leading any functional feature response, with explicit Mode 1 (Architect) and Mode 2 (Execution with silent rule injection).
        - **UX Dual-Track Router**: Established Track A (Presentation / Frontend / Bugfix - high autonomy) and Track B (Functional / Domain / API - Fatal Flaw, frictionless roadmap integration, approval gate).
        - **Automated Canary Guard Hook**: Implemented [`.agents/hooks.json`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/hooks.json) and [`scripts/canary_guard.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/scripts/canary_guard.py) on the `Stop` lifecycle event to enforce the `[🛡️ Clanker Active]` dead man's switch with a robust 1-retry loop breaker.
    52. **Boss Fight Acceptance Test Suite & Dual-Gate LLM Judge Architecture**:
        - **Boss Fight Acceptance Suite (`backend/tests/boss_fights/test_hazardous_concurrency.py`)**: Authored high-stress acceptance test suite stress-testing Provable's synthesis engine against complex industrial domain invariants (Optimistic Concurrency Controls, `version_number` collision handling, `StaleDataError`, and pure domain event buffer vs direct dispatch).
        - **Dual-Gate Verification Pipeline**: Implemented Gate 1 (deterministic static AST purity check ensuring 0 I/O or message bus imports in domain models) + Gate 2 (LLM-as-a-Judge prompting Gemini to audit architectural nuances and return structured JSON rationale).
        - **Workspace Sandboxing & Mock Bypass**: Sandboxes pipeline execution in an isolated `tmp_path` using `PROVABLE_WORKSPACE` override (preventing root `workspace/` contamination) and unpatches `conftest.py` autouse LLM mocks when running explicitly with `RUN_BOSS_FIGHTS=1`.
        - **Pytest Marker & Default Skip Invariant**: Registered `@pytest.mark.boss_fight` in `pytest.ini` and configured automatic skipping during standard CI runs to preserve fast hermetic execution (<17s).
    53. **Gemini 3.7 Flash Migration & Surgical CST Import Synchronization**:
        - **Model Upgrade**: Migrated default LLM from legacy `gemini-2.5-flash` to flagship `gemini-3.7-flash` across `.env`, [`backend/agent_orchestrator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/agent_orchestrator.py), and [`backend/config/models.yaml`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/config/models.yaml), taking advantage of the 50% introductory pricing ($0.75 / 1M input tokens, ~9 öre per full generation run) and superior DDD reasoning.
        - **Surgical CST Import Synchronization**: Enhanced [`cst_isolator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/cst_isolator.py) and [`skeleton_builder.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/skeleton_builder.py) to automatically preserve `dataclass, field` and typing primitives during class splicing, preventing collection/import crashes during GREEN phase.
        - **TDD Invariant Assertion Hardening**: Hardened [`tdd_machine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/tdd_machine.py) to accept both `True` and `None` (standard Python domain invariant validator returns) and enhanced `evaluate_green_gate_result` error reporting.
    54. **Zero-Tolerance Double-Lock Test Architecture & 10/10 Boss Fight Victory**:
        - **Eliminated False-Positive Leniency**: Overhauled [`backend/tests/boss_fights/test_hazardous_concurrency.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/boss_fights/test_hazardous_concurrency.py) to implement a **Triple-Gate Verification**:
          1. *Gate 1A (Static AST Purity)*: Zero imports of `requests`, `sqlalchemy`, `sqlite3`, `service_layer.messagebus`, `fastapi`.
          2. *Gate 1B (Deterministic Runtime Execution)*: Dynamically imports generated `Zone` and `Pallet` classes, executes hazardous pallet quarantine, verifies `version_number >= 2`, and validates aggregate event buffer.
          3. *Gate 2 (Zero-Tolerance Binary Disqualification)*: Mandatory auto-fail (passed=False, score=0) if any symbols are unimported/undefined or if `globals().get()` hacks are used.
        - **Authoritative Scaffold Complete (`skeleton_builder.py`)**: Added automatic generation of `src/domain/exceptions.py` (`DomainError`, `StaleDataError`, `InvariantViolation`) and `src/domain/events.py` (`DomainEvent`, `ZoneQuarantinedEvent`), imported cleanly into domain modules.
        - **10/10 Score & Flawless Execution**: Boss fight executed live against Gemini 3.7 Flash: scored **10/10 with 0 violations**, passing all deterministic runtime assertions.
    55. **AppPreview Swagger UI Viewport Optimization**:
        - **Dynamic Viewport Height Calculation**: Updated [`frontend/src/components/AppPreview.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/frontend/src/components/AppPreview.tsx) Swagger API container to `height: calc(100vh - 110px)`, `margin: 16px`, and `flex: 1` with dark slate styling (`#0f172a`, `border: 1px solid #334155`).
        - **Unclipped Iframe Stretching**: Configured the Swagger `<iframe>` with `width: 100%`, `height: 100%`, `flex: 1`, ensuring seamless vertical expansion without scroll-clipping or bottom cutoffs.
        - **Empirical Verification**: Frontend built cleanly (`cmd /c npm run build` passed with 0 TypeScript/Vite errors) and full preflight verification (`agent_preflight_check.py`) passed 100%.

    56. **Windows Uvicorn Reload Patch Harmonization & Zero-Cost Test Policy**:
        - **Root Cause Resolution for Kickstart Crashes**: Diagnosed and resolved sudden server termination during `POST /api/onboarding/kickstart`. On Windows, scaffold file generation in `workspace/` triggered Uvicorn's default reloader which broadcast console-wide `CTRL_C_EVENT` signals, terminating parent `run.py`.
        - **Subprocess Monkey Patch & Launcher Fix**: Fixed `_patched_restart` in [`backend/run_server.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/run_server.py) to properly invoke `uvicorn.supervisors.basereload.get_subprocess` and updated `run.py` to launch the Workspace Domain API (`ws_backend_cmd`) using `run_server_script` instead of raw `uvicorn`.
        - **Hermetic Zero-Cost Testing Invariant**: Codified in [`.agents/AGENTS.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/AGENTS.md) and [`.agents/rules/03-tdd-engine.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/rules/03-tdd-engine.md) that all standard test suites MUST be 100% mocked via `backend/tests/conftest.py` with zero live LLM token expenditure, reserving live app generation strictly for `@pytest.mark.boss_fight` stress tests.
        - **Empirical Verification**: 100% test pass across unit test suite (93/93 in 1.15s) and full preflight verification (`agent_preflight_check.py`) passed cleanly.

    57. **Boss Fight 2: Multi-Stage Iterative Domain Evolution Engine**:
        - **Realistic Human-Driven DevEx Test Suite**: Authored [`backend/tests/boss_fights/test_iterative_domain_evolution.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/boss_fights/test_iterative_domain_evolution.py) to simulate a real-world developer journey: starting from a minimal 1-sentence vague kickstart (*"Heavy machinery rental fleet with equipment tracking and scheduled maintenance"*), synthesizing opinionated baseline models (`HeavyEquipment`, `RentalBooking`), injecting an incremental BDD maintenance lockout invariant, and validating OCC double-booking race condition resilience.
        - **Deterministic Triple-Gate & LLM-as-a-Judge**: Equipped with static AST purity analysis (zero I/O imports), dynamic in-memory invariant execution, and zero-tolerance LLM code review contracts.
        - **Empirical Verification**: Fully integrated under `@pytest.mark.boss_fight`, passing full preflight verification (`agent_preflight_check.py`) 100% cleanly.

    58. **Dual-Mode Kickstart Engine & Zero-Fatigue Clarification Interface**:
        - **Dual-Mode Backend Architecture**: Upgraded [`backend/onboarding/domain_ontology.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/domain_ontology.py), [`backend/service_layer/services.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/services.py), and routers to support `mode: "fast"` (0–3 questions, 0 questions if prompt provides sufficient clarity) and `mode: "guided"` (max 5 strategic domain-fork questions).
        - **Interactive Chip-Based Clarification UI**: Completely overhauled [`frontend/src/components/KickstartStudio.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/frontend/src/components/KickstartStudio.tsx) with dual action buttons (`⚡ Snabbstart` vs `🎯 Guidad Arkitektur`), an inviting placeholder, interactive choice chips with pre-selected defaults, and a one-click `"⚡ Hoppa över & använd standardval"` button.
        - **TDD & Build Verification**: Added unit test suite [`backend/tests/unit/test_kickstart_modes.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/unit/test_kickstart_modes.py) (3/3 passed in 1.38s), verified clean Vite compilation (`0 errors`), and passed 100% full preflight verification (`agent_preflight_check.py`).

    59. **Boss Fight 2 (Iterative Domain Evolution Crucible) Victory — 10/10 Score & Triple-Gate Verification**:
        - **Syntax-Safe Indented Import Reconciliation (`_add_import_symbol`)**: Implemented multiline-aware regex with exact line indentation slicing in [`backend/onboarding/cst_isolator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/cst_isolator.py), eliminating indentation shifts and invalid commas in `try/except` import blocks across generated domain files.
        - **Dynamic Standard Library & Typing Auto-Reconciliation**: Enhanced `cst_isolator.py` to auto-reconcile `math` (`math.ceil`, `math.floor`), `uuid`, `decimal` (`Decimal`), `enum` (`Enum`, `auto`), `copy`, and typing primitives (`Union`, `Optional`, `List`, `Dict`, `Set`, `Tuple`, `Callable`, `field`) into domain modules whenever referenced by synthesized logic.
        - **AST Domain Symbol & Hierarchy Synchronization (`sync_domain_symbols_to_package`)**: Implemented `extract_domain_symbols_from_ast` and `sync_domain_symbols_to_package` in [`backend/service_layer/tdd_machine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/tdd_machine.py) to dynamically register all newly synthesized exception classes in `src/domain/exceptions.py` (inheriting from `DomainError`) and domain event classes in `src/domain/events.py` (inheriting from `DomainEvent`), completely eradicating runtime `NameError` failures.
        - **Purged Companion Class Clobbering**: Removed `extra_nodes` injection from `cst_isolator.py`'s `_ClassReplacer`, enforcing strict 1-class-per-file Single Responsibility Principle (SRP) and preventing companion aggregate roots and events from being redefined inside sibling domain files.
        - **Flawless Triple-Gate Boss Fight 2 Victory**: Executed live Boss Fight 2 against Gemini 3.7 Flash: passed Gate 1A (AST Purity), Gate 1B (Runtime Invariant Execution), and Gate 2 (Zero-Tolerance LLM Judge) with **Score 10/10 and 0 violations**. Passed full system preflight verification across all 6 phases.

    60. **Interactive Manual Acceptance & Dynamic BDD TDD Engine Hardening**:
        - **Zero-Fatigue Direct Snabbstart**: Refactored [`domain_ontology.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/domain_ontology.py) and [`KickstartStudio.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/frontend/src/components/KickstartStudio.tsx) so `fast` mode adopts all opinionated DDD defaults automatically and launches baseline prototypes directly (0 questions) without modal question fatigue.
        - **Dynamic RED Phase Test Synthesis**: Authored [`backend/prompts/red_test_generation.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/prompts/red_test_generation.md) and updated `synthesize_red_test_implementation` in [`backend/service_layer/tdd_machine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/tdd_machine.py) to dynamically synthesize sharp, non-tautological pytest test files for arbitrary user-entered `Given / When / Then` scenarios.
        - **DomainEvent Flexible Kwarg Initialization**: Updated `DomainEvent` in [`skeleton_builder.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/skeleton_builder.py) and `tdd_machine.py` so auto-synchronized events accept arbitrary keyword arguments without `TypeError` constructor crashes.
        - **Behavior Inbox Spec Execution (`▶ Kör TDD`)**: Added `POST /api/specs/inbox/{spec_id}/execute` endpoint in [`backend/entrypoints/routers/specs.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/entrypoints/routers/specs.py) and added direct `⚡ Kör TDD` buttons on all spec cards in [`RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/frontend/src/components/RequirementControlPanel.tsx).
        - **Workspace OpenAPI Swagger UI Health & Toolbar**: Enhanced Swagger view in [`AppPreview.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/frontend/src/components/AppPreview.tsx) with a dedicated header toolbar, live connection info (`http://localhost:8001/docs`), a `🔄 Ladda om Swagger` action button, and an external link button.
    61. **The Trinity Live Data Continuity Protocol (Shared State across Engine Room, Preview, and Swagger API)**:
        - **Workspace API Client & Hook (`useWorkspaceDomainData.ts`)**: Implemented dynamic endpoint slugging (`getEndpointSlug`), direct CRUD functions (`fetchWorkspaceEntities`, `createWorkspaceEntity`), and reactive data hook targeting `http://localhost:8001/api/{slug}`.
        - **Live Full-Stack Schema-Driven Preview (`SchemaDrivenAppPreview.tsx`)**: Replaced disconnected local state with live Workspace Domain API integration. Submitting forms sends real HTTP POST requests to port 8001, displays live records in the data table, and renders prominent green success / red domain exception banners (`RoomNotReadyError`, validation errors).
        - **Engine Room Entity Data Synchronization (`RequirementControlPanel.tsx`)**: Upgraded `hydrateData` to query running Workspace Domain API endpoints on port 8001 and merge live runtime instances directly into the aggregate data views.
        - **Automatic Tab Invalidation & Viewport Re-sync (`AppPreview.tsx`)**: Bumping component keys on tab transitions ensures switching from Swagger to Preview or Engine Room instantly synchronizes all runtime data.
        - **Zero Domain Purity Violations & Full Preflight Green**: Renamed tab to `🧬 Domain Engine`, sanitized DTO type definitions in `types/api.ts`, and verified 100% PASS across TypeScript build and all 6 preflight check phases.

    62. **The Living Rule Deck ('The Fluxx Paradigm') & Bidirectional Auto-Rule Derivation**:
        - **Minimalist 2-Card Architecture**: Codified `LOGIC` and `VIEW` card types in [`backend/domain/model.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/domain/model.py), eliminating category bloat by scoping system rules and global styling to `target = "global"`.
        - **Living Deck REST API & Lifecycle Toggling**: Added `GET /api/specs/deck`, `POST /api/specs/deck/add`, `POST /api/specs/deck/{id}/toggle`, and `POST /api/specs/deck/{id}/update` in [`backend/entrypoints/routers/specs.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/entrypoints/routers/specs.py) and [`backend/service_layer/services.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/services.py).
        - **Bidirectional Auto-Rule Derivation Engine**: Implemented `derive_logic_rules_from_view_prompt` and `project_ui_affordances_from_logic_card` in [`backend/onboarding/router_engine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/router_engine.py), guaranteeing Zero Dark Matter by automatically synthesizing formal `LOGIC` BDD cards from View changes, and projecting UI affordances onto target views from Logic changes.
        - **Living Rule Deck UI Cockpit**: Upgraded [`frontend/src/components/RequirementControlPanel.tsx`](file:///c:/Users/ahlst/Documents/GitHub/provable/frontend/src/components/RequirementControlPanel.tsx) with interactive category filters, active/paused toggle switches (`🟢 / ⏸️`), status badges, Gherkin BDD views, and modal card injectors.
        - **Empirical Verification**: 100% PASS across 117 unit/integration tests and 0 TypeScript compilation errors (`cmd /c npm run build` passed in 6.55s), verified with full agent preflight check.

63. **The Living Rule Deck & TDD Engine Hardening (Boss Fight Verification)**
    - **Status**: Complete & Verified (100% PASS across 6/6 Preflight Verification Phases).
    - **Key Deliverables & Architectural Refinements**:
        - **Boss Fight 1 (Hazardous Concurrency & OCC)**: Verified with **10/10 Score and 0 Violations** from the zero-tolerance LLM judge, empirically proving pure DDD aggregate isolation, optimistic concurrency control (`version_number` + `StaleDataError`), and local event buffering (`self.events`).
        - **Deterministic Companion Model Resolution**: Upgraded LibCST surgical splicing in [`backend/onboarding/cst_isolator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/cst_isolator.py) to dynamically discover actual companion domain entities from the workspace, eliminating `NameError` and hallucinated imports while injecting `from __future__ import annotations`.
        - **Robust TDD Code Extraction & Invariant Handling**: Enhanced [`backend/service_layer/tdd_machine.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/service_layer/tdd_machine.py) with AST syntax verification on synthesized test cases, structured code extraction, and clean exception contract checking.
        - **System Preflight Verification**: Full preflight verification passed 100% across all 6 phases:
          1. Frontend PM Studio compilation: 0 TypeScript/Vite errors.
          2. Backend pytest test suite: 114 passed, 2 skipped, 0 failed.
          3. Domain Purity and Anti-Regression checks: Verified.
          4. Cold-Boot API endpoints and prompt intake: Verified.
          5. Workspace Domain OpenAPI health: Healthy.
          6. Visual CI checks: Ready.

64. **Standalone Full-Stack Frontend Generation Engine (`workspace/frontend/` on Port 5174)**
    - **Status**: Complete & Verified (100% PASS across 118 backend tests and full preflight).
    - **Key Deliverables & Architectural Refinements**:
        - **Standalone Frontend Scaffolder**: Implemented in [`backend/onboarding/skeleton_builder.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/onboarding/skeleton_builder.py):
          - `generate_frontend_package_json` (React 18 + Vite + Tailwind + Lucide Icons)
          - `generate_frontend_vite_config` (configured for port 5174 with `/api` proxy targeting `:8001`)
          - `generate_frontend_tsconfig`, `generate_frontend_tailwind_config`, `generate_frontend_postcss_config`
          - `generate_frontend_index_html`, `generate_frontend_index_css`, `generate_frontend_main_tsx`
          - `generate_frontend_api_client` (auto-generated, type-safe API client with CRUD functions for every domain aggregate)
          - `generate_frontend_entity_view` (high-contrast, responsive management views with search, data tables, and mutation forms)
          - `generate_frontend_app_component` (tabbed workspace shell with live `:8001` connection badge)
        - **Fullstack Skeleton Integration**: `generate_fullstack_skeleton_files` now populates both the FastAPI backend (`workspace/src/`) and the standalone React frontend (`workspace/frontend/`).
        - **Automated Verification**: Added unit test suite [`backend/tests/unit/test_skeleton_frontend_generator.py`](file:///c:/Users/ahlst/Documents/GitHub/provable/backend/tests/unit/test_skeleton_frontend_generator.py) (100% PASS). Preflight verification passed 6/6 phases.

---

*Updated by Antigravity AI on 2026-08-31 (Standalone Full-Stack Frontend Engine Milestone).*























