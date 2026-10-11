# Hair Salon Booking Page: Specification

## 1. People and their journey

**Client** (the salon's customer, the only role in this product)
- Needs to see the services offered with their durations, the open appointment times, and to submit a booking with their contact details.
- Path: opens the page, chooses a service, chooses a free time slot, enters name and contact details, submits, and sees "Requested" with the chosen time. Done.

*Outside the interface:* Salon staff confirm requests by phone or in their own system. This page does not show staff screens or confirm bookings.

## 2. How it looks

A single-column web booking form, in the plain style of a standard online appointment page: white card on a light grey page, dark text, one accent colour for actions, with generous spacing and no decoration.

Parts, from back to front and top to bottom:

- **Page background:** flat light grey (#F2F2F2), fills the whole screen behind everything.
- **Booking card:** white (#FFFFFF), raised with a soft shadow, centred, maximum width 640 px, full width on phones with 16 px side margins.
- **Header:** top of card, salon name in bold dark charcoal (#222222) with a thin grey (#DDDDDD) rule below.
- **Step 1 "Choose a service" heading:** dark charcoal, bold, with the number "1" in a grey circle.
- **Service list:** stacked rows, each showing service name (bold) and duration in grey (#666666), e.g. "Cut and blow-dry · 45 min". Unselected rows are white with a grey (#CCCCCC) outline. Selected row has an accent (#1F6FEB) outline 2 px and a light blue fill (#EAF2FF) with a blue check mark at the right. Pressed row darkens to #F7F7F7.
- **Step 2 "Choose a time" heading:** same style as Step 1, number "2".
- **Date strip:** horizontal row of seven day buttons, each showing weekday above date number. Unselected: white with grey outline. Selected: accent blue fill with white text. Days with no free slots for the chosen service: grey text (#AAAAAA), struck through, not selectable.
- **Time slot grid:** three columns on phones, four on wider screens. Each slot is a button showing start time (e.g. "10:30"). Free: white with blue (#1F6FEB) outline and blue text. Selected: solid blue fill, white text. Taken or unavailable: light grey (#EEEEEE) fill, grey text, no outline, not selectable.
- **Empty-slot message:** when no slots are free on the chosen day, centred grey text: "No free times on this day. Choose another day."
- **Step 3 "Your details" heading:** same style, number "3".
- **Contact form:** four fields stacked, each with a label above in dark charcoal and a white input with grey (#CCCCCC) outline. Focused input outline turns accent blue, 2 px. Fields: Full name, Phone number, Email address, Note (optional, multi-line, three lines high). Invalid field: red (#C0392B) outline and red message below it.
- **Summary line:** above the button, grey text: "Haircut and blow-dry, Saturday 10:30, 45 min".
- **Request booking button:** full width, solid blue (#1F6FEB), white bold text, rounded 6 px. Disabled: light grey (#CCCCCC) fill, grey text. Pressed: darker blue (#1858C0).
- **Confirmation panel:** replaces the form after a successful submit. White card with a green (#2E7D32) top border 4 px, heading "Booking requested" in dark charcoal, then the service, date, time and "The salon will confirm your booking shortly." in grey text, and a grey "Make another booking" text link.
- **Form error banner:** red text (#C0392B) above the button when submission fails: "Your booking could not be sent. Please try again."

## 3. How it is used

- **Tap a service row** (mouse click or finger tap): selects that service, clears any chosen time, and loads its free slots for the date strip.
- **Click or tap a day button:** shows that day's free time slots for the chosen service.
- **Click or tap a free time slot:** selects it; the summary line updates. Tapping a selected slot again clears it.
- **Click or tap a taken or greyed day or slot:** nothing happens.
- **Click in an input and type:** enters the name, phone, email or note; the field's error message clears when the field is corrected.
- **Tab or tap from one field to the next:** moves focus down the form in order.
- **Click or tap "Request booking":** sends the request if all required fields are valid; otherwise shows the field errors and sends nothing.
- **Click or tap "Make another booking":** clears the form and returns to Step 1.
- **Press Enter in a single-line field:** submits the form, the same as clicking "Request booking".

## 4. Scope

The loop: a client chooses a service, a free time on a day, enters name plus phone or email, and submits a booking request, which is recorded as Requested and shown back to them.

Out of scope: staff rosters and stylist choice, payments and deposits, product sales, loyalty, client accounts or logins, viewing or changing a booking after it is sent, and confirmation to the client by message.

Forms ask only for name, phone or email, and an optional note.

## 5. Things and their states

- **Service:** holds name and duration in minutes. Offered or not offered (not offered services are not shown).
- **Time slot:** holds date, start time, and the service it fits. Moves from Free to Taken when a booking request for it is recorded; a Taken slot does not return to Free through this page.
- **Booking request:** holds service, date and start time, client name, phone, email, optional note, and status. Created as Requested when submitted. Moves to Confirmed when salon staff confirm it outside this page. This page shows only Requested at creation.

## 6. Rules

- A service is shown only if it is offered; an offered service is shown with its duration in minutes.
- A time slot is shown only if it is in the future and free for the chosen service's full duration; otherwise it is greyed and cannot be chosen.
- A slot can belong to one booking request; if it is taken, selecting it is refused and the page reloads its slots.
- Only one service and one time slot can be selected at a time; choosing a new service clears the chosen time.
- Step 2 is unavailable until a service is chosen; Step 3 is unavailable until a time is chosen; the button is disabled until all required fields are valid.
- Full name is required; at least one of phone number or email address is required; a phone number must contain 7 to 15 digits, with spaces, hyphens and a leading plus allowed; an email must contain one "@" and a dot after it.
- An invalid field shows its red message beside it and blocks submission; nothing is sent and nothing changes.
- The note is optional and holds up to 300 characters; longer text is refused at the 300th character.
- Pressing "Request booking" twice sends one booking request only; the button is disabled while sending.
- A failed send keeps all entered values and shows the error banner; nothing is recorded.
- A successful send records a booking request with status Requested, marks its slot Taken, and replaces the form with the confirmation panel.
- A booking request cannot be changed or cancelled from this page; the client's only further action is "Make another booking".