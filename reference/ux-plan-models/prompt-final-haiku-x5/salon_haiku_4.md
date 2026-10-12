### 1. Default Landing & Cold-Start Behavior
- On arrival the page shows the booking card with step 1 "Service" active; no service is selected, so steps 2 to 4 are muted and unclickable.
- The service list is the `Service` records: each row shows `Service.name` left and `Service.duration_minutes` as "45 min" right.
- While `Service` records load, show three grey placeholder rows of equal height, not a spinner.
- When there are no `Service` records, show "No services are available to book right now." in grey text where the list would sit.
- When `Service` records fail to load, show "We couldn't load the services. Try again." with a "Try again" text button that reloads them.
- Days are hidden until a service is chosen; no day buttons are drawn before then.
- Day buttons are generated from today onward for the next 14 days, so the day row never opens empty.
- A day with no free times for the chosen service is faded and unclickable.
- Time slots are the `TimeSlot` records for the chosen service and day, filtered by the rules; while loading, show a row of six grey placeholder buttons.
- When a chosen day has no open slots, the grid is replaced by "No times left on this day."
- When `TimeSlot` records fail to load, show "We couldn't load times. Try again." with a "Try again" text button.
- The header always reads "Book your appointment" beneath the salon title; no intro paragraph precedes the form.
- Confirmation panel is never shown on arrival.

### 2. Primary Navigation & View Structure
- One view only: the booking page, with no tabs, menu or navigation bar.
- Steps are in order: "Service", "Day", "Time", "Your details", shown as numbered sections within the single card.
- Each step opens when its prerequisite is complete; completed steps remain visible and can be reopened by clicking them.
- Changing the service after a time is chosen clears the time and recalculates the slots.
- Confirmation replaces the form inside the same card; "Book another" returns to step 1.
- No staff, account, payment or management surfaces exist.

### 3. Workflow Prerequisites & Form Ergonomics
- Steps 2 to 4 are shown muted with the line "Choose a service first." beside the step heading.
- Muted steps are unclickable until the previous step is complete.
- The Time step, before a day is chosen, shows the line "Choose a day first."
- The "Request booking" button, while disabled, shows beside it the line "Still needed: " followed by the missing items, such as "a time, your name, phone and email".
- Only open slots accept clicks; booked or past slots are faded with strikethrough and ignore clicks.
- A day with no free times is faded and unclickable with no extra text.
- Name field: text input, label "Name", refused message "Enter your name (up to 80 characters)."
- Phone field: phone input, label "Phone", refused message "Enter a phone number with 7 to 15 digits."
- Email field: email input, label "Email", refused message "Enter an email address like name@example.com."
- Validation runs when a field is left; focus shows a dusty-rose outline, invalid shows a red outline.
- If the slot was taken during submission, the error banner appears and the time list refreshes, clearing the selected time.
- Double submit is ignored while sending; the button shows "Sending…" and is disabled.
- Confirmation shows status "Requested" in amber; a status set to confirmed shows "Confirmed" in green.
- No cancel or edit controls exist on any booking view.

### 4. Human Copy & Action Labeling
Seen:
- "Book your appointment" — header line, under the salon title.
- "Service", "Day", "Time", "Your details" — step headings, numbered 1 to 4.
- "min" appended to durations, e.g. "45 min".
- "Choose a service first." — muted Day step line.
- "Choose a day first." — muted Time step line.
- "No times left on this day." — empty slot grid.
- "No services are available to book right now." — empty service list.
- "We couldn't load the services. Try again." — service load error.
- "We couldn't load times. Try again." — slot load error.
- "Try again" — retry link on both load errors.
- "Name", "Phone", "Email" — field labels.
- "Enter your name (up to 80 characters)." — name refused message.
- "Enter a phone number with 7 to 15 digits." — phone refused message.
- "Enter an email address like name@example.com." — email refused message.
- Summary line: "{service} on {date} at {start time}, ends {end time}" — shown above the button once a time is chosen.
- "Still needed: {missing items}" — beside disabled button.
- "Request booking" — primary button.
- "Sending…" — button while sending.
- "That time was just taken. Please choose another time." — error banner for taken slot.
- "We couldn't send your booking. Please try again." — error banner for send failure.
- "Thank you. Your booking request has been sent." — confirmation heading.
- "Requested" — amber badge; "Confirmed" — green badge.
- "Book another" — link on confirmation panel.

Spoken only:
- "Salon booking" — region label for the card.
- "Service option, {name}, {duration} minutes" — each service row.
- "Day, {weekday} {date}" — each day button; "Day unavailable, no free times" for faded days.
- "Time {start time}" — each slot; "Time unavailable" for booked or past slots.
- "Error" — banner role label.
- "Check mark" — confirmation icon.

### 5. Contextual Action Placement
- Service rows sit inside step 1; selecting one reveals step 2 directly below.
- Day buttons sit in the horizontal row inside step 2.
- Time slots sit in the grid inside step 3, with the summary line directly above the button.
- "Request booking" sits at the foot of the card, full width, below the details fields.
- Error banner sits directly above "Request booking".
- "Book another" sits beneath the confirmation panel's summary, inside the card.
- "Try again" sits beside its load error message, inside the step it belongs to.

### 6. Visual Direction
- **Feel**: a calm, friendly appointment widget, like a salon's own booking card on a warm page.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; accent dusty rose #C77D8E; accent pressed #A9606F; rose fill #F8E6EA; hover fill #F3ECE6; outline grey #D9D2CB; muted grey #9A9A9A; error red #C0392B; error fill pale red #FBE9E7; amber #E0A030; green #3E8E5A; disabled light grey #E5E5E5.
- **Type**: `font-sans` for headings and body; salon title 24px semibold, step headings 16px bold, body 15px regular.
- **First screen**: the header band with the salon title and "Book your appointment", then the card with step 1 open at once, service rows visible without scrolling on desktop.
- **Form of the main view**: one card, one width, 640px maximum, full width on phones, containing the four numbered steps stacked in order. Service rows are full-width stacked rows, each 56px tall, equal size whatever they hold. Day buttons are 64px wide by 64px tall in a horizontal row that scrolls sideways on narrow screens. Time buttons are 88px wide by 40px tall in a grid that wraps to fewer columns on narrow screens.
- **Shape and rhythm**: corners 8px on card, rows and buttons; soft shadow `0 4px 16px rgba(43,43,43,0.08)` on the card only; 24px between steps; 12px between rows; dense enough to fit one screen of step 1 and 2.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans