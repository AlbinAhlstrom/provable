# Struggle Corpus

Where recorded runs got stuck, grouped, so the commonest cause is traced and fixed first. Implemented in
`backend/struggle_corpus.py` on top of the run folders the [[Run Recorder]] writes; read it with
`scripts/struggle_corpus.py`. It calls no model and changes no prompt.

## What counts as a struggle

A moment a run's own record says something went wrong. Nothing is read out of prose.

| Source | Struggle |
| :--- | :--- |
| A verifying step's recorded output | The RED gate rejected a test, a page test failed or could not find its control, QA did not pass or needed rework, the visual review found a problem (repaired or not), the spec review found a conflict, a first test was reconsidered, a rule fix did not hold. |
| A second code answer for a class | The code writer needed its retry (`tdd.green_together/retried`). |
| A traced step's `error` | The step raised. An exception is recorded by every step it leaves; it is counted at the one that raised it. |
| A stage in `summary.json` | The stage failed. A skipped stage is not a struggle. |

Struggles are grouped by the step that reported them and the verdict it gave (`tdd.red_gate/REJECTED_TAUTOLOGY`).
A new verifying step is added to the table at the top of the module.

## What an entry holds

- `occurrences`, against the corpus's `checks` for that step: how often it happened of how often the step ran.
- `runs`, `labels`, `models`, `first_seen`, `last_seen`, `last_commit`: whether it still happens, and on what.
- `nearest_llm`: the LLM call that came nearest before it in the call tree. It is the prompt to read first, not a
  verdict on which prompt is at fault: a failing page test can mean the page is wrong and the test is right.
- `examples`: the latest three, each with its run, trace file and reason.
- `review`: `status` (`candidate` until someone traced it), `cause` and `knowledge`. Written by whoever traced the
  cause, kept by every later build.

## How it is kept

The corpus is `logs/struggle_corpus.json` (`PROVABLE_STRUGGLE_CORPUS` moves it). The recorder prunes old run
folders, so a run is counted once and its counts stay after its folder is gone. A run still in progress (no
`summary.json`) is left for the next build.

```
python scripts/struggle_corpus.py             # add the runs not yet counted, list every kind of struggle
python scripts/struggle_corpus.py --show ID   # one entry in full
python scripts/struggle_corpus.py --runs minesweeper   # each run of a pitch scored by its fix-ups
```

## Fix-ups per run

Every struggle is a fix-up: work sent back, retried or repaired, which costs time. `--runs PITCH` lists each
finished run whose folder name holds PITCH with its fix-ups in all and by step; a run with none is clean, right
the first time. Comparing runs of one pitch shows which step varies most.

## What it is for

An entry is a pointer to a root cause, not a fix. Trace it with the `fix-pipeline-bug` skill or [[Step Analysis]]
and fix the stage's prompt, schema or contract; then record the cause in the entry's `review`.

An entry seen for one kind of product only cannot become a prompt rule (prompts are domain-neutral): `labels` says
which runs it was seen on. Sending an entry's `knowledge` to a model as extra context is not built; it would be a
prompt change like any other, checked on a second kind of pitch.
