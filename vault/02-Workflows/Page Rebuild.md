# Page Rebuild

Writes a generated app's page again, against the domain it already has. Use it when a change only alters how pages are
planned, written, audited or reviewed: it costs about a tenth of a kickstart in tokens and about a quarter of its time.

```
kickstart      pitch -> decomposition -> skeleton -> actions -> rules -> UX plan -> page -> QA -> visual review
page rebuild                                                             UX plan -> page -> QA -> visual review
```

## Why it exists

Measured over twelve kickstarts of one pitch: writing the rules' tests and their code (the TDD loop) took about 85% of
the tokens, the page and its gates about 10%. Iterating on a colour or layout problem with full kickstarts paid for
the rules every time and also changed them every time, so two runs could not be compared on the page alone.

## How it works

- `POST /api/onboarding/page` -> `services.rebuild_page` -> `backend/onboarding/page_rebuild.py`.
- The inputs come from the kickstart state as a typed `PageBrief`: the pitch, the intent, the decomposition
  (`KickstartState.structure`, kept by the kickstart for this purpose), the specs and the action protocol.
- The stages are the kickstart's own: `run_ux_plan_stage` and `run_presentation_stage` from
  `backend/onboarding/synthesis_stages.py`, then `run_page_gates` from `backend/onboarding/page_gates.py` (QA with
  one rework, then one visual review). A kickstart ends in the same gates.
- The domain, its tests, the seed records and the action protocol are not touched.
- It records itself like any run (`logs/runs/<id>_page_...`), so `scripts/trace_report.py` and `--compare` work.

## When it is not enough

- It fails loudly when there is nothing to rebuild from: no kickstart yet, a build from before the decomposition was
  kept, or a workspace that was reset since.
- It says nothing about the domain. A change to decomposition, actions, test writing or code writing needs a kickstart.
- It stays on one product. A prompt change still has to be checked on a pitch of another kind
  (`.claude/rules/pipeline.md`, "Prompts are domain-neutral").
