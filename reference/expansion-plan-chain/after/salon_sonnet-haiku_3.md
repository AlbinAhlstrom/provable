### 1. Default Landing & Cold-Start Behavior
- Service records fill the "Choose a service" card list, showing `Service.name` and `Service.duration_minutes` as "Cut, 45 min".
- While services load: three grey placeholder cards in the Service card, no text.
- No services: "No services are offered yet." in grey text inside the Service card.
- Services fail to load: "Services could not be loaded. Try again." with a "Try again" button.
- TimeSlot records fill the day strip and time grid, showing `TimeSlot.slot_date`, `start_time`, `state`.
- Time loading: the day strip shows grey placeholder tiles; the time grid shows grey placeholder pills.
- Time load fails: "Times could not be loaded. Try again." with a "Try again" button under the day strip.
- Opening view: the Service step is active, the day strip is faded and disabled, the Time and Your details cards are shown but inert.
- No booking records exist at start; the confirmation card appears only after a successful submit.

### 2. Primary Navigation & View Structure
- One view: the single booking page, no tabs or menus.
- Header: plum band "Book an appointment" at the top, full width.
- Three stacked cards in a 640px centred column: "Service", "Time", "Your details".
- Confirmation view replaces the three cards with one confirmation card.
- Summary line sits above the submit button inside "Your details".
- No navigation to staff, payments, products or loyalty.

### 3. Workflow Prerequisites & Form Ergonomics
- Day strip is shown faded before a service is chosen, with one line above it: "Choose a service first."
- Time grid stays hidden until a day is chosen; the Time card shows "Choose a day to see times." under the strip.
- Submit button is pale grey until service, time and valid details exist; beside it the summary line shows what is missing as "Choose a time and enter your details." when incomplete.
- Choosing a service clears any chosen time; choosing a day clears any chosen time.
- Taken slots are shown struck through and ignore clicks silently.
- A day with no free times is greyed and not clickable; the note "No free times on this day." appears under the strip.
- Past days and times are never shown; days beyond the next 14 are never shown.
- Name input: text input, label "Name", refusal messages: "Enter your name." (empty or spaces) and "Name must be 80 characters or fewer."
- Phone input: telephone input, label "Phone", refusal message: "Enter a phone number with 7 to 15 digits."
- Email input: email input, label "Email", refusal message: "Enter an email address like name@example.com."
- Fields are validated on leave; typing clears that field's error.
- Enter in any field submits as "Request booking" does.
- Double submit ignored while sending.
- Submit refused with a message beside each missing item, for example "Choose a time." under the summary.
- Slot just taken: banner "That time was just taken, please pick another." and the time list refreshes.

### 4. Human Copy & Action Labeling
Seen:
- "Book an appointment" – header title.
- "Service" – card heading, step one.
- "Time" – card heading, step two.
- "Your details" – card heading, step three.
- "Choose a service first." – under the faded day strip.
- "Choose a day to see times." – in the Time card before a day is chosen.
- "No free times on this day." – grey note under the day strip.
- "Name", "Phone", "Email" – field labels.
- "Enter your name.", "Enter a phone number with 7 to 15 digits.", "Enter an email address like name@example.com." – field messages.
- "Choose a time." – message beside a missing slot.
- "That time was just taken, please pick another" – error banner.
- "Could not send your request. Try again." – error banner on failed send.
- "Request booking" – submit button.
- "Sending…" – submit button while sending.
- "Requested" – amber status badge.
- "Confirmed" – green status badge.
- "Your request has been sent. The salon will confirm it." – confirmation card line.
- "Book another" – button on confirmation card.
- "Services could not be loaded. Try again." / "Times could not be loaded. Try again." – load errors with "Try again" button.
- "No services are offered yet." – empty service list.
- Day tile weekday and date, e.g. "Mon 14".

Spoken only:
- "Service option Cut, 45 minutes" – service card.
- "Day Monday 14" – day tile; "Today" for today's tile.
- "Time 10:00, free" / "Time 11:00, taken" – time pills.
- "Remove" not used; check mark labelled "Selected".
- "Booking summary" – summary region.

### 5. Contextual Action Placement
- Service selection action sits on the service card itself.
- Day selection sits on each day tile in the strip directly above the time grid.
- Time selection sits on each pill in the time grid.
- "Request booking" sits at the foot of the "Your details" card, below the summary line.
- Error banner sits directly above "Request booking".
- "Try again" sits beside the load error in its own card or strip.
- "Book another" sits on the confirmation card, below the summary.
- Field messages sit directly beneath their field.

### 6. Visual Direction
- **Feel**: a calm, warm salon booking page, like a tidy appointment card set on a soft counter.
- **Palette**: background #FAF6F2 full width; surfaces white #FFFFFF; text deep plum #4A2B3F; accent plum #4A2B3F for actions and selections; rose #C0728A for hover borders and today's dot; pale rose #F6E3E8 for selected service fill; taken slot grey #E4E0DC; disabled submit pale grey #E4E0DC with grey text #8A8580; success green #2E7D4F with white text; status amber #E0A526 with dark text #1C1917; error red #B3261E for outlines and messages; error banner tint #FBE9E7.
- **Type**: `font-sans` for all text, headings in semibold; largest text on the first screen is the header title at 28px, bold.
- **First screen**: the plum header band sits across the top; below it the three cards are centred in a 640px column, the Service card first and fully visible without scrolling on a desktop viewport; the page background fills the rest.
- **Form of the main view**: a stacked form of three cards in one 640px column; the Service cards are a single column of full-width rows, each 56px tall; the day strip is 14 tiles of 56px wide in a horizontal row, scrolling sideways on narrow screens; the time grid is 4 pills per row of 96px wide each, wrapping onto further rows; on screens narrower than 640px the column fills the width with 16px side margins.
- **Shape and rhythm**: cards use 16px corner radius, a white raised shadow (`shadow-md`) and 24px padding; pills and day tiles use full rounding; fields use 8px radius with a 1px grey #CFC8C2 outline; 24px spacing between cards, 16px between parts inside a card; medium density.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#4a2b3f accent=#4a2b3f on_accent=#ffffff heading=sans