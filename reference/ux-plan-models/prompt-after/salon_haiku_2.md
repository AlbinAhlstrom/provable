### 1. Default Landing & Cold-Start Behavior
- On arrival the page opens on the booking form at step 1 "Service", with the service list visible and no selection.
- Steps 2 "Day" and 3 "Time" are muted and unclickable; no days appear until a service is chosen.
- Services load as `Service.name` and `Service.duration_minutes` rows; while loading, three grey placeholder rows show.
- No services published: a calm line reads "No services are offered online yet. Please check back soon." with no form controls beyond the header.
- Service load failed: "We could not load the services. Try again." with a "Try again" button in the card.
- Days load per selected service from `TimeSlot.slot_date`; while loading, the day row shows grey placeholder buttons.
- A day with no free times for the service is faded and unclickable (per specification).
- A day with no free times in the time grid shows "No times left on this day." in place of the grid.
- Time slots load from `TimeSlot.start_time` and `TimeSlot.end_time`; while loading, eight grey placeholder buttons show.
- Time load failed: "We could not load times. Try again." with a "Try again" button in the step.
- Confirmation panel is never shown on arrival; it appears only after a successful submit.

### 2. Primary Navigation & View Structure
- One view: the booking page, with a header and one card holding steps 1 to 4.
- No navigation menu, tabs, or links to other pages.
- Header holds the salon booking title and "Book your appointment".
- Confirmation panel replaces the card contents in the same view; no separate route.
- "Book another" returns to the same view at step 1.

### 3. Workflow Prerequisites & Form Ergonomics
- Steps 2 to 4 are shown muted with the line "Choose a service first." beside the step heading until a service is selected.
- Step 3 is shown muted with the line "Choose a day first." until a day is selected.
- Step 4 details fields are shown muted with the line "Choose a time first." until a time is selected.
- Changing the service clears the chosen time and recalculates slots; the summary hides.
- Book button is disabled until service, slot, name, phone and email are valid; beside it, the line "Still needed: " followed by the missing items (for example "a time, your phone number").
- Name: text input, label "Name", refused with "Enter your name (up to 80 characters)." when empty or too long.
- Phone: telephone input, label "Phone", refused with "Enter a phone number with 7 to 15 digits." when invalid.
- Email: email input, label "Email", refused with "Enter an email address, such as name@example.com." when invalid.
- Validation runs when a field is left; invalid fields show a red outline and the message below.
- Slot taken at submit: no booking created, error banner "That time was just taken. Please choose another time.", slot list refreshes.
- Sending failure: error banner "We could not send your request. Please try again."
- Clicks on booked or past slots are ignored with no change to selection.
- Double submit ignored while "Sending…" shows.

### 4. Human Copy & Action Labeling
Seen:
- "Book your appointment" (header subtitle, under "Salon booking" title).
- "1 Service", "2 Day", "3 Time", "4 Your details" (step headings, on the step header line).
- "Choose a service first.", "Choose a day first.", "Choose a time first." (step guidance, beside muted headings).
- "No times left on this day." (time step, replaces grid).
- "Name", "Phone", "Email" (field labels in the details step).
- "Enter your name (up to 80 characters).", "Enter a phone number with 7 to 15 digits.", "Enter an email address, such as name@example.com." (field messages, below fields).
- "Still needed: …" (line beside the disabled button).
- "Request booking" (primary button); "Sending…" (while submitting).
- "That time was just taken. Please choose another time." and "We could not send your request. Please try again." (error banner).
- Summary line: "{Service.name}, {day}, {start} to {end}" (above button, hidden until a time is chosen).
- Confirmation heading: "Request received"; badge "Requested"; labels "Service", "Date", "Time", "Name".
- "Book another" (link under confirmation).
- "Try again" (load failure buttons).
- "No services are offered online yet. Please check back soon." (empty services).

Spoken only:
- "Services" list group; "Day" option group; "Time" option group.
- "Selected" / "Not selected" state on option rows and buttons.
- "Unavailable" on faded days and slots.
- Check icon in confirmation: "Booking requested".
- Loading placeholders: "Loading".

### 5. Contextual Action Placement
- Service selection sits in the service rows of step 1 themselves.
- Day buttons sit in the step 2 row directly under the step heading.
- Time slots sit in the step 3 grid directly under the step heading.
- Summary line and "Request booking" sit together at the foot of the card, below step 4.
- Error banner sits directly above "Request booking".
- "Book another" sits below the confirmation summary.
- "Try again" sits inside the failed load's own step.

### 6. Visual Direction
- **Feel**: a calm, friendly appointment widget, like a simple salon booking form that feels soft and unhurried.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; muted text #9A9A9A; accent dusty rose #C77D8E (pressed #A9606F, pale fill #F8E6EA); border #D9D2CB; hover fill #F3ECE6; error red #C0392B with pale fill #FBE9E7; amber Requested #E0A030; green Confirmed and check #3E8E5A.
- **Type**: `font-sans` for headings and body; step headings 16px bold, header title 28px bold; largest text on first screen is the 28px bold title.
- **First screen**: the header band with title and subtitle at top, then the card opening directly on step 1 with the service rows visible; no marketing copy above the form.
- **Form of the main view**: a single centred card, 640px max width, full width on phones, with four stacked numbered steps; service rows are full-width stacked rows 56px tall; day buttons are 64px wide by 64px tall in a horizontal row that scrolls on narrow screens; time slots are 96px wide by 40px tall in a grid of as many columns as fit, wrapping on phones; empty states use one line in the step's place.
- **Shape and rhythm**: 8px corner radius on card, 6px on rows and buttons, soft shadow (0 2px 8px rgba(43,43,43,0.08)); 32px between steps, 24px card padding; medium density.
- LAYOUT columns=1 rows=auto
- TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans