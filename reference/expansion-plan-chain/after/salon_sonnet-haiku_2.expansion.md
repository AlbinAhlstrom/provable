# A booking page for a hair salon

## 1. People and their journey
**Client** (the only role). Arrives wanting a haircut or treatment without phoning. Sees the services and durations, picks one, picks a day and an open time, enters name, phone and email, submits, and sees a confirmation that the request is received. Done.

Salon staff confirm requests; they are outside the interface and have no screens.

## 2. How it looks
A single calm, light page like a simple appointment-booking form: a centred column of three numbered cards on a warm off-white backdrop.

- **Page backdrop**: fills the screen, flat warm off-white (#FAF6F1).
- **Header**: top of the column, flat, salon-plum (#5B2A4A) text on the backdrop, shows the page title "Book an appointment".
- **Service list**: card 1, white, raised with a soft shadow, one row per service showing name, duration and a radio mark. Hover: pale plum tint (#F3E8EF). Selected: plum outline and filled radio.
- **Day strip**: card 2, white raised, shows the next 14 days as small buttons with weekday and date. Today has a thin plum ring. Selected: filled plum with white text. Days with no free times: grey text (#9A9A9A), unavailable. Locked with greyed look until a service is chosen.
- **Time slot grid**: card 2, below the day strip, wrapped buttons showing times. Free: white, plum outline. Hover: pale plum fill. Selected: filled plum, white text. Taken: grey fill (#E6E2DE), struck-through text, unavailable. Empty day: the grid shows "No times left this day".
- **Contact form**: card 3, white raised, fields Name, Phone, Email, with labels above and grey outlined boxes. Focus: plum outline. Error: red (#B3261E) outline with red message under the field. Locked until a time is chosen.
- **Summary line**: above the submit button, flat text showing the chosen service, day, time and duration.
- **Submit button**: bottom of card 3, plum fill, white text "Request booking". Hover: darker plum (#44203A). Disabled: pale grey until the form is complete. Sending: label "Sending…" and not pressable.
- **Confirmation panel**: replaces the cards after success, white raised, green (#2E7D4F) tick, shows the booking details and the status "Requested", and a "Book another" button in plum outline.
- **Failure notice**: red-tinted banner above the button when sending fails or the slot was just taken, showing the reason.

## 3. How it is used
- Click or tap a service row: selects it and unlocks the day strip.
- Click or tap a day: selects it and shows its time slots for that service.
- Click or tap a free time slot: selects it and unlocks the contact form.
- Click or tap a selected service, day or slot again: nothing changes.
- Click or tap a different choice: replaces the choice; changing the service or day clears the chosen time.
- Type in Name, Phone, Email: fills the field; errors show when leaving the field.
- Press Tab and Enter or Space: reach and choose any option with the keyboard.
- Click or tap "Request booking": validates and sends; on success shows the confirmation.
- Click or tap "Book another": clears everything and returns to the service list.

## 4. Scope
One loop: choose service, day, time, enter contact details, submit, see confirmation. Left out: stylist choice, payments, products, loyalty.

## 5. Things and their states
- **Service**: name, duration in minutes. Fixed.
- **Time slot**: date, start time, state free or taken. Free becomes taken when a booking is requested for it.
- **Booking**: service, slot, client name, phone, email, status. Starts **requested** on submit; staff (outside the interface) move it to **confirmed**.

## 6. Rules
- A slot is offered only if the service's full duration fits before closing; otherwise it is not shown as free.
- Only free slots can be selected; taken slots ignore clicks.
- Steps unlock in order: service, day, time, details; locked steps ignore clicks.
- Name is required, at least 2 characters; otherwise an error shows and nothing is sent.
- Phone is required, 7–15 digits (spaces, +, dashes allowed); otherwise refused with an error.
- Email is required and must look like an address; otherwise refused with an error.
- Only dates from today to 13 days ahead are offered; past times today are taken.
- If the chosen slot was taken meanwhile, the submit is refused, the failure notice appears and the time list refreshes.
- Double-pressing submit creates only one booking.
- A new booking has status requested, and the confirmation shows it as "Requested".
- The page never shows a booking as confirmed to the client until staff confirm it.