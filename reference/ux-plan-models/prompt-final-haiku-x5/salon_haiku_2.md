### 1. Default Landing & Cold-Start Behavior
- On arrival the page opens on the booking form at step 1 "Service", with the header and "Book your appointment" visible.
- Services load from Service records; while loading, the service list shows three grey placeholder rows with the text "Loading services…".
- If no Service records exist, the list shows "No services are offered yet." in grey.
- If the Service load fails, the list shows "Services could not be loaded. Try again." with a "Try again" button.
- Steps 2 to 4 are visible but muted and unclickable until a service is chosen.
- Before a service is chosen, the day step shows the line "Choose a service first." beside its muted heading.
- Day buttons come from TimeSlot records for the chosen service; while loading, day buttons show as grey placeholders.
- A day with no free times is faded and unclickable; if no day in the next 14 days has free times, the day row shows "No free days in the next two weeks."
- Time slots load per chosen day; while loading, the grid shows six grey placeholder buttons.
- A day with no slots shows "No times left on this day." in place of the grid.
- If slot loading fails, the time step shows "Times could not be loaded. Try again." with a "Try again" button.
- The Summary line stays hidden until a time is chosen.
- The Booking entity holds no records on arrival; the confirmation panel appears only after submit.

### 2. Primary Navigation & View Structure
- One view only: the booking page, with a single card holding steps 1 to 4 in order, and the confirmation panel replacing the card after submit.
- No tabs, menus or back navigation; the page is one scrolling column.
- Step headings are "1 Service", "2 Day", "3 Time", "4 Your details".
- Choosing an earlier step's option again reopens that step and clears dependent later selections.
- The confirmation panel has one exit: the "Book another" link, which returns to step 1.
- Mobile: the card fills the width, the day row scrolls sideways, and the time grid uses four columns.

### 3. Workflow Prerequisites & Form Ergonomics
- Steps 2 to 4 are shown muted with the line "Choose a service first." before service is chosen, and are not clickable.
- Day step is muted with "Choose a day first." until a day is needed; time step muted with "Choose a time first." until a day is chosen.
- Details fields are shown muted until a time is chosen, with the line "Choose a time first."
- The "Request booking" button is disabled light grey; beside it, the summary line names what is missing, such as "Add your name, phone and email to continue."
- Changing the service clears the chosen time and recalculates slots; the summary is hidden again.
- Clicking a booked or past slot does nothing; the selection does not change.
- Clicking a faded day does nothing.
- Name field: text input, label "Name", refused with "Enter your name (up to 80 characters)."
- Phone field: telephone input, label "Phone", refused with "Enter a phone number of 7 to 15 digits."
- Email field: email input, label "Email", refused with "Enter an email address, such as name@example.com."
- Fields validate on leaving; invalid fields show a red outline and their message below.
- Focused fields show a dusty-rose outline.
- Slot-taken refusal: the error banner shows "That time was just taken. Choose another time." and the slot list refreshes.
- Double submit: the button shows "Sending…" and is disabled; further clicks do nothing.
- A booking refused for any other reason shows "Your request could not be sent. Try again."

### 4. Human Copy & Action Labeling
**Seen:**
- "Book your appointment" — header, under the salon title.
- "Step headings: "1 Service", "2 Day", "3 Time", "4 Your details"" — step headings.
- "Choose a service first." / "Choose a day first." / "Choose a time first." — muted step hints.
- "Loading services…", "No services are offered yet.", "Services could not be loaded. Try again." — service list states.
- "Try again" — retry button on load failure.
- "No free days in the next two weeks." — day row empty state.
- "No times left on this day." — time grid empty state.
- "Times could not be loaded. Try again." — time load failure.
- "Name", "Phone", "Email" — field labels.
- Field refusal messages as in section 3.
- "Summary line: "[Service.name], [day], [start time] to [end time]"" — shown above the button once a time is chosen.
- "Add your name, phone and email to continue." — missing-field hint beside the disabled button.
- "Request booking" — primary button; "Sending…" while sending.
- "That time was just taken. Choose another time." — slot-taken banner.
- "Your request could not be sent. Try again." — generic failure banner.
- "Request received" — confirmation heading.
- "Requested" — amber badge; "Confirmed" — green badge.
- "Book another" — link after confirmation.

**Spoken only:**
- Service rows: "[name], [duration] minutes, selected or not selected".
- Day buttons: "[weekday] [date], free times available" or "no free times".
- Time slots: "[start time], available" or "booked" or "passed".
- Check icon on confirmation: "Booking requested".
- Loading placeholders: "Loading".

### 5. Contextual Action Placement
- Service rows sit in the service step; selecting one opens step 2 beneath.
- Day buttons sit in the day step, directly under the service step.
- Time slots sit in the time step, under the day row.
- The summary line and "Request booking" button sit together at the foot of the card, below step 4.
- The error banner sits directly above the "Request booking" button.
- The "Try again" buttons sit beside their failed list.
- "Book another" sits below the confirmation summary, inside the confirmation panel.
- No edit or cancel control appears on the confirmation panel.

### 6. Visual Direction
- **Feel**: a calm, warm appointment widget, like a salon's printed booking card, soft and personal.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; secondary text #9A9A9A; accent dusty rose #C77D8E; accent pressed #A9606F; pale rose fill #F8E6EA; hover fill #F3ECE6; outline #D9D2CB; error red #C0392B; error banner fill #FBE9E7; requested amber #E0A030; confirmed green #3E8E5A; disabled light grey #E5E5E5; struck-through faded slot #B5B5B5.
- **Type**: `font-sans` for headings and body; page title 28px bold; step headings 18px bold; body 16px regular; the largest text on the first screen is the 28px title in charcoal, semibold weight 700.
- **First screen**: a white header band with the title "Salon booking" in charcoal and "Book your appointment" beneath, then the card opening directly on step 1 with the service rows visible. No photographs; the card is the first content.
- **Form of the main view**: a single stacked booking card, one object of 640px maximum width, with the four numbered steps as sections divided by 1px #D9D2CB lines. Service rows are full-width, 56px tall; day buttons are 64px wide by 64px tall in a horizontal row that scrolls on narrow screens; time slot buttons are 88px wide by 40px tall, in a grid that wraps. Repeated parts are fixed size, not stretched to content. On a narrow screen the card fills the width with 16px side margins and the time grid drops to four columns.
- **Shape and rhythm**: 8px corner radius on cards, buttons and rows; soft shadow `0 4px 16px rgba(43,43,43,0.08)` on the card; 32px between steps; 24px inside the card padding; medium density.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans