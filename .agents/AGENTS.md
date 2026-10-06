# Clanker Protocol: Graph Engineering & Diamond DAG Architecture

## 🛑 AIRGAP DIRECTIVE (HARD TOOL CONSTRAINT)
**NEVER CALL `write_to_file` OR `replace_file_content` ON ANY PATH CONTAINING `/workspace/` OR `\workspace\`.**
- Target files inside `workspace/` are strictly **READ-ONLY** for agents.
- All code generation, layout styling, and component fixes MUST occur by modifying backend compiler engines (`backend/onboarding/presentation_projection_synthesizer.py`, `backend/onboarding/presentation_specs.py`, etc.).
- The backend engine alone is authorized to write into `workspace/`. Direct agent edits to `workspace/` constitute an immediate invariant violation.

## 🌌 Project Vision & The North Star
- **The Vision**: Build an uncompromising, VC-ready, enterprise-grade AppGen engine (**Provable**).
- **The Ultimate Goal**: Enable deterministic generation of complex industrial software by strictly enforcing pure DDD, rigorous TDD, and explicit invariant boundaries.

---

## 1. Core Invariants

### 🏛️ [`01-architecture-and-meta.md`](rules/01-architecture-and-meta.md)
- **When to read**: Architectural decisions, multi-service setup, port allocations, workspace isolation.
- **Key concepts**:
  - Strict isolation between Provable Engine (`:8000` / `:5173`) and Workspace App (`:8001` / `:5174`).
  - The "No Bandages" rule (`workspace/` is strictly off-limits; generator updates in `backend/` only).
  - Multi-service stack lifecycle (never start `run.py` from the agent) and Obsidian vault documentation conventions.

### 🎨 [`02-frontend-and-ui.md`](rules/02-frontend-and-ui.md)
- **When to read**: Modifying React components (`frontend/src/`), theming, UI layout, or dynamic schema projection.
- **Key concepts**:
  - "Dumb Projection" schema-driven UI rules (dynamic form/table projection via `@rjsf/mui`).
  - Strict ban on hardcoded domain terms (`Pallet`, `Zone`, `Pizza`, etc.).
  - Zero-mock tolerance & Fail-Loud `<ErrorBoundary>`.
  - **Visual CI Mandate**: Review `logs/latest_ui_render.png` before concluding frontend changes.

### ⚡ [`03-tdd-engine.md`](rules/03-tdd-engine.md)
- **When to read**: Writing backend features, bugfixes, test cases, or refactoring services.
- **Key concepts**:
  - 4-step TDD loop (RED $\rightarrow$ GREEN $\rightarrow$ WIRE $\rightarrow$ VERIFY) executed directly without subagents.
  - Layer boundaries & Pure DDD domain models (zero FastAPI/Pydantic/DB in domain).
  - 5-Line Hash Lock anti-cheat verification.
  - Pre-Commit full test suite execution (`python -m pytest backend/tests/`).
  - Mandatory systematic pre-flight check (`python scripts/agent_preflight_check.py`).

---

> **Tooling note**: Claude Code reads the root `CLAUDE.md` (which points back at these rule files). Skills now live in `.claude/skills/` and enforcement hooks in `.claude/hooks/`.
