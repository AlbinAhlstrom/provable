# Run Recorder

Every kickstart and every spec execution records itself to its own folder, so a surprising result can be diagnosed
after the fact instead of re-run under a debugger. Implemented in `backend/run_recorder.py` on top of the step tracer
in `backend/pipeline_trace.py`; read it with `scripts/trace_report.py`.

## What a run folder holds (`logs/runs/<timestamp>_<kind>_<label>/`)

| File | Content |
| :--- | :--- |
| `run.json` | The pitch, start time, git commit, branch and uncommitted files, model, per-stage model overrides, reasoning effort. Answers "was this run before or after my change?". |
| `trace/NNN_<step>.json` | One file per traced step and per LLM call, in call order: input, output, duration, seconds since the run began (`t_offset_s`), thread, caller chain. LLM calls add the model, token counts (prompt, completion, total, hidden reasoning, cached), prompt and response size, completion tokens per second, finish reason and the provider error. The full prompt and raw answer are there. |
| `summary.json` | Verdict (`ok`, `degraded`, `error`), a `timeline` (wall time inside stages, outside any stage, and the sum of stage times), every stage with status, start offset, duration, notes, the error that failed it and the files it changed (line count and line delta per file), a provenance map (file -> last stage that wrote it), LLM totals per stage with their cost in USD and SEK, and the run's result (stage failures, spec conflicts, timings, QA verdict, frontend inventory). |
| `workspace/` | A copy of the generated `src/` and `tests/` and the QA screenshots, kept after the next run overwrites `workspace/`. Per device there is the first screen at device density (`qa_<device>_<w>x<h>.png`) and the whole page at one image pixel per CSS pixel (`qa_<device>_full.png`). |

`logs/runs/LATEST` names the newest run. Recording is always on. `PROVABLE_RUNS_DIR` moves the folder,
`PROVABLE_RUNS_KEEP` (default 30) bounds how many runs are kept, `PROVABLE_RECORD_RUNS=0` switches it off.
The test suite points it at a throwaway directory.

## Stages and failure

The kickstart marks its stages (intent, expansion, decomposition, skeleton, persistence, shell and acceptance, spec
review, seed data, UX plan, action protocol, presentation, QA, visual review). A stage that does not deliver is `failed` with its reason; a
stage that cannot run because an earlier one failed is `skipped` with the reason (the visual review never looks at a
page the presentation stage failed to deliver or that did not pass QA). Any failed stage makes the run `degraded`, and the Studio shows the failures
and the run id when a build finishes degraded, and the build time and run id when it succeeds.

## Stages that run at the same time

Spec review, seed data and the UX plan run alongside the action protocol, and the presentation follows
(`backend/onboarding/synthesis_stages.py`); QA audits its three devices in parallel browsers. Three things keep the
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
  exports nothing (`export {};`) is not written. When the page is written, the skeleton's scaffold it no longer imports is removed and listed as `removed_scaffold`. The `behaviour_specs` stage is the domain round (actions and rules in one pass of the test loop): it notes which actions have a method (`implemented`), which do not (`missing`, which fails the stage) and how each action's spec ended (`runs`). The `page_revisit` stage is skipped with its reason when the classes hold the fields the page was written for, and otherwise notes what `changed`. It also notes the specs it `fulfilled` and the ones it did not (`unfulfilled`, with each reason, which fails the stage).
- **UX plan** notes whether it carries a visual direction (section 6 of the blueprint).
- **Visual review** notes its verdict (`clean`, `repaired`, `unrepaired`, `reverted`, `error`), the problems it saw,
  every class change with whether it was applied and why not, and what it could not repair. A repair the applier refuses is sent back to the reviewer once with the reason (`attempts` is then 2). A problem that is still on the page afterwards (`not_repaired`), or repairs taken back because the page no longer passed QA, are kept as `remarks` on the stage: the page passed QA, so they are a matter of looks and the build is not degraded. Only a review that could not look at all (a provider or parse error) fails the stage.
- **QA** notes the verdict, the rework attempts and its warnings (text cut off at the screen edge). Each device result
  in the trace holds its metrics, how long it took and both screenshots; the desktop result also holds what using each form showed (`forms`: the requests it sent and the API's answers).
- **Frontend inventory** (`backend/onboarding/app_inventory.py`, in the result as `app_inventory`): every source file
  under `src/`, its line count, and the files `src/main.tsx` never reaches through imports. It only reports.

## Reading a run

```
python scripts/trace_report.py                  # latest: verdict, wall time, stages, files, visual repairs, inventory, LLM totals, call tree
python scripts/trace_report.py --list           # every run with its verdict and its cost in SEK
python scripts/trace_report.py --compare A B    # code version, stage status changes, frontend size, files written differently
python scripts/trace_report.py <run> --full 12  # the whole input/output of one step (prompt and raw answer)
python scripts/trace_report.py --backfill-costs # price the runs recorded before costs were stored
```

Related: [[Helper Scripts]], [[Agent Execution Loop]].

## Cost

Every summary holds what the run's LLM calls cost: `llm.cost_usd` and `llm.cost_sek` in total and per stage, the
exchange rate used (`usd_to_sek`), the date of the price list (`prices_as_of`) and `unpriced_models`.

- Prices live in `backend/llm_cost.py`: list prices in USD per million tokens for fresh input, cached input and output. Hidden reasoning tokens are billed as output.
- A model the table does not hold has no price. Its run shows "cost unknown" and names the model, so a missing price never reads as a cheap run. Add the model to the table and run `--backfill-costs`.
- `PROVABLE_USD_SEK` sets the exchange rate (default 10.0).
- The cost is computed from the trace, so `--backfill-costs` can price any older run. It only fills summaries that hold no cost; it does not reprice a run after a price change.

## Replaying a recorded run

Working on one stage need not pay for all the others. A kickstart request that names recorded runs is answered from
them wherever it asks exactly what they asked (`backend/llm_replay.py`):

```json
{"pitch": "Minesweeper", "replay": ["<kickstart run id>", "<its rule tests run id>"]}
```

- A question is the same when the stage, prompt, schema or JSON mode, model and effort all are. Change one stage's prompt and that call goes to the model; any later stage whose input changed with it does too.
- A question asked several times gets its recorded answers in order; once they are used up, the model answers.
- Never replayed: calls with screenshots (the trace keeps paths, not pictures) and calls that failed.
- A replayed call costs nothing and is counted as `replayed` in the summary, in total and per stage; `run.json` names the runs replayed (`llm.replay`). `trace_report.py` shows both.
- The page tests that follow the kickstart replay the same runs.
- Replay repeats one run of the model. It says nothing about how often a stage answers well: measure that with live calls.
