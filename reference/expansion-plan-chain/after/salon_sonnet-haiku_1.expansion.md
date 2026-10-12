# A booking page for a hair salon

## 1. People and their journey
**Client** (the only role in the interface). Wants to see which times are free and book a service without phoning.
Path: arrives, chooses a service, picks a day, picks a free time, enters name, phone and email, submits, sees a confirmation that the request is "Requested".
Salon staff confirm requests outside the interface; they have no screens here.

## 2. How it looks
A single-column booking page, calm and warm, like a salon's own website: soft cream background, white cards, deep plum accents, rounded corners.

- **Page background**: flat cream (#FAF5EF), full width, content centred in a column about 640px wide.
- **Header**: top of column, flat, plum (#5B2A4E) text with the salon booking title and one line "Book your appointment".
- **Step 1 card, services**: white raised card with soft shadow, titled "Choose a service", holding the service rows.
- **Service row**: outlined grey (#D9CFC6) row showing name, duration and nothing else. Hover: border plum. Selected: plum fill, white text. Focused: plum outline.
- **Step 2 card, day**: white raised card, titled "Choose a day", with a horizontal strip of the next 14 days, each showing weekday and date.
- **Day chip**: outlined grey. Selected: plum fill, white text. Fully booked or closed day: faded, struck through, not clickable. Today carries a small plum dot.
- **Step 3 card, times**: white raised card, titled "Choose a time", showing a grid of time buttons. Before a service and day are chosen it is faded with the text "Pick a service and day first".
- **Time button**: outlined plum, plum text. Hover: light plum fill (#EFE3EC). Selected: plum fill, white text. Taken: grey fill (#EEE9E4), grey text, not clickable.
- **Empty times message**: inside the times card, grey text "No times left this day" when none are free.
- **Step 4 card, details**: white raised card, titled "Your details", with fields Name, Phone, Email, each with a label above.
- **Field**: white, grey outline. Focused: plum outline. Invalid after a submit attempt: red (#B3261E) outline and a short red message below.
- **Summary line**: above the button, plum text, e.g. "Cut · 45 min · Tue 12 May, 10:30". Hidden until a service and time are chosen.
- **Book button**: full-width plum fill, white text, "Request booking". Disabled until service and time are chosen: grey fill. Pressed: darker plum (#431D39). While sending: shows "Sending…" and is disabled.
- **Failure message**: red text above the button when sending fails, "Could not send. Try again."; entries are kept.
- **Confirmation card**: replaces the step cards after success; white raised card with a green (#2E7D4F) tick, the booking summary, a "Requested" badge in amber (#E0A526) with dark text, and a "Book another" button outlined plum.

## 3. How it is used
- Click or tap a service row: selects it; any previously chosen time is cleared.
- Click or tap a day chip: selects the day and loads its free times; clears the chosen time.
- Click or tap a free time button: selects it; tapping it again deselects.
- Click or tap Name, Phone or Email, then type: enters details.
- Click or tap Request booking: checks the entries, then sends the request.
- Press Tab and Enter or Space: reach and activate every choice by keyboard.
- Click or tap Book another: clears everything and returns to step 1.

## 4. Scope
One loop: choose service, day and time, give contact details, submit, see the "Requested" confirmation. No payments, stylists, products or loyalty.

## 5. Things and their states
- **Service**: name, duration in minutes. Fixed list, no states.
- **Time slot**: date, start time, state Free or Taken. Free becomes Taken when a booking requests it.
- **Booking**: service, slot, name, phone, email, status. Starts Requested; staff outside the interface move it to Confirmed. Shown to the client as Requested at submission.

## 6. Rules
- A service, day and time must all be chosen; otherwise the button stays disabled.
- Name is required; empty is refused with "Enter your name".
- Phone is required and must hold at least 7 digits (spaces, +, - allowed); otherwise refused with a message.
- Email must look like name@domain; otherwise refused with a message.
- Slots are offered only in the future and within the next 14 days.
- A Taken slot cannot be selected; clicks are ignored.
- If a slot is taken by someone else before submit, the booking is refused, times refresh, and the message "That time was just taken. Pick another." shows.
- A slot must fit the chosen service's duration; slots that would overrun closing time are not shown.
- Each slot holds one booking only.
- Every new booking has status Requested.
- Changing the service after choosing a time clears the time.
- Double-clicking the button sends only one request.