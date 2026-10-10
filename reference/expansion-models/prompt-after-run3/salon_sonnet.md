# A booking page for a hair salon

## 1. People and their journey

**Client** (the only role in the interface): a person who wants a hair appointment without phoning.
- Needs to see: services with durations, and open times.
- Decides: which service, which day and time, and which contact details to give.
- Path: arrives, picks a service, picks a day, picks a time slot, enters name, phone and email, submits, and sees a confirmation saying the booking is requested.

Salon staff, outside the interface, change a booking from requested to confirmed. They get no screens here.

## 2. How it looks

A single, calm, vertical booking page in the manner of a simple appointment form: a warm white background, soft rose accents, and rounded cards on one centred column.

- **Page background**: flat warm white (#FAF7F5) filling the whole window, with the content column centred about 640px wide.
- **Header**: top of the column, flat, shows the salon page title "Book an appointment" in charcoal (#2B2B2B) with a one-line prompt beneath in grey (#6B6B6B).
- **Step markers**: below the header, three numbered circles (Service, Time, Details). Current is filled rose (#C2577A) with white number; done is rose with a tick; upcoming is outlined grey.
- **Service list**: a stack of cards, white, outlined light grey (#E3DDD9), each showing the service name and the duration in minutes. Hover: outline turns rose. Selected: rose outline 2px with pale rose fill (#FBE9EF) and a tick. Pressed: slightly darker fill.
- **Date strip**: a row of day buttons for the next 14 days, each showing weekday and date. Today carries a small dot. Selected: filled rose with white text. A day with no free slots: greyed text, not clickable.
- **Time slot grid**: a grid of pill buttons showing start times, white with grey outline. Hover: rose outline. Selected: filled rose, white text. Taken or past: grey fill (#EEEAE7), grey text, struck through, not clickable. Disabled until a service and a day are chosen.
- **Empty-times message**: replaces the grid when the day has no free slots, grey text.
- **Details form**: white raised card with a soft shadow, fields for Name, Phone and Email with labels above. Focused field: rose outline. Invalid field: red (#C0392B) outline with a red message beneath.
- **Summary line**: above the submit button, shows the chosen service, date, time and duration, in charcoal.
- **Submit button**: full-width rose button with white text "Request booking". Hover: darker rose (#A8446A). Disabled: pale rose, until the form is valid. While sending: shows a spinner and ignores clicks.
- **Error banner**: above the button, pale red fill with red text, appears if sending fails or the slot was just taken.
- **Confirmation card**: replaces the form, white with a green (#2E7D5B) tick, showing the booking details and a "Requested" badge in amber (#D9922B). A "Book another" text link sits below.

## 3. How it is used

- Click or tap a service card: selects it and moves to choosing a time. Clicking another card replaces the choice.
- Click or tap a day button: selects that day and loads its slots.
- Click or tap an open time slot: selects it. Clicking the selected slot again deselects it.
- Type in the Name, Phone and Email fields: fills the details; errors appear once the field loses focus.
- Press Tab and Enter: Tab moves between controls; Enter or Space activates the focused button.
- Click or tap "Request booking": submits and shows the confirmation card.
- Click or tap a step marker that is done: returns to that step with choices kept.
- Click or tap "Book another": clears everything and returns to the service list.

## 4. Scope

One loop: choose a service, a day and a free slot, give contact details, submit, and see a requested booking. Left out: staff and stylist choice, payments, deposits, products and loyalty. Cancelling and changing bookings are not on the page; clients phone the salon for that.

## 5. Things and their states

- **Service**: name, duration in minutes. Fixed, no states.
- **Time slot**: date, start time, linked to the service length. States: open, then taken once a booking holds it. A past slot is not open.
- **Booking**: service, slot, client name, phone, email, created time. States: requested (on submit), then confirmed (by salon staff, outside the interface).

## 6. Rules

- A booking needs a service, a slot, a name, a phone and an email; otherwise submit stays disabled.
- Name must be at least 2 characters; otherwise the field shows an error.
- Phone must have 7–15 digits, allowing spaces, plus and dashes; otherwise an error shows.
- Email must have a valid format; otherwise an error shows.
- Only open slots can be chosen; taken and past slots ignore clicks.
- Slots must be long enough for the chosen service's duration; slots that are too short are shown as taken.
- Dates run from today to 14 days ahead; others cannot be chosen.
- Changing the service after picking a time clears the time if it no longer fits.
- A slot is held by the first submitted booking; a second attempt is refused with "That time was just taken, please choose another", and the form keeps the details.
- A new booking always starts as requested.
- Double clicks on submit create one booking only.
- A requested booking holds its slot so no one else can book it.