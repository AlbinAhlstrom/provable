---
name: acceptance
description: Six-step test-first workflow (self-critique, acceptance criteria, red, implement, verify, handover) for features and refactors in the Provable engine. Use for any non-trivial code change.
---

# Acceptance workflow

Run this inside a single working context. Do not hand planning, tests and implementation to different agents; verification is the only step that benefits from a separate, clean context.

1. **Self-critique the plan.** Edge cases and failure modes; latency (no synchronous network in hot paths); architectural fit (no string hacks or special cases, use contracts and schemas); UX and accessibility when UI is touched.
2. **Write acceptance criteria.**
   - Automated: exact test commands and expected results, schema and payload assertions, non-functional checks (no `import db.store` leaks, pure domain dataclasses).
   - Manual: what the user should look at in the live preview (`http://localhost:5174`) or PM Studio (`http://localhost:5173`).
3. **Red.** Write `backend/tests/unit/test_<target>.py` first (hermetic, `FakeUnitOfWork`). Run only that file and confirm it fails for the right reason.
4. **Implement** inside the DDD layers (`.claude/rules/engine-tdd.md`). Fix root causes upstream; no regex post-filters, no prohibition patches.
5. **Verify.** Targeted tests, then `python -m pytest backend/tests/`. On failure, read the traceback, fix the cause, repeat. Then run the `architecture-verifier` and `code-smell-verifier` subagents on the diff, passing only the diff and the intent.
6. **Hand over.** Summarise what changed and the test results, list the manual checks for the user, update the top of `vault/HANDOVER.md` if state or decisions changed, then follow the commit policy in CLAUDE.md (`commit-task` skill).
