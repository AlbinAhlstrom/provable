### 1. Default Landing & Cold-Start Behavior
- First view is the booking page itself: header, then step 1 "Service" open with the service list visible; no empty or placeholder screen.
- Services list is the `Service` entity: each row shows `Service.name` left and `Service.duration_minutes` right as "N min".
- While services load: three muted grey placeholder rows of equal height, labelled "Loading services…".
- No services (empty list): one line in the step card: "No services are offered right now."
- Service load failed: one line in the step card: "Services could not be loaded." with a "Try again" button.
- Steps 2 to 4 are shown muted and unclickable from the start, with no further text beside them.
- Day row shows the next 14 days from today as `TimeSlot.slot_date`, each faded until a service is chosen.
- Time slots come from `TimeSlot.start_time` and `TimeSlot.end_time`, loaded for the chosen service and day.
- Time-slot loading: grid replaced by the text "Loading times…".
- Time-slot load failed: grid replaced by "Times could not be loaded." with a "Try again" button.
- Day with no free times for the service: faded and unclickable; no explanation needed.
- Day selected with no free times (possible after a refresh): grid replaced by "No times left on this day."
- Step 4 fields are empty on arrival; nothing is pre-filled.

### 2. Primary Navigation & View Structure
- One view only: the booking page; there is no tab bar, menu or second screen.
- Steps are stacked in one column in order: Service, Day, Time, Your details.
- Step 2 appears only after a service is chosen; step 3 appears only after a day is chosen with free times, showing them in place.
- Step 4 is shown muted and unclickable until a time is chosen, with no extra line.
- Confirmation panel replaces the whole card content after submission; it is the second and last state.
- "Book another" returns to the step 1 state of the same view; no navigation is added.
- Changing the service after a time is chosen clears the time and recalculates the grid for the same day.
- Tab order follows the visual order top to bottom; every option is focusable.

### 3. Workflow Prerequisites & Form Ergonomics
- Step 2 is not shown until a service is chosen; it then appears below step 1.
- Steps 3 and 4 are shown muted with no text; they are unclickable until their prior step is complete.
- Day buttons with no free times are faded and disabled; days with free times are clickable.
- Booked or past time slots are faded with strikethrough and ignore clicks.
- Clicking a booked slot does nothing; the selection is unchanged and no message appears.
- Name field: text input, label "Name", max 80 characters; refused message "Enter your name (up to 80 characters)."
- Phone field: telephone input, label "Phone", refused message "Enter a phone number with 7 to 15 digits."
- Email field: email input, label "Email", refused message "Enter an email address like name@example.com."
- Validation runs when a field is left; focus shows a dusty-rose outline, invalid shows red outline and message.
- "Request booking" button is disabled (light grey) until service, slot and all fields are valid; no extra text explains why.
- Summary line is hidden until a time is chosen, then shows service, date, time and end time.
- Slot taken at submit: error banner "That time was just taken. Choose another time." and the slot grid refreshes.
- Sending failure: error banner "Your booking could not be sent. Try again."
- Double submits: second click ignored while the button reads "Sending…".
- Client cannot cancel or edit; no control for it appears anywhere.

### 4. Human Copy & Action Labeling
- Header title: "Hair salon booking" (salon name is a fixed title, not an entity attribute on this page).
- Header line: "Book your appointment".
- Step headings: "1 Service", "2 Day", "3 Time", "4 Your details".
- Day row label (spoken): "Choose a day"; day buttons show weekday and date, e.g. "Mon 12".
- Time grid label (spoken): "Choose a time".
- Empty day message: "No times left on this day."
- Summary line: "[Service.name], [date], [start time] to [end time]".
- Submit button: "Request booking"; while sending: "Sending…".
- Confirmation heading: "Booking requested".
- Confirmation status badge: "Requested" (amber); "Confirmed" (green) when `Booking.status` is confirmed.
- Confirmation link: "Book another".
- Load-failed buttons: "Try again".
- Spoken only: the check icon on confirmation is "Booking requested"; decorative icons are hidden from screen readers; the Name, Phone and Email inputs use their visible labels.

### 5. Contextual Action Placement
- Service rows are the action for step 1; clicking a row opens step 2 directly beneath it.
- Day buttons sit in step 2; time slots sit in step 3 under the chosen day.
- Summary line sits directly above the submit button in step 4.
- Submit button sits at the foot of the card, full width, below the error banner.
- Error banner sits directly above the submit button, inside the card.
- "Try again" for a failed load sits in the same step, beside the failure message.
- "Book another" sits below the confirmation panel, in the card.
- No action appears in the header.

### 6. Visual Direction
- **Feel**: a calm, friendly appointment widget in a warm salon setting; soft, light and tidy like a familiar booking form.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; secondary text and disabled steps #9A9A9A; accent dusty rose #C77D8E; pressed accent #A9606F; pale rose fill #F8E6EA; hover fill #F3ECE6; outline light grey #D9D2CB; button disabled #E4E4E4 with text #9A9A9A; error red #C0392B; error banner fill #FBE9E7; requested amber #E0A030; confirmed green #3E8E5A; green check #3E8E5A.
- **Type**: `font-sans` for headings and body; step headings semibold 16px; header title bold 24px; body 16px; labels 14px.
- **First screen**: header band at top, then the content card with step 1 open and the service rows visible; nothing above the card beyond the header.
- **Form of the main view**: a single stacked booking card in one column, 640px maximum width; the service rows are a list, the day buttons a horizontal row of 64px-wide buttons with 8px gaps, the time slots a grid of 96px-wide buttons with 8px gaps. Parts are sized to their content and scroll sideways on narrow screens; on phones the card is full width with 16px side margins and the day row scrolls horizontally.
- **Shape and rhythm**: card radius 12px, soft shadow `0 2px 8px rgba(0,0,0,0.08)`; option and button radius 8px; spacing 24px between steps; page margin 24px desktop, 16px phone; medium density.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans