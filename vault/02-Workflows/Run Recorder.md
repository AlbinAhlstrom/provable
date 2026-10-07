# Run Recorder

Every kickstart and every spec execution records itself to its own folder, so a surprising result can be diagnosed
after the fact instead of re-run under a debugger. Implemented in `backend/run_recorder.py` on top of the step tracer
in `backend/pipeline_trace.py`; read it with `scripts/trace_report.py`.

## What a run folder holds (`logs/runs/<timestamp>_<kind>_<label>/`)

| File | Content |
| :--- | :--- |
| `run.json` | The pitch, start time, git commit, branch and uncommitted files, model, per-stage model overrides, reasoning effort. Answers "was this run before or after my change?". |
| `trace/NNN_<step>.json` | One file per traced step and per LLM call, in call order: input, output, duration, seconds since the run began (`t_offset_s`), thread, caller chain. LLM calls add the model, token counts (prompt, completion, total, hidden reasoning, cached), prompt and response size, completion tokens per second, finish reason and the provider error. The full prompt and raw answer are there. |
| `summary.json` | Verdict (`ok`, `degraded`, `error`), a `timeline` (wall time inside stages, outside any stage, and the sum of stage times), every stage with status, start offset, duration, notes, the error that failed it and the files it changed (line count and line delta per file), a provenance map (file -> last stage that wrote it), LLM totals per stage, and the run's result (stage failures, spec conflicts, timings, QA verdict, frontend inventory). |
| `workspace/` | A copy of the generated `src/` and `tests/` and the QA screenshots, kept after the next run overwrites `workspace/`. Per device there is the first screen at device density (`qa_<device>_<w>x<h>.png`) and the whole page at one image pixel per CSS pixel (`qa_<device>_full.png`). |

`logs/runs/LATEST` names the newest run. Recording is always on. `PROVABLE_RUNS_DIR` moves the folder,
`PROVABLE_RUNS_KEEP` (default 30) bounds how many runs are kept, `PROVABLE_RECORD_RUNS=0` switches it off.
The test suite points it at a throwaway directory.

## Stages and failure

The kickstart marks its stages (intent, expansion, decomposition, skeleton, persistence, shell and acceptance, spec
review, seed data, action protocol, presentation, styling, QA). A stage that does not deliver is `failed` with its reason; a
stage that cannot run because an earlier one failed is `skipped` with the reason (styling never restyles a skeleton
the presentation stage failed to replace). Any failed stage makes the run `degraded`, and the Studio shows the failures
and the run id when a build finishes degraded, and the build time and run id when it succeeds.

## Stages that run at the same time

Spec review and seed data run alongside the action protocol and the presentation
(`backend/onboarding/synthesis_stages.py`); styling restyles its components in parallel. Three things keep the
record truthful when stages overlap:

- **Files.** A stage's changed files are the workspace diff between its start and end, which overlapping stages would
  share. A concurrent stage therefore declares what it `owns` (`stage_begin(name, owns=(...))`, `()` for a stage that
  writes nothing): it is credited with exactly those paths, and stages open alongside it are not.
- **Call tree.** The tracer's caller chain is per thread. Work handed to a thread pool goes through
  `pipeline_trace.bind_context(fn)`, so a worker's steps and LLM calls stay under the step that started them.
- **Failure reasons.** `agent_orchestrator.LAST_LLM_ERROR` is per thread, so one stage's call cannot clear or overwrite
  the reason another stage is about to report.

Because stages overlap, stage durations no longer add up to the run's duration: the `timeline` and each stage's start
offset say where the wall time went.

## What the stages report about their output

- **Presentation** notes the line count of each component it wrote and the optional files it left out. A block that
  exports nothing (`export {};`) is not written.
- **Styling** notes, per component, whether it was restyled and why not, how many attempts it took and the verifier's
  verdict on each refused one, the line count before and after, and the visitor-facing text the restyle added or
  dropped (`StyleResult`). The styling prompt keeps the copy verbatim, so a non-empty text diff is drift worth reading.
- **QA** notes the verdict, the rework attempts and its warnings (text cut off at the screen edge). Each device result
  in the trace holds its metrics, how long it took and both screenshots.
- **Frontend inventory** (`backend/onboarding/app_inventory.py`, in the result as `app_inventory`): every source file
  under `src/`, its line count, and the files `src/main.tsx` never reaches through imports. It only reports.

## Reading a run

```
python scripts/trace_report.py                  # latest: verdict, wall time, stages, files, styling changes, inventory, LLM totals, call tree
python scripts/trace_report.py --list           # every run with its verdict
python scripts/trace_report.py --compare A B    # code version, stage status changes, frontend size, files written differently
python scripts/trace_report.py <run> --full 12  # the whole input/output of one step (prompt and raw answer)
```

Related: [[Helper Scripts]], [[Agent Execution Loop]].
