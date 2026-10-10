# A booking page for a hair salon

## 1. People and their journey

**Client** (the only role in the interface): a person who wants a hair appointment and does not want to phone.
- Needs to see: the services with durations, open times, and whether the request went through.
- Decides: which service, which day, which time, and what contact details to give.
- Path: arrives, picks a service, picks a day, picks a time, enters name, phone and email, submits, sees the confirmation screen with status "Requested".

Salon staff, outside the interface, change a booking from requested to confirmed. They get no screens here.

## 2. How it looks

A single-column, light, friendly booking form, like a simple appointment-booking widget: stacked numbered steps on a warm white page, with one primary button at the foot.

- **Page background**: flat warm off-white (#FAF6F2), filling the screen, with generous margins.
- **Header**: top, flat white band with the salon booking title in dark charcoal (#2B2B2B) and one line "Book your appointment".
- **Content card**: centred, white (#FFFFFF), raised with a soft shadow, 640px wide at most, full width on phones.
- **Step headings**: numbered 1 to 4 in charcoal bold: Service, Day, Time, Your details. A step turns muted grey (#9A9A9A) until the previous step is complete.
- **Service option**: stacked rows, outlined in light grey (#D9D2CB), showing name left and duration right ("45 min"). Hover: background #F3ECE6. Selected: dusty-rose (#C77D8E) outline and pale rose fill (#F8E6EA).
- **Day picker**: horizontal row of day buttons showing weekday and date, outlined grey. Selected: filled dusty rose with white text. Days with no free times: faded, unclickable.
- **Time slot**: grid of small outlined buttons showing the start time. Selected: filled dusty rose, white text. Taken or past: faded grey with strikethrough, unclickable.
- **Empty times message**: replaces the grid when the day has no slots: "No times left on this day."
- **Details fields**: Name, Phone, Email, stacked, white, grey outline. Focus: dusty-rose outline. Invalid after leaving the field: red (#C0392B) outline with a short message below.
- **Summary line**: above the button, small grey text naming service, date, time and end time. Hidden until a time is chosen.
- **Book button**: full-width, flat dusty rose, white text "Request booking". Disabled (light grey) until everything is valid. Pressed: darker rose (#A9606F). While submitting: shows "Sending…" and is disabled.
- **Error banner**: above the button, pale red fill, red text, shown if sending fails or the slot was just taken.
- **Confirmation panel**: replaces the form, with a green check, the booking summary and a "Requested" badge in amber (#E0A030). A "Confirmed" badge is green (#3E8E5A). Below it, a "Book another" link.

## 3. How it is used

- Click or tap a service row: selects it and opens the day step. Tapping another row switches the selection.
- Click or tap a day button: selects the day and shows its free times for that service.
- Click or tap a time slot: selects it and shows the summary.
- Change service after choosing a time: the time is cleared and the slots are recalculated.
- Type in the name, phone and email fields: validated when the field is left.
- Click or tap "Request booking": submits and shows the confirmation panel.
- Press Tab and Enter or Space: reach and choose any option by keyboard.
- Click "Book another": clears everything and returns to step 1.

## 4. Scope

One loop: choose a service, a day and a time, give contact details, submit, see the confirmation with status Requested. There is no payment, stylist choice, account, loyalty or product sales.

## 5. Things and their states

- **Service**: name, duration in minutes. It has no states.
- **Time slot**: date, start time, and length matched to the service. States: open, booked. It becomes booked when a booking is made on it.
- **Booking**: service, slot, client name, phone, email, created time. States: requested (on submit), then confirmed (by salon staff, outside the interface).

## 6. Rules

- A service must be chosen before days appear. Otherwise the later steps stay muted and unclickable.
- Only open slots can be chosen. A booked slot ignores clicks.
- A slot is offered only if the service fits before closing and does not overlap a booked slot.
- Past times are never offered.
- Name is required, at most 80 characters. Empty is refused with a message.
- Phone is required and must hold 7–15 digits. Spaces, plus signs and dashes are allowed. Otherwise refused with a message.
- Email is required and must look like an address. Otherwise refused with a message.
- The button stays disabled until service, slot and all fields are valid.
- If the slot was taken in the meantime, the booking is refused, the error banner appears, and the slot list refreshes.
- Double submits are ignored while sending.
- Every new booking starts as requested and holds its slot immediately.
- Only staff, outside the interface, can set confirmed. The client cannot.
- Clients cannot cancel or edit in this page.