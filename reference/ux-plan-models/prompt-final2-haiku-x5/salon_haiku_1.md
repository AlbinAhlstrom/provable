### 1. Default Landing & Cold-Start Behavior

- The page opens on the booking card with step 1, "Service", active and the header line "Book your appointment" above it.
- Steps 2 to 4 show muted grey and are unclickable, with no days or times visible yet.
- Under step 2's heading, one line reads "Choose a service to see days." Steps 3 and 4 need no line.
- Service list (`Service.name`, `Service.duration_minutes`) shows a "Loading services…" line while records load.
- Service list shows "No services are available right now." when no records exist.
- Service list shows "Services could not load." with a "Try again" button beside it when the load fails.
- Day row appears only after a service is selected; days are the next 14 dates from today.
- A day with no free times for the service (no `TimeSlot` with `is_booked` false) is faded and unclickable.
- Time grid (`TimeSlot.start_time`, `TimeSlot.is_booked`) shows "Loading times…" while records load.
- Time grid shows "Times could not load." with a "Try again" button beside it when the load fails.
- Time grid is replaced by "No times left on this day." when the chosen day has no offered slots.
- Details fields and the Request booking button appear at once, the button disabled until all is valid.

### 2. Primary Navigation & View Structure

- One view only: the booking page, with no tabs, menus or additional screens.
- Steps run top to bottom in one card: "Service", "Day", "Time", "Your details", numbered 1 to 4.
- A step is active when it is the next to complete; completed steps stay open and can be revisited.
- Changing the service after a time is chosen clears the time and recalculates slots.
- The confirmation panel replaces the whole form after a successful submit.
- "Book another" in the confirmation panel clears all selections and returns to step 1.
- On phones, the day row scrolls sideways; all other content stacks in one column.

### 3. Workflow Prerequisites & Form Ergonomics

- Day row is hidden until a service is chosen; the time step stays muted until a day is chosen.
- Time step is muted and unclickable until a day is chosen; no slots show before that.
- Selecting a service row opens step 2 at once; choosing another row switches the service.
- Taken or past slots stay visible faded with strikethrough and ignore clicks silently.
- Summary line stays hidden until a time is chosen, then shows service, date, time and end time.
- Request booking stays disabled until service, slot, name, phone and email are all valid.
- Name: text input, label "Name", max 80 characters, refused with "Enter your name (up to 80 characters)."
- Phone: telephone input, label "Phone", 7 to 15 digits; refused with "Enter a phone number with 7 to 15 digits."
- Email: email input, label "Email", refused with "Enter an email address, such as name@example.com."
- Fields validate on leaving; invalid fields show a red outline and their message below.
- A slot refused as taken shows the error banner and refreshes the time grid at once.
- Double submits are ignored while sending; the button shows "Sending…" and is disabled.

### 4. Human Copy & Action Labeling

- Seen: "Book your appointment" in the header, the salon booking title in charcoal above it.
- Seen: step headings "Service", "Day", "Time", "Your details".
- Seen: "Choose a service to see days." under step 2's heading, the only instruction in the flow.
- Seen: "Loading services…", "Loading times…", "Services could not load.", "Times could not load.", "Try again".
- Seen: "No services are available right now." in the empty service list.
- Seen: "No times left on this day." replacing the empty time grid.
- Seen: summary line "{Service.name}, {date}, {start time}–{end time}" above the button.
- Seen: field labels "Name", "Phone", "Email"; field messages as given in section 3.
- Seen: button "Request booking"; while sending "Sending…".
- Seen: error banner "We could not send your booking. Try again." or "That time was just taken. Choose another time."
- Seen: confirmation heading "Booking requested" with badge "Requested"; badge "Confirmed" when staff confirm.
- Seen: link "Book another".
- Spoken only: "Step 1 of 4" style labels on each numbered step; "Available" or "Unavailable" on day and slot buttons.
- Spoken only: "Selected" on the chosen service, day and time; "Service duration" on each duration.
- Spoken only: "Green check" icon on the confirmation panel reads as "Booking requested".

### 5. Contextual Action Placement

- Retry buttons sit beside the failed list or grid they reload, not at the foot of the page.
- Summary line sits directly above the error banner and the Request booking button.
- Error banner sits above the Request booking button, inside the details step.
- "Book another" sits under the confirmation panel's summary, where the form was.
- Field messages sit directly under their field.
- No action sits outside the card; the page has one primary button only.

### 6. Visual Direction

- **Feel**: a calm, friendly salon appointment widget, like a simple booking form from a neighbourhood hairdresser.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; accent dusty rose #C77D8E; button text #FFFFFF. Hover row #F3ECE6; selected row fill #F8E6EA; outline #D9D2CB; muted step and faded text #9A9A9A; pressed button #A9606F; disabled button #E5E0DA; error text and outline #C0392B; error banner fill #FBE9E7; "Requested" badge #E0A030; "Confirmed" badge #3E8E5A.
- **Type**: sans throughout (font-sans); headings semibold. Largest text on first screen is the header title at 28px, semibold.
- **First screen**: flat white header band with the title and line, then the white card opening at step 1 with the services list visible. No photographs, no introduction above the form.
- **Form of the main view**: one booking form in one card, 640px wide maximum, full width on phones. Service rows are full-width, 56px tall, 8px apart. Day buttons are 64px wide by 64px tall in one horizontal row. Time slots are a grid of 40px-tall buttons, 4 per row on desktop and 3 on phones. Empty parts hold their fixed size with the message in place. On narrow screens, the day row scrolls sideways and the time grid drops to 3 columns.
- **Shape and rhythm**: card radius 12px; rows, day and time buttons radius 8px; soft card shadow 0 2px 8px rgba(43,43,43,0.08); card padding 32px, 20px on phones; 32px between steps; medium-low density with a 1px #D9D2CB outline on fields and rows.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans