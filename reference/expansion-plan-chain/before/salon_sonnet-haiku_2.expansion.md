# A booking page for a hair salon

## 1. People and their journey
**Client** (the only role): a person who wants a hair appointment and prefers not to phone.
- Needs to see: services with durations, open times, and the status of the booking they just made.
- Decides: which service, which day and time, and what contact details to give.
- Path: arrives, picks a service, picks a day, picks a free time, enters name, phone and email, submits, and sees a confirmation screen with status "Requested".

Salon staff, outside the interface, change a booking from requested to confirmed.

## 2. How it looks
A single-column, light, warm booking form, like a simple stepwise appointment page: a salon header followed by stacked numbered cards.

- **Page background**: flat warm off-white (#FAF6F1) filling the screen behind everything.
- **Header**: top, flat deep plum (#4A2545) band with the salon name in white. No other text.
- **Content column**: centred, 640 px wide at most, full width on phones, with cards stacked in order.
- **Step 1 card, Service**: raised white card with a soft shadow, titled "1 Choose a service". Holds one row per service.
- **Service row**: outlined grey (#D9D0C7) with name left, duration ("45 min") right. Hover: border plum. Selected: plum border, pale plum (#F1E4EF) fill, check mark.
- **Step 2 card, Day**: raised white card, titled "2 Choose a day". Shows a horizontal strip of the next 14 days. Locked, greyed, until a service is chosen.
- **Day button**: outlined, weekday over date. Selected: plum fill, white text. Fully booked or closed day: grey text, struck through, disabled.
- **Step 3 card, Time**: raised white card, titled "3 Choose a time". Shows a grid of time buttons. Locked until a day is chosen.
- **Time button**: outlined plum, white fill. Hover: pale plum. Selected: plum fill, white text. Taken: grey fill, grey text, disabled.
- **No-times message**: inside the Time card, grey text "No times left on this day", shown only when the day has no free times.
- **Step 4 card, Your details**: raised white card with Name, Phone and Email fields. Field: outlined grey. Focused: plum border. Invalid after attempted submit: red (#B3261E) border and red message beneath.
- **Summary line**: above the button, plum text, shows the chosen service, day and time once all three are chosen.
- **Book button**: full-width plum fill, white text "Request booking". Pressed: darker plum (#361A33). Disabled until service, time and details are all valid: grey (#CFC7BF). While sending: shows a spinner.
- **Error banner**: above the button, pale red fill with red text, shown if submission fails or the time was just taken.
- **Confirmation screen**: replaces the cards. A white raised card with a green (#2E7D32) check, the booking details, and a status badge "Requested" in amber (#B26A00). A confirmed booking shows a green "Confirmed" badge.
- **New booking link**: plum text link under the confirmation, "Book another appointment".

## 3. How it is used
- Click or tap a service row: selects it, unlocks days, and clears any chosen time.
- Click or tap a day button: selects it and shows that day's times for the service.
- Click or tap a free time button: selects it and updates the summary line.
- Click or tap a taken time or unavailable day: nothing happens.
- Type in Name, Phone and Email: fills the fields; errors clear when corrected.
- Press Tab and Enter or Space: moves between and activates buttons and fields from the keyboard.
- Click or tap Request booking: validates, creates the booking and shows the confirmation.
- Click or tap Book another appointment: returns to an empty form.

## 4. Scope
One loop: choose service, day and time, give contact details, submit, see the confirmation. Left out are staff and stylist assignment, payments and deposits, product sales and loyalty. Notes and accounts are not asked for.

## 5. Things and their states
- **Service**: name, duration in minutes. It has no states.
- **Time slot**: date, start time, and a length that fits the service. It is free, then taken once a booking holds it.
- **Booking**: service, slot, client name, phone and email. It is requested on submit, and confirmed when staff confirm it.

## 6. Rules
- A service must be chosen before days are offered; otherwise the days stay locked.
- Only free slots that fit the service's full duration before closing are shown.
- Changing the service clears the chosen time.
- Past times and past days are not offered.
- Name is required, 2 to 80 characters; otherwise it is refused with a message.
- Phone is required and must be a plausible phone number (7 to 15 digits, optional + and spaces); otherwise it is refused.
- Email is required and must be valid in form; otherwise it is refused.
- Submit is refused until service, time and valid details are present.
- A slot holds only one booking; if it is taken meanwhile, the banner says so, the times refresh, and no booking is made.
- Overlapping slots are taken together with the booked one, so no two bookings overlap.
- A new booking always starts as requested.
- Only staff, outside the interface, can set confirmed; clients cannot change status.
- Double clicks on Request booking create one booking only.