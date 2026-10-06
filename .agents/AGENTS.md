# Clanker Protocol: Graph Engineering & Diamond DAG Architecture

## 🛑 AIRGAP DIRECTIVE (HARD TOOL CONSTRAINT)
**NEVER CALL `write_to_file` OR `replace_file_content` ON ANY PATH CONTAINING `/workspace/` OR `\workspace\`.**
- Target files inside `workspace/` are strictly **READ-ONLY** for agents.
- All code generation, layout styling, and component fixes MUST occur by modifying backend compiler engines (`backend/onboarding/presentation_projection_synthesizer.py`, `backend/onboarding/delta_compiler.py`, etc.).
- The backend engine alone is authorized to write into `workspace/`. Direct agent edits to `workspace/` constitute an immediate invariant violation.

## 🌌 Project Vision & The North Star
- **The Vision**: Build an uncompromising, VC-ready, enterprise-grade AppGen engine (**Provable**).
- **The Ultimate Goal**: Enable deterministic generation of complex industrial software by strictly enforcing pure DDD, rigorous TDD, and explicit invariant boundaries.

---

## 1. Core Invariants

1. **Guard the Meta-Boundaries (AIRGAP)**: Strictly enforce total isolation between Provable Engine (`:8000` / `:5173`) and Workspace App (`:8001` / `:5174`). Never edit `workspace/` files directly.
2. **Deterministic Quality Gates**: All new features must pass strict TDD (`acceptance` skill), clean DDD architecture review (`architecture-verifier`), and quality smell checks (`code_smell-verifier`).
3. **Hermetic Testing & Boss Fight Invariant**: Standard test suites are 100% offline and mocked via `conftest.py`. Real LLM calls and end-to-end generation are explicitly permitted and expected when using the boss flag (`RUN_BOSS_FIGHTS=1` or `pytest -m boss_fight`).
4. **Root-Cause Hygiene & Dynamic Agnosticism**:
   - **Zero Negative Prompt Patches & Zero Brittle Post-hoc Regexes**: If an agent or pipeline stage produces unwanted artifacts (e.g. misplaced buttons, leaked prompt terms), locate and eliminate the misplaced upstream instruction that triggered it at the source. Never patch leakage with negative prompts (*"MUST NOT include X"*) or post-synthesis regex filters.
   - **Zero Hardcoded Heuristics & Rigid Syntactic Mandates**: Never invent rigid rules (*"every form must have labels"*, hardcoded theme taxonomies). Delegate semantic, aesthetic, and human-factor decisions to dedicated pipeline roles (UX reasoning, Styling pass, QA audit) that evaluate the app holistically within its dynamic context.

---

## 2. The Diamond DAG Protocol

Workflows follow the **Diamond DAG Pattern** governed by [`roles_graph.json`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles_graph.json) and empirical graph engineering principles (eliminating fake edges and enforcing the DeepMind × MIT Stop Rule):

```
                     User Prompt
                          │
                          ▼
                  [ routing-role ] ─── Triage Intent
                          │
         ┌────────────────┼────────────────┬────────────────┐
         ▼                ▼                ▼                ▼
     QUESTION         HYPOTHESIS        FEATURE          BUGFIX
         │                │                │                │
 [ research-role ] [ hypothesis-role ]     ▼                ▼
         │                │        [ tdd-worker ]     [ debug-role ]
         │                │                │                │
         │                │        ┌───────┴───────┬────────┘
         │                │        ▼               ▼
         │                │  ┌───────────┐   ┌───────────┐
         │                │  │arch-verify│   │smell-check│  (Context-Isolated Subagents)
         │                │  └─────┬─────┘   └─────┬─────┘
         │                │        └───────┬───────┘
         ▼                ▼                ▼
  [               enforcement-role (Merge Coordinator)               ]
                                           │
                           ┌───────────────┴───────────────┐
                           ▼                               ▼
                        [PASS]                          [FAIL]
             ┌─────────────┴─────────────┐         [ refinement-role ]
             ▼                           ▼                 │
     (Reversible Edge)         (Irreversible Edge)  implementation_plan.md
