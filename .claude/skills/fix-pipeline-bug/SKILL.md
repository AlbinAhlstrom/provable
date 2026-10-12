---
name: fix-pipeline-bug
description: Fix a defect in what the pipeline generates by finding the responsible department, reproducing it in a hermetic test, and fixing it upstream. Invoke as /fix-pipeline-bug followed by a description of the generated-output problem.
argument-hint: "<what is wrong in the generated app>"
disable-model-invocation: true
---

# Fix a pipeline bug

Problem to fix: $ARGUMENTS

1. **Observe.** Read the relevant files in `workspace/` (read only; never edit them). If the problem is visual or runtime, look at it in the running app (`bash .claude/hooks/ensure_app_running.sh`, then the `take_ui_screenshot` skill). Read the recorded run first: `python scripts/trace_report.py` shows which stage failed and why, which stage wrote each file, and the prompt and raw answer of every LLM call (`--full N`); `--compare A B` against an earlier good run shows what changed. Alternatively run the `workspace-inspector` subagent for a traced report.
2. **Locate the department.** Use the symptom-to-file table in `.claude/agents/workspace-inspector.md`. Read that file and the prompt it uses end to end before changing anything.
3. **Find the root cause.** Ask why the stage produced this. Typical causes: an ambiguous or misplaced instruction in a prompt, a schema that lets bad output through, or a contract mismatch between two departments. Do not add a regex repair, a string patch or a "MUST NOT" line.
4. **Reproduce hermetically.** Write a failing unit test against the department's function with a recorded or hand-written LLM response, so no live model call is needed.
5. **Fix upstream.** Change the prompt, schema or contract. Make the failing test pass; confirm the targeted file, then `python -m pytest backend/tests/unit`.
6. **Review.** Run `architecture-verifier` and `code-smell-verifier` on the diff.
7. **Regenerate and compare.** Run the smallest live run that shows the fix (`POST /api/onboarding/page` when only the page is affected, else a kickstart of the same pitch), in the background, and compare the new `workspace/` output with what was wrong. Report wall time, cost in SEK, model and effort. Without an LLM key, say the fix was not verified live.
8. **Commit** with the `commit-task` skill; the commit guard runs the full suite.
