# A booking page for a hair salon

## 1. People and their journey
**Client** (the only role in the interface): wants to see which times are free and book a service without phoning.
Path: arrives, picks a service, picks a day, picks a free time slot, enters name, phone and email, submits, sees a confirmation of the request with its status.
Salon staff, outside the interface, change a booking from requested to confirmed.

## 2. How it looks
A single-column, light and friendly booking form, like a simple appointment-booking widget: stacked numbered steps on one white card, with rounded corners.

- **Page background**: flat warm off-white (#FAF6F2) filling the whole window, with the card centred on it.
- **Header**: top of card, flat; salon-style title "Book an appointment" in charcoal (#2B2B2B) with a short line "Choose a service, a time and your details".
- **Service list**: step 1, outlined cards stacked. Each shows name, duration in minutes and price-free text. Hover: border rose (#C45B7A). Selected: rose fill with white text. Pressed: darker rose (#A9455F).
- **Day picker**: step 2, a row of day buttons (next 14 days) with weekday and date. Outlined grey (#D8D0C8). Selected: rose fill. Day with no free slots: greyed, struck through, unavailable. Disabled until a service is chosen.
- **Time slot grid**: step 3, wrapped grid of outlined time buttons. Free: white with grey outline. Selected: rose fill, white text. Taken: light grey fill (#EEE8E2), grey text, unavailable. Empty day shows "No times left on this day".
- **Contact form**: step 4, fields for name, phone, email, each with a label above, a sunken light-grey field, and a rose outline when focused. Invalid field: red (#B3261E) outline with a message beneath.
- **Summary strip**: above the submit button, flat pale rose (#F7E3E9), showing chosen service, day, time and end time.
- **Submit button**: bottom of card, full width, raised rose (#C45B7A), white text "Request booking". Disabled grey until everything is valid. While sending: shows "Sending…". Failed: red message above it.
- **Confirmation panel**: replaces the form after success, green (#2E7D4F) tick, booking details, and a status badge: "Requested" amber (#E0A526) or "Confirmed" green (#2E7D4F). A "Book another" outlined button sits below.

## 3. How it is used
- Click or tap a service: selects it and loads the days; selecting another replaces it.
- Click or tap a day: selects it and shows its slots; clears any chosen time.
- Click or tap a free time slot: selects it; tapping it again deselects it.
- Tapping a taken slot or an unavailable day: does nothing.
- Type in name, phone and email: fields validate when left.
- Click or tap Request booking: submits and shows the confirmation panel.
- Click or tap Book another: returns to an empty form.

## 4. Scope
One loop: choose service, day, slot, give contact details, submit, see status. Left out: staff rosters and stylist choice, payments and deposits, products, loyalty.

## 5. Things and their states
- **Service**: name, duration in minutes. No states.
- **Time slot**: start time, day. States: free, taken (when a booking holds it).
- **Booking**: service, slot, client name, phone, email, status. States: requested (on submit) → confirmed (by salon staff, outside the interface).

## 6. Rules
- A service, a day and a free slot must be chosen before submitting; otherwise the button stays disabled.
- Name is required, at least 2 characters; otherwise refused with a message.
- Phone is required, 7–15 digits, spaces, + and dashes allowed; otherwise refused.
- Email is required and must be a valid address; otherwise refused.
- A slot must be long enough for the service duration; slots that would not fit are shown taken.
- Past times and days are never offered.
- A requested booking holds its slot; if it was taken meanwhile, submit is refused with "That time was just taken, please choose another", and slots refresh.
- Each new booking starts as requested.
- Clients cannot change a booking to confirmed.
- Double submit presses are ignored while sending.