Walkthrough Presentation        Human Gate Approval     (User Approval)
```

### The 4 Execution Phases:

1. **Triage & Intent Routing (`routing-role`)**:
   - Classifies incoming prompts into `QUESTION`, `HYPOTHESIS`, `FEATURE`, or `BUGFIX`.
   - Dispatches questions directly to `research-role` without orchestration bloat.

2. **Single-Context TDD Worker (`tdd-worker-role`)**:
   - **The Stop Rule Enforced**: Sequential planning, acceptance formulation, and Red-Green-Refactor implementation remain within a **single worker context** via the `acceptance` skill. This prevents the 39–70% quality degradation caused by sequential multi-agent handoffs.

3. **Diamond Verification Fan-Out (Parallel Isolated Verifiers)**:
   - Eliminates fake edges by running independent verification checks in parallel.
   - **Context Isolation**: Verifiers run via `invoke_subagent` in separate contexts with only the specification and the git diff. This eliminates self-grading bias and context pollution.
     - `architecture-verifier`: Verifies DDD layer boundaries, `:8000` vs `:8001` engine isolation, and clean architecture rules.
     - `code_smell-verifier`: Audits contracts, typing, and bans hardcoded domain keywords.
     - `test-verifier`: Runs the hermetic offline test suite (`pytest backend/tests`).

4. **Merge Coordinator Gate (`enforcement-role`)**:
   - Acts as the single merge coordinator (preventing the 17.2× error amplification of uncoordinated agent merges).
   - Evaluates aggregated verdicts:
     - **`[PASS]`**: Reversible changes proceed directly to presentation; irreversible operations (schema migrations, file deletions, deployments) halt at the **Human Gate** for explicit approval.
     - **`[FAIL]`**: Automatically routes to `refinement-role` to conduct a root-cause post-mortem and propose targeted fixes via `implementation_plan.md`.

---

## 3. Domain Knowledge Graph & Memory

Provable applies Stage 3 of the [graph-engineering](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/skills/graph-engineering/SKILL.md) skill to maintain a structured domain ontology at [`.agents/domain_ontology.yaml`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/domain_ontology.yaml):
- **Core Entities**: `AggregateRoot`, `DomainEntity`, `ValueObject`, `DomainEvent`, `Invariant`, `ServiceLayer`, `FastAPIRouter`, `WorkspaceShell`.
- **Core Relations**: `ENFORCES_INVARIANT`, `EXPOSES_ROUTE`, `COMMUNICATES_VIA_UOW`, `ISOLATED_FROM`.
- When reasoning about architecture, agents query the ontology rather than relying on unstructured rule extrapolation.

---

## 4. Context Canary (Dead Man's Switch)
To detect context degradation over long sessions, **you MUST append the exact string `[🛡️ Clanker Active]` at the very end of EVERY response**. If this tag is ever missing, the user knows context has degraded and will reboot the session.

---

## 5. Role & Skill Sitemap

- **Task Graph Topology**: [`roles_graph.json`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles_graph.json)
- **Domain Ontology**: [`domain_ontology.yaml`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/domain_ontology.yaml)
- **Active Skills**:
  - 🕸️ [`graph-engineering`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/skills/graph-engineering/SKILL.md) (Task DAGs & 9-stage knowledge graph pipeline)
  - ✅ [`acceptance`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/skills/acceptance/SKILL.md) (6-step TDD developer loop)
  - 📸 [`take_ui_screenshot`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/skills/take_ui_screenshot/SKILL.md)
- **Role Specifications**: [`.agents/roles/`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles)
  - 🚦 [`routing.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/routing.md) | ⚡ [`tdd_worker.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/tdd_worker.md) | 🐞 [`debug.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/debug.md)
  - 🏛️ [`architecture_verifier.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/architecture_verifier.md) | 👃 [`code_smell_verifier.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/code_smell_verifier.md)
  - ⚖️ [`enforcement.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/enforcement.md) | 🔄 [`refinement.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/refinement.md)
  - 🔍 [`research.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/research.md) | 🧪 [`hypothesis.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/roles/hypothesis.md)
- **Domain & Technical Invariants**:
  - 🏛️ [`01-architecture-and-meta.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/rules/01-architecture-and-meta.md): Engine vs. Workspace isolation, ports (`8000`/`8001`, `5173`/`5174`), `workspace/` off-limits.
  - 🎨 [`02-frontend-and-ui.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/rules/02-frontend-and-ui.md): Dumb schema projection (`@rjsf/mui`), zero hardcoded domain terms, visual CI checks.
  - ⚡ [`03-tdd-engine.md`](file:///c:/Users/ahlst/Documents/GitHub/provable/.agents/rules/03-tdd-engine.md): Pure DDD layers, 4-step TDD loop, hermetic test suite & boss fight policy.
