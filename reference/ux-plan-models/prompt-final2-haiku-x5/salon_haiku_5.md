### 1. Default Landing & Cold-Start Behavior

- Service records fill the Service step's option rows, showing `Service.name` left and `Service.duration_minutes` as "45 min" right.
- TimeSlot records fill the Time step's grid, showing each open slot's start time from `TimeSlot.start_time`.
- Day buttons are derived from `TimeSlot.slot_date` for the next 14 days, starting today.
- On arrival, the page opens on the header and the card with step 1 active and steps 2 to 4 muted.
- Opening state shows the services loading, with "Loading services…" in place of the rows.
- Empty services list shows "No services are offered at the moment." in place of the rows.
- Failed service load shows "Services could not be loaded." with a "Try again" button beneath.
- Loading times shows "Loading times…" in place of the grid.
- Failed time load shows "Times could not be loaded." with a "Try again" button beneath.
- Day with no free times shows "No times left on this day." in place of the grid.
- No day free for the chosen service shows "No times are free for this service in the next 14 days."
- Day row is hidden until a service is selected, so no days appear on arrival.
- Summary line is hidden until a time is chosen.

### 2. Primary Navigation & View Structure

- One view only: the booking page, with no tabs, menus or other screens.
- Steps run top to bottom inside one card: Service, Day, Time, Your details.
- Confirmation panel replaces the whole form card after a successful submit.
- Step 1 is open on arrival; each completed step remains visible above the next.
- Changing a choice in an earlier step reopens its later steps with their values kept, except the cleared time.
- "Book another" returns the page to step 1 with every selection cleared.
- No links or navigation items exist outside the card and the header.

### 3. Workflow Prerequisites & Form Ergonomics

- Steps 2 and 3 are visible but muted; under each heading, one line says what to do first.
- Step 2 line reads "Choose a service first."; step 3 line reads "Choose a day first."; step 4 line reads "Choose a time first."
- Day buttons with no free times are faded and unclickable, not hidden.
- Booked or past time slots are faded with strikethrough and ignore clicks, with no message.
- Changing the service after a time is chosen clears the time and shows "Choose a time again." beside the grid.
- Name uses a text input, labelled "Name", with autocomplete set to name.
- Phone uses a telephone input, labelled "Phone", with autocomplete set to tel.
- Email uses an email input, labelled "Email", with autocomplete set to email.
- Name refusal message: "Enter your name, up to 80 characters."
- Phone refusal message: "Enter a phone number with 7 to 15 digits."
- Email refusal message: "Enter an email address such as name@example.com."
- Fields validate on leaving; the message sits below the field and clears when the value is fixed.
- Disabled button sits with a line beside it listing what is missing, e.g. "Still needed: name, phone".
- Double submit is ignored while sending; the button reads "Sending…" and stays disabled.

### 4. Human Copy & Action Labeling

- Page title: "Salon booking"; subtitle: "Book your appointment".
- Step headings: "1 Service", "2 Day", "3 Time", "4 Your details".
- Option label: service name with duration, e.g. "45 min".
- Day button label: weekday and date, e.g. "Mon 12 May".
- Summary line: "[Service.name], [day], [start time] to [end time]".
- Primary button: "Request booking".
- Sending state: "Sending…".
- Error banner, slot taken: "That time was just taken. Choose another time."
- Error banner, sending failed: "Your booking could not be sent. Try again."
- Confirmation heading: "Booking requested".
- Confirmation badges: "Requested" in amber; "Confirmed" in green, when status is confirmed.
- Confirmation secondary action: "Book another".
- Spoken only: each service option reads "[name], [duration] minutes, select".
- Spoken only: each time slot reads "[start time], open" or "[start time], booked".
- Spoken only: the green check in the confirmation reads "Booking sent".
- Spoken only: the header band and card carry no extra names.

### 5. Contextual Action Placement

- Service rows sit inside step 1; choosing one opens step 2 directly beneath it.
- Day buttons sit inside step 2; choosing one reveals the time grid in step 3.
- Time slots sit inside step 3; choosing one reveals the summary line above the button.
- Summary line and error banner sit directly above the "Request booking" button at the card foot.
- "Try again" for a failed load sits in the place that failed, not in a global message.
- "Book another" sits in the confirmation panel beneath the booking summary.
- No action appears in the header.

### 6. Visual Direction

- **Feel**: a calm, friendly salon appointment widget: warm, light, uncluttered, with soft rose accents and clear numbered steps.
- **Palette**: page background #FAF6F2; surface #FFFFFF; text #2B2B2B; accent dusty rose #C77D8E; pressed rose #A9606F; option hover #F3ECE6; option outline #D9D2CB; selected fill #F8E6EA; muted step and unavailable grey #9A9A9A; error red #C0392B; error banner fill is a pale red, Tailwind red-50 #FEF2F2; amber Requested badge #E0A030; green Confirmed badge and check #3E8E5A; disabled button light grey #E5E7EB with text #9A9A9A.
- **Type**: sans throughout (Tailwind font-sans); headings semibold; largest text on the first screen is the page title at 28px, font-semibold.
- **First screen**: a header band with "Salon booking" and "Book your appointment", then the card opening on step 1 with the service rows. No photographs and no introduction above the form.
- **Form of the main view**: a single stacked booking form in one card. Service rows are full width at 56px tall. Day buttons are 64px wide by 64px tall in one horizontal row that scrolls sideways on narrow screens. Time slots are 88px wide by 40px tall in a wrapping grid of three to five per row. Each repeated part keeps its fixed size whatever it holds. On phones, the card is full width and the day row scrolls.
- **Shape and rhythm**: card radius 12px with a soft shadow (Tailwind shadow-md); option and button radius 8px; 1px outlines; 32px between steps; 12px between options; the page is airy with generous margins of 24px on phones and 48px on wider screens.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans