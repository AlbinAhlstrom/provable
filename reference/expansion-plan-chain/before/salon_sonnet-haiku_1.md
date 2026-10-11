### 1. Default Landing & Cold-Start Behavior

- The page opens on step 1 "Choose a service" with steps 2 to 4 visible but greyed, each with its own hint line.
- Nothing is pre-selected; the summary, day strip and time grid stay hidden until their step can be used.
- Service list (Service.name, Service.duration_minutes) loads into step 1 cards, showing a calm "Loading services…" line while waiting.
- Empty service list shows "No services are offered yet." in grey, with no card and no button.
- Failed service load shows "Services could not be loaded." with a "Try again" button that reloads the list.
- Day strip (TimeSlot.slot_date) shows 14 chips from today, rendered without waiting on the network.
- Day chips are greyed when TimeSlot records show the day closed or fully booked.
- Time grid (TimeSlot.start_time, TimeSlot.status) shows a "Loading times…" line while the chosen day's slots load.
- A day with no free slot for the service shows "No free times on this day." in grey, replacing the grid.
- Failed time load shows "Times could not be loaded." with a "Try again" button for that day.
- Booking entity has no pre-loaded records; the confirmation panel appears only after a successful submission.

### 2. Primary Navigation & View Structure

- One view only: a single booking page with four numbered steps stacked top to bottom.
- No menu, tabs or links to other pages; the page header carries the title and subtitle only.
- Step headings are the navigation; a completed step heading is a button that scrolls back to that step.
- Completed step headings show a plum tick beside their number badge.
- The confirmation panel replaces the step 4 form within the same page, with no separate route.
- "Book another" returns to step 1 on the same page, scrolled to the top of the column.

### 3. Workflow Prerequisites & Form Ergonomics

- Step 2 hint, shown while greyed: "Choose a service first."
- Step 3 hint, shown while greyed: "Choose a day first."
- Step 4 hint, shown while greyed: "Choose a time first."
- Day strip and time grid are disabled, not hidden, until their prerequisite step is complete.
- Changing the service clears the chosen time and shows the step 3 hint again until a time is picked.
- Name: text input, label "Name", max 80 characters, red message "Enter a name of up to 80 characters."
- Phone: telephone input, label "Phone", message "Enter a phone number of 7 to 15 digits."
- Email: email input, label "Email", message "Enter a valid email address."
- Each field validates on blur; a red outline and message appear below only after a blur or failed submit.
- Request booking is disabled until all selections and fields are valid; hint beside it: "Complete your details to request this booking."
- Taken or too-short slots are not pressable; a press does nothing and leaves the selection unchanged.
- Changing the service during a selected day keeps the day chosen and only reloads its times.

### 4. Human Copy & Action Labeling

- Page title "A booking page for a hair salon"; subtitle "Choose a service, a day and a time, then request your booking."
- Step headings: "Choose a service", "Choose a day", "Choose a time", "Your details".
- Summary labels: "Service", "Day", "Time", "Duration"; summary heading "Your booking".
- Primary button "Request booking"; while sending "Sending…"; retry button "Try again".
- Taken slot message: "That time was just taken. Please pick another time."
- Failure banner: "Your booking could not be sent. Please try again."
- Confirmation heading "Booking request received"; status pill "Requested" or "Confirmed".
- Confirmation secondary button "Book another"; no other actions appear on the panel.
- Empty day strip: "No free days in the next 14 days."

### 5. Contextual Action Placement

- Service "Try again" sits under the failed-load message inside step 1.
- Time "Try again" sits under the failed-load message inside step 3.
- Failure banner sits directly above the Request booking button, inside step 4.
- Booking summary sits directly above the Request booking button, inside step 4.
- Request booking sits at the foot of step 4, full width.
- "Book another" sits on the confirmation panel beneath the status pill, the only action there.
- Step heading scroll-back sits on the heading itself, the whole row tappable.

### 6. Visual Direction

- **Feel**: a warm, simple appointment scheduler; calm, light and friendly, like a salon's own booking sheet.
- **Palette**: page background #FAF6F1; surface white #FFFFFF; text charcoal #2B2B2B; secondary text grey #6B6B6B; accent plum #7A3E65 for selection, badges and the main button; plum pressed #5E2E4D; plum pale fill #F3E6EE; outline light grey #DDD3CA; disabled grey #CFC7C0 and greyed heading #B5ADA6; chip closed fill #EEE9E4; error red #B3261E; success green #2E7D4F; amber pending #C77D00.
- **Type**: sans throughout (font-sans); page title text-3xl semibold, about 30px; step headings text-lg semibold; body text-base, 16px.
- **First screen**: the page title and subtitle, then step 1 with its service cards visible at once, steps 2 to 4 greyed below; no photographs and no marketing copy.
- **Form of the main view**: a single vertical form column, 640px wide, of four stacked step sections separated by 32px; service cards are full-width rows, each 64px tall; day chips are 64px wide by 72px tall in a horizontal scroller; time buttons are full-width cells of 48px height in three columns with 8px gaps; when narrower than 640px the column fills the screen with 16px side padding and the grid stays three columns.
- **Shape and rhythm**: corners 8px on cards, chips, buttons and fields; 1px outlines, flat surfaces, shadow only on the confirmation panel (soft, about 0 4px 16px rgba(43,43,43,0.08)); section spacing 32px; page density comfortable, with 16px inside cards.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f1 surface=#ffffff text=#2b2b2b accent=#7a3e65 on_accent=#ffffff heading=sans