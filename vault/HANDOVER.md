# Provable Handover (current state)

Last updated 2026-10-06, when work moved from Antigravity to Claude Code. The full history of earlier sessions is in [[HANDOVER-archive]]; read it only when you need the background for a specific item, and verify its claims against the code first.

## State

- Branch `main`; commits made in Claude sessions are not pushed. Never push without the user asking.
- The working tree holds unrelated uncommitted changes (line-ending churn in `scripts/` and the router prompt, Wayfinder-removal fallout). Stage only the files a task touched.
- Unit tests are green as confirmed by the user on 2026-10-06. One strict `xfail` in `test_compiler_graph.py` marks the router-prompt regression below.
- Wayfinder, OpenCode and guided architecture were removed (commit `e9707e6`). Some docs and scripts still mention them.
- `workspace/` is not versioned. It is regenerated and wiped during quality checks, and the engine DB lives at `<workspace>/requirements/provable.db`.
- `scripts/agent_preflight_check.py` Phase 4 now runs against a throwaway workspace and DB with the LLM off. The user has not yet confirmed a clean full run.
- Claude Code configuration is versioned in `scripts/claude_setup/` and installed with `python scripts/claude_setup/install.py`.

## Open decisions and known gaps

1. **Router prompt regression.** `backend/prompts/router_decomposition.md` has only ever existed in two versions in git. The atomicity and invariant-taxonomy rules (archive #18) and the specs-first, plain-language and chapters rules (archive #19) are not in either. The code that consumes them exists (`chapters` parsing, `RuleCard.chapter`, the accordion UI). Restoring the prompt is pending; candidate sources for the lost text are Antigravity's local file history.
2. **Jargon sanitizer.** `router_engine.verify_and_clean_spec_jargon` rewrites spec text with regexes and a Minesweeper-specific replacement map, and is the only thing producing plain-language specs today. Design choice pending: A) specs-first single call, B) two-stage generation, C) detect and send back through the bounded rework gate. `test_spec_jargon_cleanliness_verifier` pins the current behaviour and must change with the decision.
3. **Other post-hoc patching.** `frontend_planning_engine.py` (hex-to-CSS-variable rewrite, `useState` seed rewrite) and `domain_engine_synthesizer.py` (import rewrites, typing-import repair).
4. **Negative-prompt phrasing.** About 40 prohibition lines across 15 prompt files, plus `FORBIDDEN` blocks in `dynamic_architectural_synthesizer.py`.
5. **Duplication and error handling.** Markdown-fence stripping appears about 10 times and the snake_case helper in 5 files; 19 `except: pass/continue` blocks in the pipeline and service layer.
6. **Size.** `services.py` (about 2,400 lines), `frontend_planning_engine.py` (about 1,500, missing from the department map), `RequirementControlPanel.tsx` (about 900).
7. **Hard-coded domain term.** `BehaviorInboxPanel.tsx` defaults the aggregate to `'Order'`.
8. **Stale docs.** `.agents/rules/02-frontend-and-ui.md` section 4 (Wayfinder), `vault/01-Architecture/PM-Studio-UX-Architecture-And-Direction.md`, OpenCode mentions in `backend/scripts/`, and the `.gitignore` comment claiming `workspace/` has its own git.
9. **`run.py`.** Unpinned `pip install --upgrade` on every launch, kills any process on ports 8000/8001/5173/5174, and binds services to `0.0.0.0`.

Working rules live in `CLAUDE.md` and `.claude/rules/`.
