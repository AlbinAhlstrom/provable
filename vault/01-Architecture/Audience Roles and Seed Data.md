# Audience Roles and Seed Data

How the generator decides what the interface is organised around and where a product's visible content comes from.

## Audience role (`EntitySpec.audience_role`)

The decomposition step labels every entity from the product intent (`backend/onboarding/router_engine.py`, prompt `router_decomposition.md`):

| Role | Meaning | Example (public website) |
| :--- | :--- | :--- |
| `created_by_audience` | Records the audience brings into being by using the product | A visitor's inquiry |
| `shown_to_audience` | Content the business publishes for the audience to read | Offerings and rates, credentials |
| `internal` | Back-office state the audience never sees | Audit notes |

`DomainStructureSchema.master_entity()` picks the master aggregate: the first `created_by_audience` entity, else the first aggregate root, else the first entity. Structures without roles keep the old rule. The action protocol and the presentation stage both use it, so a public site is organised around the inquiry its visitors send, not around whichever aggregate was listed first.

## Clients for everything the audience touches

The presentation stage writes a deterministic API client (`src/api/<slug>Client.ts`) for the master and for every `shown_to_audience` entity (`DomainStructureSchema.presented_entities()`), and lists them with their roles in the prompt. The model writes only the UI. A form must report success only after its `create...` call resolves.

## Seed data (`backend/onboarding/seed_data.py`)

An entity only the business can author stays empty on a site with no owner screens, and the model would otherwise invent that content as literals in the UI (a breach of the zero-mock rule). The seed stage asks for 3 to 5 sample records per `shown_to_audience` entity (`prompts/seed_data.md`), proves every record by building it with the generated domain class and serialising it through the response schema (in a subprocess inside the workspace), and writes `src/seed_data.json`. A rejected record is fed back once; a second rejection, a provider error or an unusable answer fails the stage loudly and no file is written.

The generated routers read the seed file on the first request after it appears or changes (the file is written after the workspace API has started) and add records the domain accepts. A record the domain rejects later, for example after a new invariant, is reported in the API log and left out; the API stays up. The page renders these records from the API, and the business edits them like any other record.

## Who performs an action

`performed_by` in the action manifest is `audience` for what the product's users do and `other` for whoever runs it (owner, staff, automation). Only `audience` actions get controls in the interface.

Related: [[Run Recorder]], [[ADR-008 Aggregate Ownership and Audience-Scoped UI]].

## Record identity

Every stored entity (an aggregate root, or anything created by or shown to the audience) has the identity attribute
`id`: the decomposition prompt asks for it and `EntitySpec` guarantees it. The generated repository, router, seed
loader and clients key records by `id`; a model that named its identity `offering_id` made every seeded record
collapse into one. Whoever creates a record does not know its id, so the generated create endpoint assigns one when
none is sent, and the presentation prompt lists the fields a create must carry.
