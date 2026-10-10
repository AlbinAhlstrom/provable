### 1. Default Landing & Cold-Start Behavior
- Service records fill the step 1 "Service" option list, showing `Service.name` left and `Service.duration_minutes` right as "45 min".
- TimeSlot records fill the step 3 time grid, showing each open slot's `TimeSlot.start_time`, filtered to the chosen service and day.
- Services loading: step 1 shows "Loading services…" in muted grey text.
- No services: step 1 shows "No services are offered at the moment." and no option rows.
- Services failed to load: step 1 shows "Services could not be loaded." with a "Try again" button beside it.
- First visit opens on step 1 with services listed; steps 2 to 4 are muted, the book button is disabled, no days appear.
- Day picker opens on the next 14 days starting today, each showing weekday and date.
- No free days in the 14 days: step 2 shows "No free days in the next 14 days."
- Times loading: step 3 shows "Loading times…" in muted grey text.
- Times failed to load: step 3 shows "Times could not be loaded." with a "Try again" button beside it.
- Booking records are not shown to the client; the confirmation panel shows only the one just created.

### 2. Primary Navigation & View Structure
- One view only: the booking page, with a header band above a single centred content card.
- Steps 1 to 4 stack vertically inside the card in fixed order; no tabs, no menu, no back navigation.
- Completed steps stay open and visible so the client can change an earlier choice.
- Changing an earlier step (service, day) updates the later steps in place without leaving the page.
- The confirmation panel replaces the card's form content inside the same card; it is a state, not a new page.
- "Book another" returns the same card to step 1 with all selections cleared.

### 3. Workflow Prerequisites & Form Ergonomics
- Step 2 heading is muted until a service is chosen; no day buttons appear before then.
- Under muted step 2 heading, one line reads "Choose a service first." Step 3 heading reads "Choose a day first."; step 4 reads "Choose a time first."
- Muted steps are not clickable and do not respond to Tab focus.
- Choosing a service opens step 2 and marks step 1 complete with a check mark beside its heading.
- A day with no free times for the chosen service is faded and unclickable.
- A changed service clears the chosen time and recalculates the slot grid for the new service.
- The book button stays disabled until service, slot, name, phone and email are all valid.
- Beside the disabled book button, grey text lists what is missing, for example "Still needed: a time, your phone number."
- Name field: text input, label "Name", refused with "Enter your name, up to 80 characters."
- Phone field: telephone input, label "Phone", refused with "Enter a phone number of 7 to 15 digits."
- Email field: email input, label "Email", refused with "Enter an email address like name@example.com."
- Each field is validated when left, not while typing.
- A refused field shows its red outline and message below it; the message clears once the value is valid.

### 4. Human Copy & Action Labeling
**Seen:**
- Header title: "Hair Salon Booking", with the line "Book your appointment" beneath it.
- Step headings: "1 Service", "2 Day", "3 Time", "4 Your details".
- Muted-step guidance: "Choose a service first.", "Choose a day first.", "Choose a time first."
- Duration on each service row: "45 min" from `Service.duration_minutes`.
- Empty times message, in the time grid's place: "No times left on this day."
- Summary line above the button: "{Service.name} on {day and date}, {start} to {end}."
- Field labels: "Name", "Phone", "Email".
- Field messages: "Enter your name, up to 80 characters." / "Enter a phone number of 7 to 15 digits." / "Enter an email address like name@example.com."
- Missing-items line beside disabled button: "Still needed: {list of missing items}."
- Primary button: "Request booking"; while sending: "Sending…".
- Error banner, slot taken: "That time was just taken. Please choose another."
- Error banner, sending failed: "We could not send your request. Please try again."
- Confirmation heading: "Booking requested".
- Confirmation status badge: "Requested" in amber; "Confirmed" in green when staff confirm.
- Confirmation line: "The salon will confirm your appointment."
- Link under confirmation: "Book another".
- Load-failure buttons: "Try again".

**Spoken only:**
- Each service row: "Select {Service.name}, {duration} minutes".
- Each day button: "{weekday} {date}, {free time count} free" or "{weekday} {date}, no free times".
- Each time slot: "{start time}, available" or "{start time}, unavailable".
- Completed step marker: "Step complete".
- Loading indicator: "Loading".
- Confirmation check icon: "Booking requested".

### 5. Contextual Action Placement
- Service rows sit inside step 1, each row itself the action; no separate choose button.
- Day buttons sit in the step 2 row directly under the service choice they depend on.
- Time slots sit in step 3's grid directly under the chosen day.
- Summary line sits directly above the book button, visible only once a time is chosen.
- Error banner sits directly above the book button, inside the card.
- "Request booking" sits at the foot of the card, full width, the only primary action.
- "Try again" sits beside the load-failure message in the step it belongs to.
- "Book another" sits under the confirmation panel, inside the card.
- Field messages sit directly below their own field.

### 6. Visual Direction
- **Feel**: a calm, friendly appointment-booking widget, like a simple salon booking card on a warm white page.
- **Palette**: page background #FAF6F2; card surface #FFFFFF; text #2B2B2B; accent dusty rose #C77D8E; pressed rose #A9606F; hover fill #F3ECE6; selected fill #F8E6EA; outline #D9D2CB; muted grey #9A9A9A; disabled button #E5E5E5; error red #C0392B; error banner fill #FBE9E7; amber badge #E0A030; green badge #3E8E5A.
- **Type**: `font-sans` for headings and body; header title and step headings bold; largest text on the first screen is the header title at 24px, bold.
- **First screen**: a flat white header band with the title and line, then the card's step 1 with service rows visible; no hero, no photographs, nothing above the booking controls.
- **Form of the main view**: one stacked single-column card, not a calendar; service rows span the full card width at 56px tall; day buttons 64px wide by 64px tall in one horizontal row; time slots 96px wide by 40px tall in a wrapping grid; on phones the day row scrolls sideways and the time grid drops to 3 columns. Repeated parts are fixed in size, not stretched to content.
- **Shape and rhythm**: card and buttons corner radius 12px, service rows and fields 8px; card shadow `0 4px 16px rgba(43,43,43,0.08)`; 32px between steps, 12px between rows; medium density; card maximum width 640px.
LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans