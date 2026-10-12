### 1. Default Landing & Cold-Start Behavior
- On arrival, the Book page opens directly on step 1 "Service" with the Services list visible; no empty state is shown.
- Header shows "Book your appointment" under the salon booking title; the card is centred below.
- Services list loads from Service records showing `Service.name` and `Service.duration_minutes` as "45 min".
- While Services load: three grey placeholder rows in the same outline shape, no text.
- Services empty: "No services are offered right now." centred in the card, with no other controls.
- Services load failed: "Services could not be loaded." with a "Try again" button that refetches.
- Steps 2–4 are muted and unclickable on arrival; no days appear until a service is chosen.
- Days strip is built from the next 14 calendar days of TimeSlot.slot_date for the chosen service.
- Day with no free times for the service: faded, unclickable.
- Time grid with no open slots on the chosen day: replaced by "No times left on this day."
- Time slots load failed: "Times could not be loaded." with a "Try again" button beside it.
- Booking form is never shown empty of structure; fields are present but the button is disabled.

### 2. Primary Navigation & View Structure
- One view only: the booking page, with a single card holding steps 1 to 4 in order, then the confirmation panel.
- No menu, no tabs, no back navigation; the page is a single scroll.
- Confirmation panel replaces the card contents; it is the only other state of the same view.
- "Book another" returns to the same view at step 1 with all selections cleared.
- Steps 2 to 4 are shown but muted until the prior step is complete, so the path is visible.
- Changing a service after a time is chosen clears the time and reloads the time grid for the new service.
- On narrow screens the card goes full width and steps stack vertically in the same order.

### 3. Workflow Prerequisites & Form Ergonomics
- Step 2 muted line above the day strip: "Choose a service first."
- Step 3 muted line above the time grid: "Choose a day first."
- Step 4 muted line above the fields: "Choose a time first."
- Disabled "Request booking" button sits beside/above the summary line; it shows the summary only once a time is chosen, and it names what is missing in the summary area: "Still needed: name, phone, email" listing only the missing items.
- Clicking a muted step does nothing.
- Choosing a booked or past slot is ignored with no message.
- Name: text input, label "Name", refused if empty or over 80 characters: "Enter your name (up to 80 characters)."
- Phone: telephone input, label "Phone", refused unless 7–15 digits: "Enter a phone number with 7 to 15 digits."
- Email: email input, label "Email", refused unless it looks like an address: "Enter an email address like name@example.com."
- Each field validates on blur only; red outline and message appear below the field.
- Focus shows the dusty-rose outline on every option and field.
- Slot taken at submit: error banner "That time was just taken. Choose another time." and the time grid refreshes.
- Sending failure: error banner "Your booking could not be sent. Please try again."
- Double submit: second click ignored while "Sending…" shows.

### 4. Human Copy & Action Labeling
- Seen: "Book your appointment" (header subtitle), "Salon booking" (title, owned by the salon's name attribute if provided).
- Seen: "1 Service", "2 Day", "3 Time", "4 Your details" (step headings).
- Seen: "Choose a service first.", "Choose a day first.", "Choose a time first." (step guidance).
- Seen: "No days available." (day strip when no day has any free time).
- Seen: "No times left on this day." (time grid empty).
- Seen: "Services could not be loaded.", "Times could not be loaded.", "Try again" (load errors).
- Seen: "No services are offered right now." (empty services).
- Seen: summary line "Service: {name} · {date} · {start} to {end}" shown only when a time is chosen.
- Seen: "Still needed: name, phone, email" (missing items beside disabled button).
- Seen: "Request booking" (primary button), "Sending…" (submitting).
- Seen: error banner texts as in section 3.
- Seen: "Requested" badge (amber) and "Confirmed" badge (green) on the confirmation panel.
- Seen: "Your request has been sent. The salon will confirm it." (confirmation line).
- Seen: "Book another" (link on confirmation).
- Spoken only: "Service option", "Day, {weekday date}", "Time {start}", "Close" on error banner, "Salon booking logo" if any.

### 5. Contextual Action Placement
- Service rows are the action for step 1; choosing one opens step 2 directly below.
- Day buttons sit in the step 2 row; time slots sit in the step 3 grid.
- Summary line and "Request booking" sit together at the foot of the card, above the error banner area.
- Error banner sits directly above the button it concerns.
- Field messages sit directly below their field.
- "Book another" sits below the confirmation panel, centred.
- "Try again" for load errors sits beside the failed list.

### 6. Visual Direction
- **Feel**: a calm, friendly appointment widget, like a simple salon booking form on a warm page.
- **Palette**: page background warm off-white #FAF6F2; surface white #FFFFFF; text charcoal #2B2B2B; accent dusty rose #C77D8E; button pressed #A9606F; option hover #F3ECE6; selected fill #F8E6EA; outline grey #D9D2CB; muted grey #9A9A9A; invalid red #C0392B; error fill #FBE9E7; requested amber #E0A030; confirmed green #3E8E5A; disabled button light grey #E5E1DD.
- **Type**: `font-sans` for headings and body; step headings bold; largest text on first screen is the header title at 28px, weight 700.
- **First screen**: header band at top with title and subtitle, then the card opening with step 1 Service rows visible; no photographs, no intro paragraph.
- **Form of the main view**: a single stacked form in one card, 640px maximum width. Service rows are full-width stacked rows 56px tall. Day buttons are fixed 64px × 72px in a horizontal row that scrolls sideways if needed. Time slots are fixed 96px × 40px in a grid that wraps. Each part keeps its size whatever its content; on narrow screens the day row scrolls and the time grid drops to 3 columns.
- **Shape and rhythm**: corner radius 12px on card, 8px on rows, buttons and fields; card shadow soft (0 4px 16px rgba(43,43,43,0.08)); 24px spacing between steps; 16px within a step; moderately dense.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans