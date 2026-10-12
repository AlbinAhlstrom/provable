### 1. Default Landing & Cold-Start Behavior
- On arrival the single booking view is active: the Header, then the Content card with step 1 "Service" live and steps 2–4 muted.
- Step 1 lists one Service option row per record, showing `Service.name` on the left and `Service.duration_minutes` on the right as "45 min".
- While services load, step 1 shows three 56px skeleton rows in #EFE8E2, with no text.
- If no services exist, step 1 shows one line: "No services are listed right now."
- If the service load fails, step 1 shows "Services couldn't load." with a "Try again" text button beside it.
- Step 2 Day picker shows the next 14 days once a service is chosen. Each day button shows its weekday and date from `TimeSlot.slot_date`.
- A day with no free times appears faded and is unclickable. No extra text is added.
- While times load, step 3 shows eight 40px skeleton slots in #EFE8E2.
- If the time load fails, step 3 shows "Times couldn't load." with a "Try again" text button beside it.
- A chosen day with no slots shows the Empty times message "No times left on this day." in place of the grid.
- Time slot buttons show the start time from `TimeSlot.start_time`. The end time comes from `TimeSlot.end_time`, matched to the service.
- The Summary line is hidden and the Book button is disabled on first visit.

### 2. Primary Navigation & View Structure
- One view: "Book your appointment". It has no tabs and no navigation.
- After a successful submit, the Confirmation panel replaces the form inside the same Content card.
- "Book another" returns to the empty form at step 1. There are no other views and no staff screens.

### 3. Workflow Prerequisites & Form Ergonomics
- Each muted step heading carries one grey line (#9A9A9A, 14px) beneath it, saying what to do first.
- Under step 2 Day, before a service is chosen: "Choose a service first."
- Under step 3 Time, before a day is chosen: "Choose a day first."
- Step 4 Your details fields are always usable. There is no prerequisite, so they carry no hint.
- While the Book button is disabled, a line sits under it naming what is missing, e.g. "Still needed: time, phone."
- Missing items in that line are named in this order: service, day, time, name, phone, email.
- Changing the service clears the time, hides the Summary line, reloads slots, and keeps the chosen day if it still has times.
- A booked or past slot does nothing on click or keypress. It is faded with strikethrough and carries no message.
- A faded day does nothing on click or keypress.
- Name field: a text input with autocomplete "name" and maxlength 80, labelled "Name".
- Phone field: input type "tel" with autocomplete "tel", labelled "Phone".
- Email field: input type "email" with autocomplete "email", labelled "Email".
- Fields are validated when they are left. The message appears below the field in red #C0392B at 13px.
- A field's error clears as soon as its value becomes valid.
- While sending, the button reads "Sending…" and is disabled. Further presses are ignored.
- If the slot was taken, the Error banner appears, the time is cleared, the slot grid refreshes, and the details are kept.
- If sending fails, the Error banner appears and all choices and details are kept.

### 4. Human Copy & Action Labeling
**Seen**
- Header title: "Salon booking". Header line: "Book your appointment".
- Step headings: "1 Service", "2 Day", "3 Time", "4 Your details".
- Service option duration: "{`Service.duration_minutes`} min".
- Day button: "Tue" over "14 May".
- Time slot: "10:00".
- Step hints: "Choose a service first." and "Choose a day first."
- Empty times message: "No times left on this day."
- Load messages: "No services are listed right now.", "Services couldn't load.", "Times couldn't load.", plus the "Try again" button.
- Field labels: "Name", "Phone", "Email".
- Name error: "Please enter your name (up to 80 characters)."
- Phone error: "Enter a phone number with 7–15 digits."
- Email error: "Enter a valid email address."
- Summary line: "{`Service.name`} · Tue 14 May · 10:00–10:45".
- Book button: "Request booking", then "Sending…" while submitting.
- Missing line: "Still needed: {items}."
- Error banner, slot taken: "That time was just taken. Please choose another."
- Error banner, send failed: "Your booking couldn't be sent. Please try again."
- Confirmation panel heading: "Your booking". It shows the summary line, then name, phone and email.
- Badges: "Requested" (amber) and "Confirmed" (green).
- Confirmation link: "Book another".

**Spoken only**
- Green check: "Booking sent".
- Taken slot: "10:00, unavailable".
- Faded day: "Tue 14 May, no times".
- Service group: "Services". Day group: "Days". Time group: "Times".
- Skeletons: "Loading".

### 5. Contextual Action Placement
- Service selection sits on each Service option row in step 1.
- Day selection sits on the Day picker in step 2. Time selection sits on the time grid in step 3.
- Each "Try again" sits beside the message of the step whose load failed.
- The Summary line, Error banner and Book button stack at the card's foot, in that order. The missing line sits under the button.
- "Book another" sits under the confirmation summary, centred.

### 6. Visual Direction
**Feel**: A simple appointment-booking widget. It is warm, calm and friendly, like a salon's front desk card.

**Palette**:
- Background #FAF6F2. Surface #FFFFFF. Text #2B2B2B. Accent dusty rose #C77D8E.
- Accent pressed #A9606F.
- Muted text #9A9A9A. Outlines #D9D2CB.
- Hover fill #F3ECE6. Selected fill #F8E6EA.
- Skeleton #EFE8E2.
- Disabled button #E4DEDA with #9A9A9A text.
- Error #C0392B on banner fill #FBEAE8.
- Requested badge #E0A030 with #2B2B2B text. Confirmed badge #3E8E5A with white text.
- Confirmation check #3E8E5A.

**Type**:
- Headings and body are both `font-sans`.
- The header title is 24px bold. Step headings are 18px bold. Body text is 16px. The summary line is 14px.

**First screen**:
- The white header band is 72px tall.
- Below it, the centred card opens straight on step 1, with its service rows ready.
- The muted steps follow underneath.

**Form of the main view**:
- A booking widget: one card, max 640px wide, with stacked numbered steps.
- Service rows run full width at 56px tall.
- Day buttons are 64×72px in a single horizontally scrolling row.
- Time slots are 80×40px in an auto-fill grid with 8px gaps.
- On phones the card goes full width with 20px padding. The day row scrolls sideways.

**Shape and rhythm**:
- Card radius is 12px, with shadow 0 4px 16px rgba(43,43,43,0.08) and 32px padding.
- Controls have an 8px radius and a 1px outline. The selected service row has a 2px outline.
- Steps are 32px apart and rows 8px apart. The density is airy.

LAYOUT columns=1 rows=auto
TOKENS background=#FAF6F2 surface=#FFFFFF text=#2B2B2B accent=#C77D8E on_accent=#FFFFFF heading=sans