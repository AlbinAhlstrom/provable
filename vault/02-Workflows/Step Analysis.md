# Step Analysis

How one pipeline step's prompt is measured and improved without running the pipeline. It is the `step-analysis`
skill (`.claude/skills/step-analysis/`); this page says why the method is what it is.

## The method

1. Fix the step's inputs for three pitches of unrelated kinds, as the pipeline hands them over today.
2. Run the step's prompt alone on Opus, Sonnet and Haiku (`step_bench.py run`).
3. Read the answers side by side. Where a weaker model differs from the best one, find the sentence of the prompt
   that caused it. Count with a checklist of wanted and unwanted things (`step_bench.py score`), then read what the
   checklist reported.
4. Rewrite the prompt at the cause, run again, and repeat the final draft at least twice.
5. Land the prompt with a test, keep the evidence under `reference/<step>-models/`, and report speed, cost and
   quality before and after.

## Why it is done this way

- **The best model shows what the step can deliver.** Where it and a cheap model differ, the prompt left something
  to judgement. Twice so far the cause was an instruction the strong model overrode and the weak one obeyed: a word
  cap in the pitch expansion, a mandate for guidance text in the UX plan.
- **Isolated, a step costs a few SEK and seconds.** A kickstart costs minutes, changes every other step's output as
  well, and so cannot say which step made a page better. See also [[Page Rebuild]] and [[Run Recorder]].
- **Three kinds of pitch**, because a prompt is read for every pitch. A draft that took needless text out of a game
  also took needed guidance out of a form; only the third pitch showed it.
- **A checklist is read, not trusted.** Patterns miss synonyms and match inside negations. Once a checklist passed a
  draft that had cut a feature, because the word appeared in the list of things left out.
- **Repeats.** One sample hid a layout line that was wrong half the time.

## What it does not show

What the pipeline builds from the step's output. A richer plan is only better if the page is. The smallest run that
shows it (a page rebuild or a kickstart) is a separate, approved step.

## Results so far

- Pitch expansion: `reference/expansion-models/`. It now runs on Sonnet under the `anthropic` provider
  ([[LLM Abstraction and Prompts]]).
- UX plan: `reference/ux-plan-models/`.
