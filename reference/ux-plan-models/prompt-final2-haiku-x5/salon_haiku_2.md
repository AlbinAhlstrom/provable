### 1. Default Landing & Cold-Start Behavior

- The page opens on the single booking card with step 1, "Service", active and the header above it.
- Service records fill the step 1 option rows: `Service.name` on the left, `Service.duration_minutes` as "45 min" on the right.
- While services load, step 1 shows "Loading services…" in place of the rows.
- If no services load, step 1 shows "No services are available to book right now." with no other control.
- If services fail to load, step 1 shows "Services could not be loaded." and a "Try again" button beneath it.
- Steps 2 to 4 show muted from the start, with their one-line prompts, and no days or times appear yet.
- The day strip (step 2) fills from `TimeSlot.slot_date`, showing the next 14 days, and only after a service is chosen.
- While times load, step 3 shows "Loading times…" in place of the grid.
- The time grid (step 3) fills from `TimeSlot.start_time` and `TimeSlot.end_time`, with `TimeSlot.is_booked` deciding open or unavailable.
- If the chosen day has no free times, the grid is replaced by "No times left on this day."
- If no day in the 14-day strip has free times, step 2 shows "No days have free times for this service."
- If times fail to load, step 3 shows "Times could not be loaded." and a "Try again" button beneath it.
- No Booking records are loaded; a booking exists only after the client submits.

### 2. Primary Navigation & View Structure

- The product is one view: the booking page, with the confirmation panel as a state of the same view.
- There is no navigation menu, tab bar or separate page for any step.
- Steps 1 to 4 stay in one card, in order, on one scrolling page.
- The confirmation panel replaces the form inside the same card; no URL change is needed.
- "Book another" returns to step 1 within the same view.
- Header contains only "Salon booking" and "Book your appointment"; it carries no links.

### 3. Workflow Prerequisites & Form Ergonomics

- Step 2 (Day) is muted with the line "Choose a service first." beneath its heading until a service is chosen.
- Step 3 (Time) is muted with the line "Choose a day first." beneath its heading until a day is chosen.
- Step 4 (Your details) is muted with the line "Choose a time first." beneath its heading until a time is chosen.
- Muted steps do not respond to clicks or Tab focus until they become active.
- The day strip appears only after a service is chosen; before that it is not drawn.
- The disabled button shows a line above it: "Still needed: " followed by the missing items, named in words.
- The "Still needed" line lists only what is missing, in step order, and disappears when the button is enabled.
- Selecting a different service clears the chosen time and reloads the slots for that service.
- Service row: a selectable option, activated by click, tap, Enter or Space.
- Day button: a selectable option showing weekday and date, activated the same way.
- Time slot: a selectable option showing start time, activated the same way.
- Name: text input, label "Name", refused message "Enter your name, up to 80 characters."
- Phone: telephone input, label "Phone", refused message "Enter a phone number with 7 to 15 digits."
- Email: email input, label "Email", refused message "Enter an email address, such as name@example.com."
- Fields validate when left, not while typing; a refused field keeps its typed value.
- Empty name shows "Enter your name, up to 80 characters."; empty phone and email show their own messages above.
- Focused field shows a dusty-rose outline; a refused field shows a red outline with its message beneath.
- A slot taken after it was shown is refused, with the error banner and a refreshed grid.

### 4. Human Copy & Action Labeling

- Headings: "1 Service", "2 Day", "3 Time", "4 Your details" — the step numbers stay visible at all times.
- Header title: "Salon booking"; subtitle: "Book your appointment".
- Option labels show the service name and its duration; the time slots show only the start time.
- Summary line, once a time is chosen: "{Service.name}, {day}, {start time} to {end time}".
- Primary button: "Request booking"; while sending: "Sending…".
- Error banner, failed send: "Your booking could not be sent. Try again."
- Error banner, slot taken: "That time was just taken. Choose another time."
- Confirmation heading: "Booking requested"; body: "The salon will confirm your booking."
- Confirmation badges: "Requested" in amber, "Confirmed" in green.
- Link below confirmation: "Book another".
- Load error action: "Try again"; empty-state lines as set out in section 1.
- Spoken only: each service row reads "{name}, {duration} minutes, selected or not selected".
- Spoken only: each day button reads "{weekday} {date}, free times" or "{weekday} {date}, no free times".
- Spoken only: each time slot reads "{start time}, open" or "{start time}, booked or passed".
- Spoken only: the green check in the confirmation reads "Confirmed step complete"; the loading spinners read "Loading".

### 5. Contextual Action Placement

- Service rows sit inside step 1, each row being the whole action; no separate button.
- Day buttons sit inside step 2 on one horizontal row.
- Time slots sit inside step 3 directly under the day strip.
- The summary line sits above the button in the details step, hidden until a time is chosen.
- The error banner sits above the "Request booking" button, inside the details step.
- "Request booking" sits at the foot of step 4, full width, the only primary action.
- "Try again" sits directly beneath the load-error message it repairs, in the same step.
- "Book another" sits below the confirmation panel, replacing the form's action.
- Nothing on the page edits or cancels a booking; no such controls are placed anywhere.

### 6. Visual Direction

- **Feel**: a tidy paper appointment card on a warm off-white page, the look of a familiar salon booking widget.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; muted text and muted step numbers #9A9A9A; outlines #D9D2CB; hover fill #F3ECE6; accent and selected outline #C77D8E; pressed #A9606F; selected fill #F8E6EA; error red #C0392B; error banner fill #FBE9E7; amber badge #E0A030 with text #2B2B2B; green badge and check #3E8E5A with text #FFFFFF; disabled button fill #E6E6E6 with text #9A9A9A; faded unavailable slots #9A9A9A with strikethrough.
- **Type**: sans throughout (system UI stack). Headings bold; body regular 16px. Largest text on the first screen is the "Salon booking" title at 28px, weight 700.
- **First screen**: the header band with its title, then the card with "1 Service" and the service rows already drawn, steps 2 to 4 muted below. No photographs and no marketing copy.
- **Form of the main view**: a single stacked booking card, 640px wide at most, full width on phones, with four numbered steps. The day step is a horizontal strip of 14 day buttons rather than a month calendar, because the window is short. Service rows are 56px high with 16px padding. Day buttons are 64px high and 64px wide, in a horizontally scrolling row on narrow screens. Time slots are 96px wide and 40px high, in a grid of four columns at 640px and above, three below. On a phone the card fills the width and the day strip scrolls sideways.
- **Shape and rhythm**: card radius 12px with a soft shadow of 0 4px 16px rgba(43,43,43,0.08); options, fields and buttons radius 8px with a 1px outline; 32px between steps, 24px card padding (16px on phones); medium density with generous margins.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans