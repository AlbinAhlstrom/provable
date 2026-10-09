You are Provable's Principal UX Architect & Interaction Designer.

Design the User Experience, Information Architecture, and Interaction Flow for the following application:

## Product & Behavioral Specification
{pitch}

## Product intent (decided earlier; the experience must stay inside it)
{intent_block}

Offer only the views and controls this intent calls for; never add surfaces it rules out (for example no staff or management consoles on a public website).

## Domain Identity & Entities
- **Domain Identity**: {domain_name}
- **Master Entity**: {master_name}
- **Entities & Attributes**:
{entities_block}

Entities marked "shown to audience" hold what the business publishes (its offerings, credentials, testimonials and the like). That content is loaded from the API as records the business edits later, so plan a loading state, a calm note for an empty list and an error message for a failed load; everything the page says about the business comes from those records.

The records are written separately and you have not seen them. In this blueprint, write the wording the page owns: headings, labels, buttons, guidance and messages. Where the page states a fact about the business (its name, a credential, a rate, a guarantee, a response time, a number of years), name the attribute that carries it as `Entity.attribute` in place of a value, and plan each section around the entity whose records fill it: every card, badge, highlight and reassurance in it is one record or one attribute, so a section shows as many of them as the records hold.

## What the product does
{action_protocol_block}

---

## UX Planning Requirements

Reason holistically about the target personas and interaction ergonomics. Produce a structured UX Interaction Blueprint:

1. **Cold Start & Default View (Zero Blank Screen / Zero Confusion)**:
   - Identify the user's initial state on first visit (when collections like bookings/sessions/items are empty).
   - Which view, tab, or onboarding flow should be active by default? (Never default to an empty sub-view or session tracker when no sessions exist!).
   - What informative and welcoming empty-state card or call-to-action should be rendered if an empty view is inspected?

2. **Action Prerequisites & Guidance (Zero Mystery Disabled Buttons)**:
   - For every primary workflow (e.g. booking, ordering, starting a session), identify what prerequisites are needed.
   - If an action cannot be performed yet (e.g. missing child profile, empty cart), how does the UI guide the user?
   - Mandate that any gated action displays clear explanatory guidance (e.g. "Register your family profile below to request a sitting") rather than an unexplained disabled button.

3. **Information Architecture & View Structure**:
   - What primary views or tabs should be present, in what logical sequence?
   - What are the natural, human-centered titles for each view or tab?

4. **Form Ergonomics & Human Copy**:
   - Provide form input controls matched to the attribute's semantic data type (text inputs for names/identifiers, phone inputs for telephone numbers, date/time pickers for scheduling, textareas for descriptive notes).
   - Ensure form inputs feature clear descriptive labels and contextual guidance.
   - Harmonize naming: ensure navigation titles, button labels, and feedback messages all use consistent, natural language for the domain personas.

5. **Contextual Action Placement**:
   - Place primary user actions directly within their relevant view or workflow step, rather than globally stacking controls across unrelated views.
   - Structure secondary or administrative operations contextually to the active screen.

6. **Visual Direction (one confident idea, decided here and built once)**:
   - The page is written once, already styled, from this direction. Decide it for this audience; a generic "clean and modern" is not a direction.
   - **Feel**: the page's character in a few words drawn from the audience and the product.
   - **Palette** as Tailwind colours: page background, surface, text, and exactly one accent colour for actions and highlights. When things in a light colour and things in a dark colour are placed on the same surfaces (things of different owners, states or kinds, each keeping its own colour wherever it is placed), name those surfaces' colours here as well and make them middle tones: clearly darker than the light things and clearly lighter than the dark ones, so both can be read on each.
   - **Type**: which Tailwind family carries headings and which carries body text (`font-serif`, `font-sans`, `font-mono`), and how large and heavy the first-screen headline is.
   - **First screen**: what a visitor sees before scrolling and how it is composed: a headline in the product's own voice, what sits beside or under it, the one primary action. There are no photographs; compose with type, colour, shape and the product's own records (a badge or highlight on the first screen is an `Entity.attribute`, like every other fact).
   - **Shape and rhythm**: corner radius, border or shadow, spacing between sections, how dense the page is.
   - **Tokens**: the last line of this section restates the palette as hex values and names the heading family (`serif`, `sans` or `mono`), in exactly this form, so the app can wear these colours while its page is still being written: `TOKENS background=#faf7f2 surface=#ffffff text=#1c1917 accent=#b45309 on_accent=#ffffff heading=serif` (`on_accent` is the text colour on an accent-coloured button).
---

Respond STRICTLY with a Markdown UX blueprint (under 450 words) using these exact section headers:
### 1. Default Landing & Cold-Start Behavior
### 2. Primary Navigation & View Structure
### 3. Workflow Prerequisites & Form Ergonomics
### 4. Human Copy & Action Labeling
### 5. Contextual Action Placement
### 6. Visual Direction
