### 1. Default Landing & Cold-Start Behavior
- Service records fill the "Choose a service" card: each row shows `Service.name` and `Service.duration_minutes` as "45 min".
- Service list while loading: three grey placeholder rows, no text.
- Service list when empty: "No services are offered right now." in grey, inside the card.
- Service list when the load fails: "Services could not load. Try again." with a "Try again" button.
- TimeSlot records fill the day strip: each chip shows the weekday and date from `TimeSlot.slot_date`, with state marking the day.
- TimeSlot records fill the times grid: each button shows `TimeSlot.start_time` and its `TimeSlot.state`.
- Day strip and times card while loading: grey placeholder chips and buttons, no text.
- Times load failure: "Times could not load. Try again." inside the times card, with a "Try again" button.
- The page opens on step 1 with no selection. Steps 2 to 4 are visible beneath it, not yet usable.
- The day strip opens with all 14 days shown, none selected, today marked with a plum dot.
- The confirmation card is not shown on arrival.

### 2. Primary Navigation & View Structure
- The page is one view with no tabs, menus or separate pages.
- Steps are cards stacked top to bottom in the order: services, day, time, details, then the button.
- After success, the step cards are replaced by the confirmation card on the same page.
- "Book another" returns the same page to step 1 with everything cleared.
- No navigation bar, sign-in or links to other pages.

### 3. Workflow Prerequisites & Form Ergonomics
- The day strip is shown faded until a service is chosen, with the line "Choose a service first" above it.
- The times card is faded with "Pick a service and day first", as the specification states.
- The details card is shown but its fields accept input at any time; validation runs on submit only.
- Request booking is disabled until service, day and time are chosen.
- Beside the disabled button, one line reads "Still to choose: service, day, time" listing only what is missing.
- Changing the service clears the chosen time with no message.
- Choosing a day clears the chosen time and loads that day's free times.
- Name is a text input, labelled "Name", refused with "Enter your name".
- Phone is a telephone input, labelled "Phone", refused with "Enter a phone number with at least 7 digits".
- Email is an email input, labelled "Email", refused with "Enter an email like name@example.com".
- Invalid fields are flagged with a red outline and message only after a submit attempt.
- Fields keep their entries after any failure.
- A slot taken by someone else before submit shows "That time was just taken. Pick another." above the button, times refresh, and the chosen time clears.
- A failed send shows "Could not send. Try again." above the button and keeps all entries.
- Taken or past slots cannot be clicked; clicks do nothing.
- A closed or fully booked day cannot be clicked; clicks do nothing.

### 4. Human Copy & Action Labeling
- Seen: "Salon booking" as the page title; "Book your appointment" as the line beneath it.
- Seen: card titles "Choose a service", "Choose a day", "Choose a time", "Your details".
- Seen: "Choose a service first" above the day strip, and "Pick a service and day first" in the times card.
- Seen: "No times left this day" in the times card when none are free.
- Seen: "Requested" as the badge text on the confirmation card.
- Seen: "Request booking" on the submit button; "Sending…" while sending; "Book another" on the confirmation.
- Seen: "Today" as the text beneath the plum dot's day chip only in the chip's accessible name, not visibly.
- Seen: the summary line in the form "Cut · 45 min · Tue 12 May, 10:30".
- Seen: "Still to choose: service, day, time" beside the disabled button.
- Seen: error messages exactly as the specification gives them.
- Spoken only: "Service list" on the services container; "Day strip" on the day container; "Time slots" on the times grid.
- Spoken only: "Free", "Taken", "Closed", "Selected" on day and time buttons.
- Spoken only: "Remove" on the cleared time when toggled off.
- Spoken only: "Tick" on the green confirmation mark.

### 5. Contextual Action Placement
- Each service row is the action that chooses it; the choice sits on the row itself.
- Each day chip is the action that picks the day; the choice sits on the chip.
- Each time button is the action that picks the time; the choice sits on the button.
- Retry buttons for service and time loads sit inside their own cards.
- "Request booking" sits below the details card, full width, beneath the summary line.
- The failure and slot-taken messages sit directly above "Request booking".
- "Book another" sits inside the confirmation card, beneath the booking summary.
- No action sits in the header.

### 6. Visual Direction

- **Feel**: a warm salon's own booking page: calm, soft, personal, uncluttered.

- **Palette**:
  - Page background: #FAF5EF.
  - Surface (cards, fields): #FFFFFF.
  - Text: #2B1F27.
  - Secondary text: #6F6660.
  - Accent (actions, selected states, headings marks): #5B2A4E.
  - On-accent text: #FFFFFF.
  - Hover fill (time buttons): #EFE3EC.
  - Pressed fill: #431D39.
  - Outline grey (rows, chips, buttons): #D9CFC6.
  - Disabled fill: #D9CFC6, with text #6F6660.
  - Taken fill: #EEE9E4, with text #8A8079.
  - Error: #B3261E.
  - Success tick: #2E7D4F.
  - Requested badge: #E0A526 fill, text #2B1F27.

- **Type**: headings in `font-serif` (semibold, 22px for card titles); body and labels in `font-sans` (regular 16px, labels 14px medium). Largest text on first screen is the page title at 32px, semibold, serif.

- **First screen**: page title and line centred at the top of a 640px column, then the "Choose a service" card directly beneath, starting near the top at 48px from the edge. The column is centred in both directions at the top under the header. Below the fold: day strip, times, details, button. No images, no written introduction beyond the header line.

- **Form of the main view**: a single-column stack of cards, not a grid of cells. The column is 640px wide on desktop: the cards fill it fully, with 24px card padding. Service rows are 56px tall, full card width, stacked with 8px gaps. Day chips are 64px wide by 72px tall in a horizontal strip with 8px gaps, scrolling sideways if they overflow. Time buttons are 48px tall in a four-column grid, each stretched to its share of the card width, with 8px gaps. Each card is as tall as its content, with a minimum of its own rows. Narrow screens: the column takes full width minus 16px side padding; the day strip scrolls sideways; the time grid drops to three columns below 480px.

- **Shape and rhythm**: cards use 16px corner radius, soft shadow `0 4px 16px rgba(43,31,39,0.08)`, no border. Rows, chips, buttons and fields use 10px radius; grey outlines are 1px. Spacing between cards is 24px. Card padding is 24px. Density is airy and generous, with one clear action at a time.

LAYOUT columns=1 rows=auto
TOKENS background=#faf5ef surface=#ffffff text=#2b1f27 accent=#5b2a4e on_accent=#ffffff heading=serif