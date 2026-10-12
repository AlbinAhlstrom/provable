# A booking page for a hair salon

## 1. People and their journey

**Client** (the only role in the interface). Wants to see what the salon offers, find a free time and book without phoning.

Path: arrives on the page, picks a service, picks a day, picks a free time slot, enters name, phone and email, submits, and sees a confirmation message with the booking summary and its status.

Salon staff, who confirm requested bookings, are outside the interface and have no screens here.

## 2. How it looks

A single-column, light, friendly booking form in the style of a simple appointment scheduler, with numbered steps stacked top to bottom.

- **Page background**: flat warm off-white (#FAF6F1), full width, content centred in a 640px column.
- **Header**: top of the column, flat; salon-style title "A booking page for a hair salon" in deep charcoal (#2B2B2B) with a one-line subtitle in grey (#6B6B6B).
- **Step 1 heading "Choose a service"**: charcoal text with a plum (#7A3E65) number badge.
- **Service cards**: a vertical list, white, outlined in light grey (#DDD3CA), showing service name and duration in minutes. Hover: outline turns plum. Selected: plum outline, pale plum fill (#F3E6EE), plum tick at right.
- **Step 2 heading "Choose a day"**: same style, shown greyed (#B5ADA6) until a service is selected.
- **Day strip**: a row of the next 14 days, scrolling sideways; each day is a white outlined chip with weekday and date. Selected: plum fill, white text. Closed or fully booked days: grey text, striped-free flat grey fill (#EEE9E4), not pressable.
- **Step 3 heading "Choose a time"**: same style, greyed until a day is chosen.
- **Time slot grid**: three columns of small white outlined buttons showing start times. Selected: plum fill, white text. Taken or too short for the service: grey fill, struck-through text, not pressable.
- **No-times message**: grey text in place of the grid when a day has no free slot.
- **Step 4 heading "Your details"**: same style, greyed until a slot is chosen.
- **Details form**: fields for name, phone and email, white, outlined grey, labelled above. Focus: plum outline. Error: red (#B3261E) outline with red message below.
- **Booking summary**: pale plum flat box above the button showing service, day, time and duration.
- **Book button**: full width, flat plum with white text, "Request booking". Pressed: darker plum (#5E2E4D). Disabled until all is valid: grey (#CFC7C0). While sending: label "Sending…".
- **Confirmation panel**: replaces the form; white, raised with soft shadow, green (#2E7D4F) tick, summary, and a status pill "Requested" (amber #C77D00 fill) or "Confirmed" (green fill).
- **Failure banner**: red-tinted strip above the button when submission fails, with the message.

## 3. How it is used

- Click or tap a service card: selects it and enables day choice; tapping another switches the choice.
- Click or tap a day chip: selects it and loads that day's slots; swipe or scroll the strip sideways.
- Click or tap a free time slot: selects it; tapping another switches the choice.
- Type in name, phone and email: fields validate when left.
- Click or tap "Request booking": submits and shows the confirmation panel.
- Click or tap "Book another" on the confirmation: returns to an empty step 1.
- Click or tap a step heading already completed: scrolls back to it for changing.

## 4. Scope

One loop: choose service, day and time, give contact details, submit, see the confirmation. Staff, stylist choice, payments, products and loyalty are excluded. The form asks only for name, phone and email.

## 5. Things and their states

- **Service**: name, duration in minutes. Fixed.
- **Time slot**: date, start time. States: free → taken (when a booking is made on it); stays taken.
- **Booking**: service, slot, client name, phone, email. States: requested (on submit) → confirmed (by salon staff, outside the interface).

## 6. Rules

- A service must be chosen before a day; otherwise day and time stay disabled.
- A day must be chosen before a time; likewise.
- Changing the service clears the chosen time, since durations differ.
- A slot is offered only if the whole service duration fits before closing and before any taken slot.
- Taken slots cannot be selected; presses are ignored.
- Days in the past are not shown.
- Name is required, at most 80 characters.
- Phone is required, digits, spaces, + and - only, 7–15 digits.
- Email is required and must be a valid address.
- Invalid fields block submission and show a red message.
- If the slot was taken meanwhile, submission is refused, the slot greys out, and the client is asked to pick another time; details are kept.
- A new booking starts as requested.
- Only one booking per slot; a double submit creates one booking.
- A confirmed status is shown as it stands; clients cannot change it.