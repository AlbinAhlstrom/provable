# Hair Salon Booking Page: Product Specification

## 1. People and their journey

**Client** (the only role in this interface): a person who wants a hair appointment.
- Needs to see the services with their durations, the days and times they can book, and a form for their contact details.
- Decides which service, which day and which time suits them, then gives their name and phone number.
- Path: arrives on the page, chooses a service, chooses a day, chooses a free time, enters contact details, submits, and sees "Requested".

*Outside the interface:* Salon staff confirm or decline requests and move them to Confirmed. They have no screens here.

## 2. How it looks

A plain single-column online appointment form on a white page, with three numbered panels stacked top to bottom, like a standard web booking form.

- **Page background:** Flat, pure white, covers the whole screen.
- **Page title:** Top-left, "Book an appointment", charcoal text, 28px bold, with a thin charcoal rule below it.
- **Service panel, step 1:** Below the title, a white panel with a light grey outline, headed "1. Choose a service" in charcoal.
- **Service option:** Full-width flat row in the panel, showing the service name in charcoal and its duration, e.g. "45 min", in grey on the right.
- **Service option, selected:** Row filled pale teal with a 2px dark teal outline and a dark teal tick at the left.
- **Service option, hover or press:** Row fill changes to very light grey.
- **Day panel, step 2:** Below the service panel, headed "2. Choose a day", a horizontal row of day buttons for the next 14 days, with weekday above date.
- **Day button:** Flat white, light grey outline, charcoal text.
- **Day button, selected:** Dark teal fill, white text.
- **Day button, no free time for the chosen service:** Grey text, no outline, not clickable.
- **Time panel, step 2 (continued):** Under the day row, a grid of time buttons for the chosen day, headed "Free times".
- **Time button, free:** Flat white, dark teal outline, dark teal text.
- **Time button, selected:** Dark teal fill, white text.
- **Time button, taken or too short for the service:** Light grey fill, grey strikethrough text, not clickable; hidden for past times.
- **Contact panel, step 3:** Below the time grid, headed "3. Your details", with three stacked fields.
- **Field:** White with a grey outline, charcoal text, label above in charcoal. Labels: "Name *", "Phone *", "Email".
- **Field, focused:** Dark teal outline, 2px.
- **Field, invalid:** Red outline and red message under it, e.g. "Enter a phone number."
- **Submit button:** Full width at the bottom, dark teal fill, white text "Request booking".
- **Submit button, not ready:** Light grey fill, grey text, not clickable, until a service, a time, a name and a phone number are given.
- **Submit button, sending:** Dark teal, with the text "Sending…" and no further presses.
- **Confirmation panel:** Replaces the three panels after success; white with dark teal outline, headed "Request received", showing service, date, time and a status badge.
- **Status badge, Requested:** Amber fill, charcoal text, reading "Requested".
- **Error banner:** Red-outlined strip above the submit button for refused submissions, with red text.

## 3. How it is used

- **Click a service row:** Selects that service and clears any earlier service; time buttons refresh for its duration.
- **Tap a service row:** Same as click on a phone.
- **Click a day button:** Shows free times for that day and the chosen service; clears any chosen time.
- **Tap a day button:** Same as click on a phone.
- **Click a free time button:** Selects that time; a second click on another time moves the selection.
- **Tap a free time button:** Same as click on a phone.
- **Type in Name, Phone or Email:** Fields validate when you leave them; errors show beside the field.
- **Tab or tap from field to field:** Moves focus to the next field in order: name, phone, email, submit.
- **Click or tap "Request booking":** Sends the request if everything is valid; shows the confirmation panel.
- **Press Enter in any field:** Same as clicking "Request booking".
- **Click the page title or scroll up:** Returns to the top; nothing is changed.

## 4. Scope

A client opens the page, chooses one service, chooses a day, chooses a free time that fits the service, enters a name and phone number, and submits a booking request. The page shows that the request is Requested. The salon confirms it outside this page. Nothing else is in scope: no sign-in, no payment, no staff choice, no products, no loyalty.

## 5. Things and their states

- **Service:** Name, duration in minutes. Active or hidden. Moves to hidden when the salon withdraws it (outside the interface).
- **Time slot:** Start time and date, which a booking can use if the chosen service fits before the next booked time. States: Free, Booked. Becomes Booked when a booking request is created; returns to Free only if that request is declined outside the interface.
- **Booking request:** Service, start time, name, phone, optional email, status. States: Requested, then Confirmed. Created as Requested; moves to Confirmed when the salon confirms it (outside the interface).

## 6. Rules

- Only one service can be chosen at a time; choosing another replaces it.
- Only dates from today onward appear; past times never appear.
- A time is offered only if the chosen service fits in full before the next booked time; otherwise it is greyed out.
- Changing the service re-checks the chosen time; if it no longer fits, the time is cleared and the client is asked to choose again.
- A time is offered only if it is still Free; a time booked by someone else is greyed out on the next refresh.
- If a time is taken between selection and submission, the request is refused with "That time is no longer free. Choose another time." The time is greyed out and nothing is saved.
- Name is required; a request with no name is refused, with the error shown beside the field.
- Phone is required; it must contain 7 to 15 digits and may start with +, spaces and hyphens allowed. Otherwise refused, with error shown.
- Email is optional; if given, it must contain one @ and a dot after it. Otherwise refused, with error shown.
- A request missing service or time cannot be submitted; the button stays unavailable.
- A request is always created with status Requested; the client cannot set Confirmed.
- After a successful submission, the button is disabled, so one press creates one booking request only.
- If the submission fails for connection reasons, nothing is saved; the form keeps all entered values and shows "Could not send. Please try again."
- The client cannot cancel or change a request from this page; the confirmation shows no cancel control.
- Hidden services and staff-declined bookings never appear in the client's view.