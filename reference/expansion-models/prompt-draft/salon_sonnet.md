# A booking page for a hair salon

## 1. People and their journey

**Client** (the only role in the interface): a person who wants a haircut or other salon service without phoning.
- Needs to see: services with durations, open times, and whether their request went through.
- Decides: which service, which day, which time, and what contact details to give.
- Journey: arrives, picks a service, picks a day, picks a time, enters name, phone and email, submits, and sees a confirmation of the request with its status.

Salon staff, outside the interface, change a booking from requested to confirmed. They get no screens here.

## 2. How it looks

A single, calm, vertical form-style page, like a simple appointment-booking widget: white card on a soft cream background, with sage green as the accent colour.

- Page background: flat warm cream (#FAF6F0), filling the whole window behind the card.
- Header: top of the card, flat white, salon-style title "Book an appointment" in charcoal (#2B2B2B) with a one-line subtitle in grey (#6B6B6B).
- Booking card: centred, white, raised with a soft shadow, maximum 640px wide; fills the screen width on phones.
- Step labels: small numbered labels "1 Service", "2 Day", "3 Time", "4 Your details" in charcoal; the current step is sage (#5E8C6A), completed steps show a sage tick.
- Service list: one outlined option per service, showing name and duration, such as "45 min". Hover is light sage tint; selected is a sage fill with white text; keyboard focus shows a dark outline.
- Day picker: a horizontal row of the next 14 days, each an outlined chip with weekday and date. Selected is sage fill with white text; a day with no free times is greyed and unclickable. Disabled until a service is chosen.
- Time slot grid: wrapped outlined buttons with times such as "10:30". Available is white with a sage outline; hover is a sage tint; selected is sage fill with white text; taken is light grey with strikethrough and unclickable.
- Empty-times note: grey text in place of the grid when the chosen day has no free times: "No times left on this day."
- Details fields: stacked inputs for Name, Phone, Email and an optional Note, each with a label above and a grey outline. Focused is a sage outline; invalid is a red (#B3402F) outline with red message below.
- Summary strip: above the submit button, light sage (#E8F0EA) flat strip showing chosen service, day, time and duration. It is hidden until a service is chosen.
- Submit button: full width at the bottom of the card, sage fill, white text "Request booking". Disabled is pale grey until all steps are complete; pressed is darker sage; while sending it shows "Sending…".
- Confirmation panel: replaces the form after success, white with a sage tick. It shows the booking summary and a status badge: "Requested" in amber (#C98A1B) or "Confirmed" in green (#2E7D4F). A "Book another" link sits below.
- Error banner: at the top of the card, flat pale red with red text, shown when submission fails or the time was just taken.

## 3. How it is used

- Click or tap a service: selects it and enables the day picker; clicking another service replaces the choice.
- Click or tap a day: selects it and loads its time slots; changing the day clears any chosen time.
- Click or tap an available time: selects it; clicking another time moves the selection.
- Type in the Name, Phone, Email and Note fields.
- Press Tab and Enter: Tab moves between options and fields; Enter or Space picks the focused option.
- Click or tap "Request booking": validates, creates the booking, and shows the confirmation.
- Click or tap "Book another": clears everything and returns to step 1.
- Click or tap a taken or empty day: nothing happens.

## 4. Scope

The loop: choose a service, a day and a time, give contact details, submit, and see the booking as requested. Left out: stylist choice, payments or deposits, product sales, loyalty, accounts, and cancelling or rescheduling in the page. The form asks only for name, phone, email and an optional note.

## 5. Things and their states

- **Service**: name, duration in minutes. It has no states.
- **Time slot**: date, start time, and the service it fits by duration. States: available, then taken once a booking holds it.
- **Booking**: service, slot, client name, phone, email, optional note, created time. States: requested (on submission), then confirmed (set by salon staff outside the page).

## 6. Rules

- A service must be chosen before a day can be picked; otherwise the day picker is disabled.
- A day must be chosen before times appear.
- A time slot must be long enough for the service's duration; otherwise it shows as taken.
- Only available slots can be selected; taken slots ignore clicks.
- Name is required and must be non-empty; otherwise "Please enter your name".
- Phone is required and must hold at least 7 digits; otherwise "Please enter a valid phone number".
- Email is required and must look like an address; otherwise "Please enter a valid email".
- The note is optional, at most 300 characters; extra typing is ignored.
- Submit is refused until service, day, time and valid details are all present; the first invalid field is focused.
- Days offered are today and the next 13 days; past times on today are not shown.
- A new booking starts as requested.
- A slot is held as soon as a booking is created; two bookings cannot hold the same slot.
- If the slot was taken meanwhile, submission is refused, the error banner says "That time was just taken. Please pick another.", and the time grid refreshes with the details kept.
- A client cannot confirm their own booking; only staff set confirmed.
- A double click on submit creates only one booking.