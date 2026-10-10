### 1. Default Landing & Cold-Start Behavior
- On arrival the page opens on the booking form at step 1 "Service", with the service list visible and no selection.
- Steps 2 "Day" and 3 "Time" are muted and unclickable; no days appear until a service is chosen.
- Service list shows `Service.name` and `Service.duration_minutes` as "45 min" while loading, showing a single line "Loading services…" in grey.
- Service list when no services exist: "No services are offered at the moment." with no form controls below it.
- Service list when load fails: "Services could not be loaded." with a "Try again" text button beneath.
- Day step shows the next 7 days from today as day buttons once a service is chosen; days with no free times are faded and unclickable.
- Day row while loading slots: five grey placeholder buttons, no text.
- Time step when the chosen day has no free slots: grid replaced by "No times left on this day."
- Time step when slot load fails: "Times could not be loaded." with "Try again" beneath.
- Confirmation panel is never shown on arrival; it appears only after a successful submit.

### 2. Primary Navigation & View Structure
- One view only: the single booking page with a header and one content card.
- The card holds four stacked steps in order: Service, Day, Time, Your details.
- No tabs, menus, or links to other areas; the only secondary link is "Book another" on the confirmation panel.
- Confirmation panel replaces the card contents rather than opening a new page.
- Page title in the header: "Book your appointment" beneath the salon booking title.

### 3. Workflow Prerequisites & Form Ergonomics
- Steps 2–4 are shown muted with the line "Choose a service first." beside the step 2 heading only; steps 3–4 carry no extra line.
- Step 3 stays muted until a day is chosen; it shows "Choose a day first." beside its heading while muted.
- Step 4 fields are shown muted until a time is chosen, with "Choose a time first." beside its heading.
- Changing the service clears the chosen time and recalculates the slots without clearing the day.
- Slots are offered only when `S + duration ≤ closing`, not overlapping a booked slot, and not in the past.
- "Request booking" is disabled until service, slot, name, phone and email are all valid; beside it, the line "Still needed: " followed by the missing items, e.g. "Still needed: time, phone".
- Name input: text input, label "Name", refused with "Enter your name (up to 80 characters)." when empty or too long.
- Phone input: telephone input, label "Phone", refused with "Enter a phone number of 7 to 15 digits."
- Email input: email input, label "Email", refused with "Enter an email address like name@example.com."
- Validation runs when a field is left; focus shows dusty-rose outline, invalid shows red outline with the message below.
- Double submit: button turns to "Sending…" and ignores further clicks until the response returns.
- Slot taken at submit: no booking created, error banner shown, slot grid refreshed, chosen time cleared.
- Sending failure: error banner shows "Your booking could not be sent. Please try again."; entered details are kept.

### 4. Human Copy & Action Labeling
- Seen: "Book your appointment" (header subtitle); "Service", "Day", "Time", "Your details" (step headings).
- Seen: "45 min" (duration format on each service row).
- Seen: "Choose a service first." / "Choose a day first." / "Choose a time first." (muted step guidance).
- Seen: "No times left on this day." (empty day message).
- Seen: "Loading services…", "Services could not be loaded.", "Try again" (load states).
- Seen: "No services are offered at the moment." (empty services).
- Seen: summary line "[Service.name], [day and date], [start time] to [end time]" shown only after a time is chosen.
- Seen: "Request booking" (primary button); "Sending…" (while sending); "Still needed: …" (disabled reason).
- Seen: error banner "Your booking could not be sent. Please try again." and "That time was just taken. Please choose another time."
- Seen: confirmation heading "Request received"; badge "Requested"; labels "Service", "Day", "Time", "Name"; "Book another" link.
- Seen: field labels "Name", "Phone", "Email"; messages as in section 3.
- Spoken only: "Previous" none; "Service option, 45 minutes" for each row; "Day, [date], free times" per day; "Time, [start] to [end]" per slot; "Booked, unavailable" for faded slots; "Step complete" / "Step locked" on step headings.
- Action names match everywhere: "Request booking" on the button and in the error banner's retry context.

### 5. Contextual Action Placement
- Service rows are the action for step 1; selecting one reveals step 2 directly beneath.
- Day buttons sit in step 2 and reveal the time grid in step 3 below them.
- Time slots sit in step 3; the summary line sits directly above the button in step 4.
- "Request booking" sits at the foot of the card, full width, with the "Still needed" line and error banner directly above it.
- "Book another" sits beneath the confirmation panel, the only action on that panel.
- "Try again" sits beside the failed list it reloads, not in the header.

### 6. Visual Direction
- **Feel**: a calm, friendly appointment widget, like a salon's own booking card: warm, light, unhurried.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; muted text #9A9A9A; accent dusty rose #C77D8E; accent pressed #A9606F; rose fill #F8E6EA; hover fill #F3ECE6; outline #D9D2CB; error red #C0392B; error fill pale red #FBE9E7; requested amber #E0A030; confirmed green #3E8E5A; disabled light grey #E5E5E5.
- **Type**: `font-sans` for headings and body; step headings bold at 18px; header title bold at 24px; body 16px.
- **First screen**: header band with title and subtitle, then the card opening directly on the numbered steps with Service active. No hero, no photographs; the page is used, not read.
- **Form of the main view**: a single stacked booking card, 640px maximum width, forming one unit with its four steps in order. Service rows are full width at 56px height; day buttons are fixed 64px wide by 64px tall in a horizontal row that scrolls on narrow screens; time slots are fixed 88px by 40px in a grid that wraps. On a narrow screen the card becomes full width with 16px side margins and day buttons scroll sideways.
- **Shape and rhythm**: 8px corner radius on rows, buttons and fields; soft shadow `0 4px 16px rgba(43,43,43,0.08)` on the card; 32px between steps, 24px card padding; medium density.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans