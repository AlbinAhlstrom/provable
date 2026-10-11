### 1. Default Landing & Cold-Start Behavior

- Page opens on the booking form at step 1, Service, with the header "Book your appointment" above it. No view is pre-selected.
- Service records fill the step 1 option rows, showing `Service.name` left and `Service.duration_minutes` as "45 min" right.
- While Service records load, step 1 shows "Loading services…" in place of the rows.
- If no Service records exist, step 1 shows "No services are offered yet." Nothing else is offered.
- If Service records fail to load, step 1 shows "Services could not be loaded. Try again." with a "Try again" button.
- TimeSlot records fill the step 3 time grid, each showing `TimeSlot.start_time` on the button, with `TimeSlot.is_booked` deciding its state.
- While TimeSlot records load for a chosen day, step 3 shows "Loading times…" in place of the grid.
- If a load of TimeSlot records fails, step 3 shows "Times could not be loaded. Try again." with a "Try again" button.
- Steps 2, 3 and 4 are muted and show no days, times or fields until the step before is complete.
- Step 2 Day shows the line "Choose a service first." while muted; step 3 and 4 show nothing extra until reached.
- A day with no free times for the chosen service is faded and unclickable; the time step is not opened by it.
- A day with no free times, once chosen, shows "No times left on this day." in place of the grid.
- Day buttons cover the next 14 days from today, starting with today; past days are never shown.

### 2. Primary Navigation & View Structure

- The product is one view: a single booking page with one flow of four numbered steps.
- Step order is fixed: 1 Service, 2 Day, 3 Time, 4 Your details, then the Request booking button.
- The confirmation panel replaces the whole form in the same view after a successful submit.
- There is no menu, tab bar, back navigation or second page.
- Steps open forward only as each is completed; a change to an earlier step clears the later steps it affects.
- Changing Service clears the chosen Time and recalculates slots; Day stays if it still has free times for the new service.
- "Book another" returns to step 1 within the same page.
- Narrow screens: the card goes full width with 16px side margins; the time grid drops from 4 columns to 3.

### 3. Workflow Prerequisites & Form Ergonomics

- Days appear only after a Service is selected; before that, step 2 is muted with "Choose a service first." beside it.
- Time grid appears only after a Day is selected; before that, step 3 is muted with "Choose a day first." beside it.
- Details fields appear only after a Time is selected; before that, step 4 is muted with "Choose a time first." beside it.
- The Request booking button is shown always, disabled until valid, with "Still needed: " and the missing items listed beside it.
- Missing items are named in form order: service, day, time, name, phone, email.
- Name is a text input, labelled "Name", required, refused with "Enter your name, up to 80 characters." when empty or too long.
- Phone is a phone input, labelled "Phone", refused with "Enter a phone number of 7 to 15 digits." when out of range or invalid.
- Email is an email input, labelled "Email", refused with "Enter an email address, such as name@example.com." when it does not look like an address.
- Field validation runs when the field is left; a refused field shows its red outline and message below it.
- Focused fields show the dusty-rose outline; the message clears as soon as the value becomes valid.
- A chosen option cannot be chosen again; a taken or past time is never clickable, so no refusal message is needed for it.
- If a slot is taken between display and submit, the error banner shows and the time grid refreshes with the slot marked taken.
- While sending, the button is disabled and extra clicks are ignored; no second booking is created.
- If sending fails, the error banner shows "We could not send your request. Try again." and the form keeps all entries.

### 4. Human Copy & Action Labeling

- Seen: "Book your appointment" — header line under the salon booking title "Salon booking".
- Seen: "Service", "Day", "Time", "Your details" — step headings, numbered 1 to 4.
- Seen: "Choose a service first." / "Choose a day first." / "Choose a time first." — muted step lines.
- Seen: "Loading services…", "Loading times…" — loading states.
- Seen: "No services are offered yet." / "No times left on this day." — empty states.
- Seen: "Services could not be loaded. Try again." / "Times could not be loaded. Try again." — load failure messages.
- Seen: "Try again" — button on load failure.
- Seen: "Name", "Phone", "Email" — field labels.
- Seen: "Enter your name, up to 80 characters." / "Enter a phone number of 7 to 15 digits." / "Enter an email address, such as name@example.com." — refusal messages.
- Seen: "Still needed: " followed by the missing items — beside the disabled button.
- Seen: "Request booking" — primary button; "Sending…" while submitting.
- Seen: "This time was just taken. Choose another time." — error banner when the slot is taken.
- Seen: "We could not send your request. Try again." — error banner on sending failure.
- Seen: "Your booking is requested." — confirmation heading, status shown by the amber "Requested" badge.
- Seen: "Requested" / "Confirmed" — status badges.
- Seen: "Book another" — link resetting to step 1.
- Seen: summary line "Service · Day date · Start time–End time" with service name, date, time and end time.
- Spoken only: "Service option, 45 minutes" — name read for each service row.
- Spoken only: "Open time, 10:00" / "Booked time, 10:00" / "Unavailable day, Monday 3" — names for day and time buttons.
- Spoken only: "Clear" / "Green check" — names for the confirmation icon and status marks.

### 5. Contextual Action Placement

- Service rows sit inside step 1; selecting one opens step 2 directly beneath it.
- Day buttons sit inside step 2 directly beneath the service choice they depend on.
- Time slots sit inside step 3 directly beneath the chosen day.
- The summary line sits directly above the Request booking button, shown only once a time is chosen.
- The error banner sits directly above the Request booking button.
- The Request booking button sits at the foot of the card, full width, under the Your details fields.
- The "Try again" control for a failed load sits inside the same step that failed.
- "Book another" sits below the confirmation panel, as a link.
- There are no actions in the header; it carries only the title and the line beneath.

### 6. Visual Direction

- **Feel**: a simple, warm appointment-booking widget, like a salon's own calm booking card: light, soft and easy to finish.
- **Palette**: page background flat #FAF6F2; surface #FFFFFF; text charcoal #2B2B2B; accent dusty rose #C77D8E for selection and the primary button. Hover #F3ECE6; selected fill #F8E6EA; outline grey #D9D2CB; muted text #9A9A9A; pressed rose #A9606F; disabled button light grey #E4E0DC; error red #C0392B with banner fill #FBE3E0; amber "Requested" #E0A030; green "Confirmed" and check #3E8E5A.
- **Type**: sans family throughout. Largest text is the header title, 28px bold charcoal; step headings 18px bold; body 16px regular.
- **First screen**: header band with title and line, then the card opening directly on step 1 with the service rows listed. No photographs, no introduction block; the rows are the first thing read.
- **Form of the main view**: a single stacked form inside one card, read top to bottom in numbered steps. Service rows are full-width rows, 56px tall, with 8px gap. Day buttons are 64px wide by 64px tall in a horizontal row that scrolls sideways on narrow screens. Time buttons are 44px tall in a grid of 4 columns of equal width, 8px gap. Empty parts hold only their message line. On narrow screens the card fills the width and the time grid drops to 3 columns.
- **Shape and rhythm**: card corner radius 12px, soft shadow (0 4px 16px rgba(43,43,43,0.08)); buttons and options radius 8px; 1px outlines; 24px between steps; 16px inside the card padding of 24px. Dense enough to fit the four steps and the button without scrolling on a laptop.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans