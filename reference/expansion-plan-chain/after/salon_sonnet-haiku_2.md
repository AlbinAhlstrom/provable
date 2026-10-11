### 1. Default Landing & Cold-Start Behavior

- The page opens on the single booking view, with card 1 (services) active and cards 2 and 3 locked.
- Service list: fills from `Service.name` and `Service.duration_minutes`, one row per record, in API order.
- While services load: "Loading services…" centred in card 1.
- When no services exist: "No services are available right now." in card 1, with no controls.
- When the service load fails: "Services could not be loaded." with a "Try again" button in card 1.
- Day strip (card 2) fills from `TimeSlot.slot_date` for the 14 offered days, starting today.
- Day strip while locked: greyed, with "Choose a service first." above it.
- Time slot grid (card 2) fills from `TimeSlot.start_time` and `TimeSlot.state` for the chosen day and service.
- While times load: "Loading times…" in the grid area.
- Time grid when the load fails: "Times could not be loaded." with a "Try again" button.
- Time grid for a day with no free times: "No times left this day".
- Contact form (card 3) is locked until a time is chosen, with "Choose a time first." above it.
- No booking records are loaded; BookingRequest is created only on submit.

### 2. Primary Navigation & View Structure

- One view only: the booking page. No tabs, menus or navigation bar.
- Views inside the page: service list, day and time choice, contact form, confirmation panel.
- Confirmation panel replaces cards 1–3 after a successful submit; no other view exists.
- "Book another" returns to the service list, card 1 active, with cards 2 and 3 locked.
- Header "Book an appointment" stays at the top of the column in every state.

### 3. Workflow Prerequisites & Form Ergonomics

- Order is strict: service, then day, then time, then details. Later cards show locked with their hint line.
- Locked cards ignore clicks and keyboard input; the hint line names the step to do first.
- Changing service clears the chosen day and time; changing day clears the chosen time.
- Reselecting the current service, day or time changes nothing.
- Taken slots are not selectable; they ignore clicks and keyboard activation.
- Name input: text input, label "Name", refused under 2 characters with "Enter at least 2 characters."
- Phone input: telephone input, label "Phone", refused unless 7–15 digits with "Enter 7 to 15 digits."
- Email input: email input, label "Email", refused unless address-shaped with "Enter a valid email address."
- Errors appear when leaving a field; a focused field shows a plum outline instead.
- Submit button is pale grey and disabled until all three fields are valid.
- Beside the disabled button: "Still needed: {missing field names}." Hidden once the form is complete.
- If the slot was taken on submit, the failure notice appears and the time grid refreshes.
- Double-press on submit sends once; the button reads "Sending…" and is not pressable while in flight.
- Failure notice shows the reason above the button; the form keeps the entered values.

### 4. Human Copy & Action Labeling

- Page title: "Book an appointment". Card headings: "Choose a service", "Choose a day and time", "Your details".
- Button labels: "Request booking", "Sending…", "Book another", "Try again".
- Summary line above submit: `Service.name` · `Service.duration_minutes` min · day · start time.
- Confirmation heading: "Booking requested". Status label: "Requested". Message: "The salon will confirm your appointment."
- Failure notices: "That time was just taken. Choose another time." and "Sending failed. Please try again."
- Each control uses one word for one thing: "Request booking" everywhere the submit is named.
- Spoken only: service row "{name}, {duration} minutes, selected or not selected".
- Spoken only: day button "{weekday} {date}, free times or no times left".
- Spoken only: time slot "{time}, free" or "{time}, taken".
- Spoken only: tick icon on confirmation "Requested".
- Spoken only: radio marks carry the name of their service row.

### 5. Contextual Action Placement

- Service selection happens on the service rows in card 1.
- Day selection happens on the day buttons at the top of card 2.
- Time selection happens on the slot buttons directly below the day strip.
- Contact fields sit in card 3, with "Request booking" at the bottom of card 3.
- Failure notice sits directly above "Request booking", inside card 3.
- Summary line sits directly above "Request booking".
- "Book another" sits inside the confirmation panel, where the cards were.
- "Try again" for a failed load sits inside the card whose records failed.

### 6. Visual Direction

- **Feel**: a calm, light salon appointment form; warm, unhurried, like a printed appointment card on soft paper.
- **Palette**: background #FAF6F1; surface #FFFFFF; text #2B2330; accent salon plum #5B2A4A; on-accent #FFFFFF; plum hover fill #F3E8EF; plum darker hover #44203A; taken fill #E6E2DE; unavailable text #9A9A9A; disabled fill #E5E7EB with text #9CA3AF; error #B3261E; error tint #FBE9E7; success #2E7D4F; field border #9A9A9A; label text #2B2330.
- **Type**: headings in `font-serif` (Georgia), body in `font-sans` (system sans); largest text is the title at 28px, semibold.
- **First screen**: a single centred column of three cards on the backdrop, starting 48px under the header; header is the top element; nothing above it introduces the page.
- **Form of the main view**: a stacked column of three cards, one width, inside one frame. Column is 560px wide with 24px padding on each side, so the inner width is 512px. Day buttons are fixed at 64px by 56px with 8px gaps: seven across make 496px, so the strip wraps to two rows of seven. Time slots are fixed 88px by 40px and wrap onto as many lines as needed. Service rows stretch across the full inner width. The contact form stretches across the inner width. Below 600px wide, the column fills the screen with 16px side padding and day buttons shrink to 44px, still seven across.
- **Shape and rhythm**: cards 12px radius, white with a soft shadow (0 2px 8px rgba(43,35,48,0.08)); buttons and slots 8px radius; 24px between cards; 16px inside cards; medium density.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f1 surface=#ffffff text=#2b2330 accent=#5b2a4a on_accent=#ffffff heading=serif