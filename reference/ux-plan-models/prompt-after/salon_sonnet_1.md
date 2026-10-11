### 1. Default Landing & Cold-Start Behavior
- Arrival shows the single booking view: header band, then the content card with step 1 "Service" open and steps 2–4 muted.
- Nothing is written above the form except the header title and the line "Book your appointment".
- Service rows are filled by `Service.name` (left) and `Service.duration_minutes` (right, "45 min"), one row per record.
- While services load: three grey placeholder rows in the step 1 area, outlined #D9D2CB, with no text.
- Services empty: one line in step 1, "No services are available right now."
- Services load failed: one line in step 1, "Services could not be loaded.", with a "Try again" button beside it.
- Day row shows no days before a service is chosen; steps 2–4 stay muted with their one-line prompts (see section 3).
- Day buttons come from `TimeSlot.slot_date`; while slots load, a row of grey placeholder day buttons, no text.
- Day with no free times: faded, unclickable day button. No days at all: "No days are open for booking right now."
- Slots load failed: "Times could not be loaded." with a "Try again" button beside it.
- Chosen day without free slots: "No times left on this day." replaces the grid.
- Summary line, error banner and confirmation panel are absent on arrival.

### 2. Primary Navigation & View Structure
- One view only: the booking form, with four stacked numbered steps; no tabs, menu or navigation.
- After submit, the confirmation panel replaces the form within the same card; "Book another" returns to step 1.
- No staff, account or management screens exist.

### 3. Workflow Prerequisites & Form Ergonomics
- Step 2 muted until a service is chosen, carrying the line "Choose a service first." Day buttons are not shown until then.
- Step 3 muted until a day is chosen, carrying the line "Choose a day first." Step 4 muted until a time is chosen, carrying "Choose a time first."
- Muted steps are grey #9A9A9A and unclickable; their fields are disabled.
- Book button disabled until service, slot, name, phone and email are valid; beside it a small grey line lists what is missing, e.g. "Still needed: time, phone."
- Changing service clears the chosen time and day-time slots are recalculated; the summary hides again.
- Booked, past or faded slots and days simply ignore clicks, with no message.
- Double press on "Request booking" while sending does nothing.
- Name: text input, label "Name", autocomplete name, max 80 characters. Refused: "Please enter your name (80 characters at most)."
- Phone: tel input, label "Phone", autocomplete tel. Refused: "Enter a phone number with 7 to 15 digits."
- Email: email input, label "Email", autocomplete email. Refused: "Enter a valid email address."
- Fields validate on leaving; invalid shows red #C0392B outline and message below; focus shows a dusty-rose outline.
- Slot taken meanwhile: error banner "That time was just taken. Please choose another." and the slot list refreshes, with the chosen time cleared.
- Send failure: error banner "Your request could not be sent. Please try again."
- Services, days and slots are focusable and operated with Enter or Space; the selected one carries aria-pressed.

### 4. Human Copy & Action Labeling
- **Seen**
- Header title: "Salon Booking". Header line: "Book your appointment".
- Step headings: "1 Service", "2 Day", "3 Time", "4 Your details".
- Service rows: `Service.name`, `Service.duration_minutes` + " min".
- Day buttons: weekday and date from `TimeSlot.slot_date`.
- Slot buttons: `TimeSlot.start_time`.
- Prompts: "Choose a service first.", "Choose a day first.", "Choose a time first."
- Empty and failed states: "No services are available right now.", "Services could not be loaded.", "No days are open for booking right now.", "Times could not be loaded.", "No times left on this day.", "Try again".
- Labels: "Name", "Phone", "Email", with the refusal messages from section 3.
- Summary line: `Service.name`, date, `TimeSlot.start_time` to `TimeSlot.end_time`, e.g. "Cut · Tue 12 Mar · 10:00 to 10:45".
- Missing line: "Still needed: …".
- Buttons: "Request booking", "Sending…", "Book another".
- Banners: "That time was just taken. Please choose another.", "Your request could not be sent. Please try again."
- Confirmation: heading "Booking requested", the summary, badge "Requested" (amber) or "Confirmed" (green).
- **Spoken only**
- Green check icon: "Success".
- Day and slot buttons: "Unavailable" added for faded ones.
- Loading placeholders: "Loading".
- Error banner: role alert.

### 5. Contextual Action Placement
- Selecting a service happens on its row in step 1; days and times on their buttons in steps 2 and 3.
- "Try again" sits beside the failed-load line in the step that failed.
- Contact fields sit in step 4, validated in place with the message below each.
- Summary, missing line, error banner and "Request booking" sit together at the foot of the card, in that order.
- "Book another" sits as a link below the confirmation panel.

### 6. Visual Direction
- **Feel**: a simple appointment-booking widget: stacked numbered steps on a warm white page, friendly and light, one rose button.
- **Palette**: page #FAF6F2; surface #FFFFFF; text charcoal #2B2B2B; muted #9A9A9A; outline #D9D2CB; hover #F3ECE6; accent dusty rose #C77D8E; pale rose #F8E6EA; pressed #A9606F; error #C0392B with pale red banner #FBE9E7; amber #E0A030; green #3E8E5A; disabled button #D9D2CB with text #FFFFFF.
- **Type**: font-sans throughout; the title is 28px bold, step headings 18px bold, body 16px, summary 14px.
- **First screen**: white header band, then a centred card (max 640px) with step 1 service rows open and steps 2–4 muted below; button at the foot.
- **Form of the main view**: a single-column stepped form. Service rows are full width and 56px tall; day buttons 72×64px in a horizontal scrolling row; slot buttons 88×44px in a wrapping grid. On phones the card is full width.
- **Shape and rhythm**: 12px card radius with a soft shadow (0 4px 20px rgba(43,43,43,.08)); 8px radius on controls; 1px outlines; 32px between steps; relaxed density.

LAYOUT columns=1 rows=auto

TOKENS background=#FAF6F2 surface=#FFFFFF text=#2B2B2B accent=#C77D8E on_accent=#FFFFFF heading=sans