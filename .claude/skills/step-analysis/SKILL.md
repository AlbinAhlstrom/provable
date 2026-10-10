---
name: step-analysis
description: Benchmark one pipeline step in isolation on Opus, Sonnet and Haiku, find why the cheaper models fall short, and rewrite the step's prompt to close the gap. Reports speed, cost and quality before and after. Invoke as /step-analysis followed by the step (its prompt file or stage name).
argument-hint: "<step: prompt file or stage name>"
---

# Analyse one pipeline step

Step to analyse: $ARGUMENTS

The aim is a prompt on which the cheap model writes what the best model writes. The best model's answer shows what
the step can deliver; where a weaker model differs, the prompt left something to judgement. Calls go straight to the
provider and write only to a scratch folder: the app, `workspace/` and the database are not touched.

Worked examples: `reference/expansion-models/` and `reference/ux-plan-models/`.

## 1. Fix the inputs
- Find the step's prompt in `backend/prompts/` and the function that fills it. List its placeholders.
- Build `cases.json` in the scratch folder: `{"<case>": {"<placeholder>": "<value>"}}`, one case per pitch.
- Use **three pitches of unrelated kinds** (for example a product known by sight, a tool, a form with steps). One
  pitch tunes the prompt to that pitch.
- The values are what the pipeline would hand the step **as it stands today**: run the upstream steps once (their
  functions, or `step_bench.py` on their prompts) and reuse the result for every model and every draft. A recorded
  trace (`logs/runs/<id>/trace/`, `reference/*/trace/`) is a fine source when the upstream prompts have not changed.

## 2. Baseline
```
python .claude/skills/step-analysis/scripts/step_bench.py run --template backend/prompts/<step>.md \
    --cases <scratch>/cases.json --out <scratch>/out --tag before
```
Options: `--models haiku,sonnet,opus`, `--effort low`, `--repeat N`, `--json` for a step that answers in JSON.
Nine calls of a planning step cost about 3 SEK; say so before a step with a much larger prompt.

## 3. Read, then count
- Read every answer of one pitch side by side before scoring anything. Note where the models differ: what one
  states and another leaves to a phrase, what one adds that nobody asked for, what breaks the format the next step
  parses.
- For each difference, find the sentence of the prompt that caused it. Typical causes: a cap or a mandate the
  stronger model overrides by judgement and the weaker obeys; an instruction with no stated reader or reason; two
  things sharing one heading; an example from one kind of product; a contract described in one product's words.
- Write `checklist.json`: per case, `wanted` (what the next step needs from this one) and `unwanted` (inventions,
  vague phrases), each a name and a regex over the lowercased answer. Score with
  `step_bench.py score --checklist ... --out ... <tag>`.
- **The checklist is a first pass.** Open every hit and every miss it reports. Patterns miss synonyms and match
  inside negations ("no status line"); repair the pattern, and report by reading where the two disagree.

## 4. Rewrite
- Change the cause, not the symptom: say who reads the output and what they do with it, ask for the missing thing
  under a heading or line of its own, replace a total cap with a limit per line. No "MUST NOT" lines
  (`.claude/rules/pipeline.md`), and keep the prompt domain-neutral.
- Draft in the scratch folder (`prompt_v1.md`, ...) and run each draft with a new `--tag`. One change per draft
  where the cause is uncertain.
- Check every draft on all three pitches: a fix for one kind of product often costs another (a draft that removed
  needless text from a game also removed needed guidance from a form).
- Run the final draft at least twice per pitch on the models that matter (`--repeat 2`). One sample hides a miss
  that happens half the time.
- Stop when a remaining gap survives two drafts aimed at it. Report it as left.

## 5. Land it
- Test first: a unit test that pins the sentences carrying the new contract, failing on the old prompt. Then
  replace the prompt and run the fast tier.
- Keep the evidence: `reference/<step>-models/` with `cases.json`, `checklist.json`, the before and after folders
  (prompt, answers, `runs.json`) and a short README.
- Commit the prompt with its test and the reference folder.

## 6. Report
- One table: per model, before and after: quality (wanted stated, unwanted found, and the counts taken by reading),
  time, cost per call in SEK, words written.
- What separated the models, as causes in the prompt. What the rewrite changed. What is left.
- Whether the step should run on another model, with the price of that.
- Say what was not measured: an isolated step shows what the step writes, not what the pipeline builds from it.
  Offer the smallest run that would show it (a page rebuild, a kickstart) and wait for a yes.
