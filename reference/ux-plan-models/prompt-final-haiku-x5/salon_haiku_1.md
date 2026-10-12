### 1. Default Landing & Cold-Start Behavior
- Arrival shows the booking page with header "Salon booking" and "Book your appointment"; step 1 "Service" is active and its list is visible.
- Services load as Service records (name, duration_minutes) from the API; show a loading line "Loading services…" inside the card.
- Empty services list: show "No services are offered yet." in the step 1 area; no other steps shown as clickable.
- Failed services load: show error banner "Services could not be loaded. Try again." with button "Try again".
- Day step (2) and time step (3) are visible but muted and unclickable, with no days shown, until a service is chosen.
- Day picker shows the next 14 days from today as Day buttons from TimeSlot.slot_date; days without free times for the service are faded.
- Slot loading shows "Loading times…" in the time grid area; failed slot load shows the error banner "Times could not be loaded. Try again."
- A day with no free times shows "No times left on this day." replacing the grid.
- Nothing is pre-selected; the summary line is hidden; the button is disabled.
- Details fields (step 4) are empty and visible but muted until a time is chosen.

### 2. Primary Navigation & View Structure
- One view: the booking page; no tabs, menus or other screens.
- Step order: 1 Service, 2 Day, 3 Time, 4 Your details, top to bottom in one card.
- Confirmation panel replaces the whole form card content after successful submit.
- Changing a service after choosing a time clears the time and re-fetches slots for that service.
- "Book another" returns to step 1 with all selections cleared.

### 3. Workflow Prerequisites & Form Ergonomics
- Steps 2–4 stay muted and unclickable until the prior step completes; each carries one line: "Choose a service first." (step 2), "Choose a day first." (step 3), "Choose a time first." (step 4).
- Disabled "Request booking" button sits beside no extra text; its missing items are shown in the summary line area as "Still needed: service, day, time, details" listing only what is missing.
- Service rows are selectable by click, tap, Tab, Enter or Space.
- Booked or past time slots ignore clicks and show faded strikethrough; they are not focusable.
- Name: text input, label "Name", refused message "Enter your name (up to 80 characters)."
- Phone: telephone input, label "Phone", refused message "Enter a phone number with 7 to 15 digits."
- Email: email input, label "Email", refused message "Enter an email address like name@example.com."
- Validation runs when a field is left; focus shows dusty-rose outline, invalid shows red outline and message below.
- Submit while sending is ignored; button reads "Sending…" and is disabled.
- Taken slot: refuse, show error banner, refresh the time grid, clear the selected time.

### 4. Human Copy & Action Labeling
Seen:
- "Salon booking" — header title, top band.
- "Book your appointment" — header line.
- "1 Service", "2 Day", "3 Time", "4 Your details" — step headings.
- "Loading services…", "Loading times…" — loading states.
- "No services are offered yet." — empty services.
- "No times left on this day." — empty day.
- "Choose a service first.", "Choose a day first.", "Choose a time first." — prerequisite lines.
- "Name", "Phone", "Email" — field labels.
- Refusal messages as in section 3.
- "Services could not be loaded. Try again.", "Times could not be loaded. Try again." — load errors, with "Try again" button.
- "Slot just taken. Please choose another time." — error banner after refused booking.
- "Sending failed. Please try again." — error banner after send failure.
- Summary line: "{service name}, {date}, {start time} to {end time}" — shown after time chosen.
- "Request booking" — primary button; "Sending…" while submitting.
- "Requested" — amber badge; "Confirmed" — green badge.
- "Your booking request has been sent. The salon will confirm it." — confirmation message.
- "Book another" — link on confirmation panel.

Spoken only:
- "Salon booking logo" not used; "Service option, {name}, {duration} minutes" for rows.
- "Day, {weekday} {date}, {free or fully booked}" for day buttons.
- "Time {start}, available" or "Time {start}, unavailable" for slots.
- "Step {n}, {state}" for step headings.
- "Check" icon on confirmation: "Booking requested".

### 5. Contextual Action Placement
- Service rows sit inside step 1; choosing one opens step 2 directly beneath.
- Day buttons sit in step 2's horizontal row; the free times grid sits directly beneath in step 3.
- Summary line and "Request booking" sit at the foot of the card, above the button and below the error banner.
- Error banner sits directly above the button.
- "Try again" sits inside the load-error message of its own step.
- "Book another" sits below the confirmation badge and details.

### 6. Visual Direction
- **Feel**: a calm, friendly salon appointment widget: warm, light, uncluttered, like a familiar booking form.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; accent dusty rose #C77D8E for selected states and the primary button, pressed #A9606F. Service outline #D9D2CB; hover fill #F3ECE6; selected fill #F8E6EA; muted step #9A9A9A; error red #C0392B; error fill pale red #FBE9E7; requested amber #E0A030; confirmed green #3E8E5A; disabled button light grey #E4E0DC.
- **Type**: sans for headings and body; step headings bold 18px; header title bold 28px; body 16px.
- **First screen**: header band at top, then the card with step 1 service rows open immediately; no introductory paragraph above the card beyond the header line.
- **Form of the main view**: one card of 640px maximum, full width on phones; stacked numbered steps; service rows and time buttons sized to content; day buttons fixed 64px wide by 72px tall in a horizontal row that scrolls on narrow screens; time slot buttons fixed 88px by 40px in a grid that wraps; on screens narrower than the card, the grid reflows to fewer columns.
- **Shape and rhythm**: corner radius 8px on cards, buttons and fields; 1px borders; soft shadow 0 4px 16px rgba(43,43,43,0.08) on the card; 32px between steps; 16px inner padding; page margins 24px, 16px on phones; moderately dense.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans