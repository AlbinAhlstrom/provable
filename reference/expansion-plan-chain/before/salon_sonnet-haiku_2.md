### 1. Default Landing & Cold-Start Behavior

- Page opens on the booking form with the salon header and card 1 "1 Choose a service" visible; no view is pre-selected.
- Service rows fill the Service part, showing `Service.name` and `Service.duration_minutes` as "45 min".
- While services load, show three grey placeholder rows of the row's height, no text.
- If `Service` has no records, show "No services are listed yet." in grey inside card 1.
- If the service load fails, show "Services could not be loaded. Refresh the page to try again." in the red error style.
- Card 2 opens locked, greyed, with "Choose a service first." beneath its title.
- Card 3 opens locked, greyed, with "Choose a day first." beneath its title.
- Card 4 opens with empty Name, Phone and Email fields; no contact data is pre-filled.
- Day strip shows 14 consecutive days from today, including today, once a service is chosen.
- Times for a chosen day fill the Time part from `TimeSlot.start_datetime` and fit `Service.duration_minutes`.
- While times load, show a grey placeholder grid of six buttons, no text.
- If a day has no free times, show "No times left on this day" in grey inside card 3.
- If the time load fails, show "Times could not be loaded. Choose the day again to retry." in the red error style.
- The Request booking button opens disabled and grey, with no prompt beside it.

### 2. Primary Navigation & View Structure

- The product is one view: the booking page, with a confirmation screen that replaces the cards.
- The booking page holds the header and four numbered cards in order: Service, Day, Time, Your details.
- Confirmation screen replaces all cards after a successful submit; no other views exist.
- Confirmation screen has no navigation; its only action is "Book another appointment".
- No menus, login, staff or account areas exist anywhere on the page.
- Sections are reached by scrolling and by Tab order, top to bottom.

### 3. Workflow Prerequisites & Form Ergonomics

- Cards 2 and 3 are shown locked, greyed, with one line saying what to do first.
- Card 2 unlocks when a service is chosen; choosing a different service clears the chosen time.
- Card 3 unlocks when a day is chosen; the day strip stays visible while locked.
- Disabled days use grey text with strike-through and are not selectable; they carry no explanatory text.
- Taken times are disabled grey buttons; clicking them does nothing.
- Request booking stays disabled until service, time and all three details are valid.
- Beside the disabled button, show "Choose a service, a time and valid details to continue." until complete.
- Fields validate on blur and on attempted submit; invalid fields get a red border and message beneath.
- Name field: text input, label "Name", refused with "Enter 2 to 80 characters for your name."
- Phone field: phone input, label "Phone", refused with "Enter a phone number with 7 to 15 digits."
- Email field: email input, label "Email", refused with "Enter an email address like name@example.com."
- An empty required field shows "Name is required.", "Phone is required." or "Email is required." instead.
- Corrected fields remove their message immediately as the client types a valid value.
- Submit is refused with no booking created if any part is invalid; focus moves to the first invalid field.
- A time taken during submit shows the error banner and refreshes the Time part; the chosen time is cleared.
- Double-clicks on Request booking are ignored while the request is sending.

### 4. Human Copy & Action Labeling

**Seen:**
- Header: salon name, configured for the business, in white on plum; no other header text.
- Card titles: "1 Choose a service", "2 Choose a day", "3 Choose a time", "4 Your details".
- Locked hints: "Choose a service first." (card 2); "Choose a day first." (card 3).
- Empty and error states: "No services are listed yet."; "No times left on this day"; "Services could not be loaded. Refresh the page to try again."; "Times could not be loaded. Choose the day again to retry."
- Field labels: "Name", "Phone", "Email".
- Field messages: "Name is required.", "Enter 2 to 80 characters for your name.", "Phone is required.", "Enter a phone number with 7 to 15 digits.", "Email is required.", "Enter an email address like name@example.com."
- Summary line: service name, day and time, for example "Haircut, Tue 12 May, 10:00".
- Button prompt: "Choose a service, a time and valid details to continue."
- Primary button: "Request booking".
- Error banners: "That time was just taken. Choose another time." and "Booking could not be sent. Try again."
- Confirmation title: "Booking requested".
- Confirmation labels: "Service", "Day", "Time", "Name", "Phone", "Email", "Status".
- Status badges: "Requested" (amber); "Confirmed" (green).
- Link: "Book another appointment".

**Spoken only:**
- Day buttons: weekday and date, for example "Tue 12 May", with "Unavailable" when disabled.
- Time buttons: start time, with "Taken" when disabled.
- Selected service row: "Selected".
- Spinner on Request booking: "Sending booking".
- Check icon on the confirmation: "Booking requested".
- Header salon name is read as a heading.

### 5. Contextual Action Placement

- Service choice sits inside card 1 on each row; a click or Enter selects it.
- Day buttons sit inside card 2 directly under the card title.
- Time buttons sit inside card 3 directly under the card title.
- Summary line sits directly above the Request booking button, in card 4's footer.
- Request booking sits full width at the foot of card 4, below the fields.
- Error banner sits directly above Request booking, inside card 4.
- Booking prompt sits directly beside the disabled Request booking button.
- "Book another appointment" sits directly beneath the confirmation card.
- No action sits outside the card it changes.

### 6. Visual Direction

- **Feel:** a calm, warm stepwise appointment page, like a simple salon booking sheet: light, plum-accented, numbered in order.
- **Palette:** background #FAF6F1 (flat warm off-white); surface #FFFFFF cards; text #2B1F2A; accent #4A2545 (plum) for header, selected states and primary button; on-accent #FFFFFF; hover and pale fill #F1E4EF; outline #D9D0C7; pressed #361A33; disabled #CFC7BF; error #B3261E with banner fill #FBE9E7; success #2E7D32; amber badge #B26A00.
- **Type:** font-sans throughout; card titles 20px semibold; body and field text 16px regular; labels 14px medium; header salon name 18px semibold.
- **First screen:** plum header band with salon name, then card 1 with service rows, then locked cards 2 and 3 and card 4 below; nothing is written above the header.
- **Form of the main view:** a single stacked column of numbered cards, a booking form in order of steps; each card is one unit with a title and its controls; day strip scrolls sideways if it overflows.
- **Shape and rhythm:** cards 8px radius, soft shadow (shadow-md tint), 1px outline on rows and fields; 24px between cards; 16px inside cards; content column 640px max, full width below 640px; buttons 48px tall, 8px radius; service rows 56px tall; time buttons 44px tall in a grid of four columns on wide screens, three on phones.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f1 surface=#ffffff text=#2b1f2a accent=#4a2545 on_accent=#ffffff heading=sans