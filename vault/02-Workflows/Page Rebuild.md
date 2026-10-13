# Page Rebuild

Writes a generated app's page again, against the domain it already has. Use it when a change only alters how pages are
planned, written, audited or reviewed: it costs about a tenth of a kickstart in tokens and about a quarter of its time
(measured on one app: 4 model calls and 57k tokens in 105 s, against 42 calls and 532k tokens in 430 s for its kickstart).

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
- A product built from a contract ([[ADR-011 The Product Contract]]) is rebuilt from the contract's own page plan
  (`PageBrief.plan`), and no model is asked for another: the plan names each part by the role and name the page
  tests find it by, and a second plan does not. Until this was so, a rebuilt page was written with an empty parts
  list and never checked for its parts. A product built without a contract still has its plan written.
- The domain, its tests, the seed records and the action protocol are not touched.
- It records itself like any run (`logs/runs/<id>_page_...`), so `scripts/trace_report.py` and `--compare` work.

## When it is not enough

- It fails loudly when there is nothing to rebuild from: no kickstart yet, a build from before the decomposition was
  kept, or a workspace that was reset since.
- It says nothing about the domain. A change to decomposition, actions, test writing or code writing needs a kickstart.
- It stays on one product. A prompt change still has to be checked on a pitch of another kind
  (`.claude/rules/pipeline.md`, "Prompts are domain-neutral").

## Wiring only

`POST /api/onboarding/wiring` writes the current app's routers and API clients again with today's generator
(`backend/onboarding/wiring.py`, use case in `backend/service_layer/app_wiring.py`). Both are written from the kept
decomposition and never by a model, so nothing is lost and no model is called. Use it when a correction to
`skeleton_builder.py` has to reach an app that exists; the domain classes, the page and the saved records are left as
they are. It answers with the files it rewrote, and adds none the app does not have.
