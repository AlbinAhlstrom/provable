### 1. Default Landing & Cold-Start Behavior
- **Service** records fill the step 1 service list. Each row shows `Service.name` on the left and `Service.duration_minutes`, written as "45 min", on the right.
- The booking view is active on arrival. The card shows all three steps open, nothing selected and the summary bar empty.
- **Services loading:** three grey placeholder rows, each 56px tall, with a `bg-gray-100` pulse.
- **No services:** one grey line, "No services are available to book right now."
- **Services failed to load:** a red line, "Services couldn't be loaded.", with a plum text link, "Try again", beside it.
- **Day strip on arrival:** 14 chips starting today. Today's chip carries the rose dot and none is selected.
- **Days on arrival:** closed days, from `OpeningHours.is_closed`, appear struck through. Days with no free start times are struck through once a service is chosen.
- **Default day:** the first available day is pre-selected once a service is chosen, so times show without an extra tap.
- **Time grid on arrival:** it shows "Choose a service first".
- **Time grid with no free times that day:** it shows "No times left this day".
- **Times loading:** eight grey placeholder pills in two rows of four.
- **Times failed to load:** a red line, "Times couldn't be loaded.", with "Try again" beside it.
- **Summary bar with nothing chosen:** it shows the grey text "No time chosen yet".
- **Salon name:** the header shows the product's identity text, "Hair Salon". No record carries it.

### 2. Primary Navigation & View Structure
- **"Book"** is the booking steps, the default view. It is reached by the salon name in the header.
- **"Booking requested"** is the confirmation panel. It replaces the steps after a successful submit.
- **"Check my booking"** is the lookup panel. It is reached by the header link.
- No tabs are used. The header carries the only navigation, and the card swaps its contents.

### 3. Workflow Prerequisites & Form Ergonomics
- **Step 2 before a service is chosen:** the step stays visible. The time grid shows "Choose a service first" and day chips stay unselectable.
- **Step tick:** each step's circle turns to the rose tick once that step is complete.
- **Request booking while grey:** the grey button has a grey line to its left naming the first missing item. The wordings are listed in section 4.
- **Pressing the grey button:** it does nothing.
- **Pressing Request booking while sending:** it does nothing, and the spinner stays.
- **Struck-through day chips:** they do nothing when tapped and use `aria-disabled`.
- **Changing to a longer service:** if the chosen time no longer fits, it clears silently. The summary bar returns to "No time chosen yet".
- **Slot taken at submit:** the error banner shows, the time grid refreshes and the selection clears. The entered details are kept.
- **Name:** text input with `autocomplete="name"`.
- **Phone:** tel input with `autocomplete="tel"`.
- **Email:** email input with `autocomplete="email"`.
- **Notes:** textarea of 3 rows with `maxlength=300`. A grey counter, for example "120/300", sits beneath it at the right.
- **When fields are checked:** each field is checked when it is left, and checked again on each keystroke once it has shown an error.
- **Enter in the Email field:** submits when the request is complete. Enter in Notes adds a new line.
- **Lookup fields:** Reference is a text input, uppercased, 6 characters long. Email is an email input. Look up does nothing until both are filled.

### 4. Human Copy & Action Labeling
**Seen**
- **Step headings:** "Service", "Time", "Your details".
- **Field labels:** "Name", "Phone", "Email", "Notes (optional)".
- **Name error:** "Enter your name (2–80 characters)."
- **Phone error:** "Enter a phone number of 7–15 digits."
- **Email error:** "Enter an email like name@example.com."
- **Empty states:** "Choose a service first", "No times left this day", "No services are available to book right now."
- **Load failures:** "Services couldn't be loaded.", "Times couldn't be loaded.", with the link "Try again".
- **Summary bar:** "No time chosen yet". Once complete, for example "Cut & blow-dry · Tue 14 May · 10:30–11:15".
- **Missing-item lines beside the grey button:** "Choose a service", "Choose a time", "Complete your details".
- **Button:** "Request booking".
- **Error banners:** "That time was just taken. Please pick another." and "Something went wrong. Please try again."
- **Confirmation panel:** "Booking requested", the reference, the summary, the badge, "Copied" and "Book another".
- **Status badges:** "Requested", "Confirmed".
- **Lookup panel:** heading "Check my booking", fields "Reference" and "Email", button "Look up", and the line "No booking found".
- **Header:** "Hair Salon", "Check my booking".

**Spoken only**
- **Day-strip arrows:** "Previous week", "Next week".
- **Day chips:** for example "Tuesday 14 May, today" or "Sunday 19 May, unavailable".
- **Spinner:** "Sending request".
- **Reference:** "Booking reference ABC123, copy".
- **Step ticks:** "Step complete".

### 5. Contextual Action Placement
- Service selection sits on the service rows themselves.
- The day arrows sit at the two ends of the day strip.
- Time selection and deselection sit on the time pills.
- Request booking sits at the right of the summary bar. The error banner sits directly above it.
- Copying the reference happens on the reference text. The tooltip appears above it.
- "Book another" sits beneath the summary on the confirmation panel.
- "Look up" sits below the Email field. The result appears directly below it.

### 6. Visual Direction
- **Feel:** a familiar online appointment booker. It is warm and boutique: cream, plum and rose, calm and personal.
- **Palette:**
  - Page background: cream #FAF6F0.
  - Surface: white #FFFFFF.
  - Text: #2B1A28.
  - Accent: plum #4A2545, with white text on it.
  - Pressed plum: #351A31.
  - Rose: #E8A0B4.
  - Pale rose: #FBEAF0.
  - Secondary text: grey #6B7280.
  - Borders and struck-through day text: #D1D5DB.
  - Field fill: #F3F4F6.
  - Disabled button: #D1D5DB with grey text #6B7280.
  - Error: #C0392B.
  - Requested badge: amber #F5C26B with text #2B1A28.
  - Confirmed badge: green #3E9B6B with white text.
- **Type:**
  - Headings use `font-serif`. Body text uses `font-sans`. The reference uses `font-mono` bold.
  - The largest text on the first screen is the step headings, at 20px semibold. The salon name is 22px.
  - "Booking requested" is 28px.
- **First screen:**
  - The plum header sits at the top, 64px tall.
  - Below it, the white card starts 32px down, opening straight onto step 1.
  - Service rows and the start of step 2 show without scrolling, with no introduction.
- **Form of the main view:** an appointment booker in one card, 720px maximum width. Steps stack vertically, with the summary bar attached at the card's bottom.
  - Service rows are full width and 56px tall.
  - Day chips are 56×64px, fixed. Seven are visible on desktop.
  - Time pills fill equal quarter-width columns and are 40px tall.
  - Below 720px the card goes full width with 16px margins. The day strip scrolls sideways, and the time grid drops to three per row below 400px.
- **Shape and rhythm:**
  - The card has a 12px radius and the shadow `0 4px 16px rgba(0,0,0,0.08)`.
  - Rows and fields have an 8px radius. Pills, chips and badges are fully rounded.
  - The card has 32px padding, with 40px between steps and 8px gaps within lists.
  - The overall density is comfortable.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f0 surface=#ffffff text=#2b1a28 accent=#4a2545 on_accent=#ffffff heading=serif