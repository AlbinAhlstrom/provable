# A booking page for a hair salon

## 1. People and their journey
**Client** (the only role). Wants to see which times are free for a service and book one without phoning.
Path: arrives, picks a service, picks a day, picks a free time, enters name, phone and email, submits, sees a confirmation showing the request as "Requested".
Salon staff confirm requests outside the interface; they get no screens or controls.

## 2. How it looks
A single calm, light, centred booking page in a salon's style: warm off-white background, deep plum text and accents, rounded cards, generous spacing.

- Page background: flat warm off-white (#FAF6F2), full width, behind everything.
- Header: top of the page, flat plum (#4A2B3F) band with the white title "Book an appointment".
- Progress cards: three stacked white raised cards (Service, Time, Your details) in a centred column 640px wide, each with a plum heading.
- Service option: a white outlined card with service name and duration in minutes, e.g. "Cut, 45 min". Hover: the border turns rose (#C0728A). Selected: plum border with a pale rose (#F6E3E8) fill and a check mark.
- Day strip: a row of the next 14 days, each a small outlined tile with weekday and date. Selected: solid plum with white text. Today: a small rose dot. Days with no free times: greyed text, not clickable. Before a service is chosen the strip is faded and disabled.
- Time slot: a pill button listing a start time, in a grid under the day strip. Free: white with plum outline. Hover: rose outline. Selected: solid plum, white text. Taken: grey (#E4E0DC) fill, struck-through text, not clickable.
- Empty-times note: grey text under the strip, shown when the chosen day has no free times.
- Details fields: Name, Phone, Email, each a text box with a label above and a grey outline. Focus: plum outline. Error: red (#B3261E) outline with a red message beneath.
- Summary line: sits above the submit button and shows the service, day, time and end time in plum text.
- Submit button "Request booking": full width, solid plum, white text. Hover: darker plum. Disabled until service, time and valid details are present: pale grey. While sending: shows "Sending…" and is disabled.
- Confirmation card: replaces the three cards, white raised, with a green (#2E7D4F) check, the booking summary and a status badge "Requested" in amber (#E0A526) with dark text, and a "Book another" outlined button. A badge for "Confirmed" is green with white text.
- Error banner: a red-tinted bar above the submit button when sending fails or the slot has just been taken.

## 3. How it is used
- Click or tap a service card: selects it, loads days and times, and deselects any earlier time.
- Click or tap a day tile: shows that day's times and clears any chosen time.
- Click or tap a free time pill: selects it and updates the summary line.
- Click a different pill: moves the selection to it.
- Type in Name, Phone or Email: fills the field and clears its error.
- Leave a field: checks it and shows any error.
- Click or tap "Request booking": checks everything, then submits and shows the confirmation.
- Press Enter in a field: acts as pressing "Request booking".
- Click "Book another": clears everything and returns to the service step.

## 4. Scope
One loop: choose a service, day and time, give contact details, submit, and see the request. Out of scope: staff rosters and stylist choice, payments and deposits, product sales, and loyalty.

## 5. Things and their states
- **Service**: name, duration in minutes. It does not change.
- **Time slot**: date, start time, state Free or Taken. Free becomes Taken when a booking claims it.
- **Booking**: service, slot, name, phone, email, status. It is created as Requested and becomes Confirmed when the salon confirms it outside the interface. The client sees the status.

## 6. Rules
- A service must be chosen before days and times are offered; otherwise the strip stays disabled.
- Only Free slots can be chosen; a click on a Taken slot is ignored.
- A slot must fit the service's duration before closing time; slots that do not fit are shown as Taken.
- A booking needs a service, a slot, a name, a phone and a valid email; otherwise submit is refused with field messages.
- Name must be non-empty after trimming and at most 80 characters.
- Phone must have 7–15 digits; spaces, dashes, brackets and a leading + are allowed.
- Email must have the form name@domain.
- Past days and past times are never offered.
- Only the next 14 days can be booked.
- A slot taken by one booking cannot be booked again; if it was taken meanwhile, the client sees "That time was just taken, please pick another" and the time list refreshes.
- A booking made covers the service's full duration, and overlapping slots become Taken.
- Every new booking has status Requested.
- Double submits are ignored while sending.