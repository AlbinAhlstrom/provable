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

The seed prompt states today's date: a date the audience acts on (an open shift, a bookable session) is written as upcoming, so a page that offers times has times to offer.

## Lists are entities, facts are attributes

A page that wants three credential cards but is given one `certifications_summary` string writes the cards itself,
as fixed text: claims about a real business that nobody entered and the owner cannot edit. Three contracts prevent it:

- **Decomposition**: whatever the business publishes as several items of one kind is its own shown-to-audience entity
  with one record per item.
- **UX plan**: it is made before the records exist, so it writes the page's own wording (headings, labels, buttons,
  guidance) and names the attribute that carries a fact (`Entity.attribute`) instead of writing a value.
- **Presentation**: a section has one item per record; headings and labels state nothing about the business.

The visual review reports what still slips through (see [[Automated-Verification-And-Self-Healing-Pipeline]]).

## Scaffold and the written page

The skeleton writes a table view per entity and one shared client, which is what the app shows until the presentation
stage writes the real page. When that page is written, the scaffold it no longer imports is removed
(`app_inventory.remove_unreachable`). A later presentation spec changes the aggregate's own view when the page renders
it, otherwise the rendered view that loads the aggregate's records (`presentation_specs.target_view`); a view the page
does not render is never edited.

## Parts live inside their owner

An entity that only exists inside one aggregate root (a board's squares, an order's lines) is marked by the
decomposition as not an aggregate root, related to that root. `backend/onboarding/owned_parts.py` turns it into a list
attribute on its owner (`AttributeSpec.item_name`, `item_attributes`) and removes it from the stored entities: it gets
no module, repository, router or client of its own, and specs that targeted it target its owner. The owner's class
holds the parts as plain records and documents what one holds, so the methods and rules written for the owner can read
and change them (a game can look at its board). Stored as a separate collection, the owner's behaviour could not see
them. Only a part with exactly one owning root is embedded.

The generated response schemas allow extra fields, so a field the domain class grows later (through a spec) is served
by `GET` as well as by the action that set it.

## The page reaches every entity its audience works with

The interface is given a client for the master, for every other entity the audience creates and for everything shown
to it (`DomainStructureSchema.presented_entities`). The users of an internal tool create customers, jobs and invoices
alike; with a client for the master only, the page had no way to list or create the others. Each action in the
protocol names the entity that owns it and that entity's client, and the presentation is shown the domain class of
every created entity, so a job's action is sent to the job and not to the customer it belongs to.

