# Hair Salon Booking Page

## 1. People and their journey

**Client** (the only role in the interface). Needs to see the services with their durations and the free appointment times, then send a booking request with contact details.

Path: opens the page → chooses a service → chooses a date and time → enters name and phone (email optional) → submits → sees the booking as Requested.

*Outside the interface:* salon staff review requests and mark them Confirmed. They have no screens here.

## 2. How it looks

A single calm, plain web page that reads top to bottom like a simple online form. Light surfaces, soft salon colours, one accent colour, and no decoration beyond what is listed.

- **Page background:** full-width flat ivory (#F7F3EE), behind everything.
- **Header bar:** flat warm white (#FFFFFF) across the top, with a 1px taupe (#CBBFB3) line beneath; shows the salon name in charcoal (#3A3331) text at left.
- **Step 1 "Service" card:** white (#FFFFFF) raised card with a soft grey shadow, titled "Service" in charcoal; lists each service as a row with its name and duration in minutes (e.g. "Cut and blow-dry · 60 min").
- **Service row, default:** no fill, charcoal text, 1px taupe outline.
- **Service row, hovered or focused:** pale rose tint (#F4E4E5) fill.
- **Service row, selected:** filled dusty rose (#A8566B) with white text and a white tick at right.
- **Step 2 "Time" card:** white raised card titled "Time", directly below Step 1.
- **Date chips:** a horizontal row of outlined chips showing day and date; available date has taupe outline and charcoal text; date with no free times has grey (#E6E2DE) fill and grey text, not selectable; selected date has dusty rose fill with white text.
- **Time slot chips:** grid of outlined chips showing start time; free slot has taupe outline and charcoal text; taken slot has grey (#E6E2DE) fill with struck-through grey text; selected slot has dusty rose fill with white text.
- **Step 3 "Your details" card:** white raised card titled "Your details", below Step 2.
- **Input fields (Name, Phone, Email):** white with 1px taupe outline, 44px high, charcoal text, placeholder in light grey (#9A918A); focused field has a 2px dusty rose outline; invalid field has a 2px red (#B3261E) outline and a red message beneath.
- **Name and Phone labels:** charcoal with "required" marked by a dusty rose asterisk; Email label has "optional" in grey.
- **Summary strip:** flat pale sand (#EFE7DE) bar fixed to the bottom of the screen; shows "Service · Date · Time" when chosen, or "Choose a service and a time" in grey text otherwise.
- **Request booking button:** full-width at the foot of Step 3, deep rose (#8E4659) with white text; disabled state is grey (#CFC7BF) with grey text until required fields are complete; pressed state darker (#6E3345); waiting state shows the words "Sending…" with the same fill.
- **Confirmation card:** replaces Steps 1–3 and the button on success; white raised card with heading "Booking request sent", the service, date and time, and a status badge.
- **Status badge, Requested:** amber (#E0A030) fill with charcoal text.
- **Status badge, Confirmed:** green (#3E8E5A) fill with white text.
- **Error banner:** pale red (#F9E3E1) strip above the button with red text, shown only when a submission is refused.

## 3. How it is used

- **Click (mouse) or tap (touch) a service row:** selects it, clears any previously chosen time that no longer fits its duration, and updates the summary strip.
- **Click or tap a date chip:** shows that day's free time slots in the Time card.
- **Click or tap a free time slot:** selects it and updates the summary strip; a taken slot ignores the click.
- **Click or tap a greyed date chip:** nothing happens.
- **Click or tap a field, or press Tab to reach it:** moves focus into it, showing the focus outline.
- **Type in Name, Phone or Email:** fills the field; leaving a required field empty or invalid shows its red message on leaving it.
- **Press Tab or Enter in the form:** moves to the next field; Enter on the last field submits if the button is enabled.
- **Click or tap Request booking:** sends the request; on success the confirmation card replaces the form.
- **Click or tap Request booking while it is disabled:** nothing happens; the first missing field is outlined in red.
- **Click or tap Request booking twice quickly:** sends one request only.
- **Scroll (mouse wheel, trackpad or swipe):** moves the page; the summary strip stays at the bottom.
- **Resize the window or rotate a phone:** the cards stack in one column; the time grid reflows to fit.

## 4. Scope

Client opens the page, picks a service, picks a date and free time, gives name and phone (and optionally email), and submits a booking request. The page then shows the request as Requested. Confirmation by salon staff happens outside this page.

Asks only for name (required), phone (required) and email (optional). Nothing else.

## 5. Things and their states

- **Service:** holds name and duration in minutes. Listed for the client to choose; no state changes.
- **Time slot:** holds start time, date and length of the chosen service it must fit. States: free, taken. A slot becomes taken when a booking uses it. Taken is final on this page.
- **Booking:** holds service, date and time, name, phone, optional email. States: Requested → Confirmed. Created as Requested when the client submits; moves to Confirmed only when staff confirm it outside the interface.

## 6. Rules

- A date with no free times cannot be selected; the click is ignored.
- A time slot is offered only if the whole service duration fits free before the next booked time; otherwise it is not offered.
- A taken slot cannot be selected; the click is ignored.
- Changing the service clears the chosen time if it no longer fits the new duration; the client must pick again.
- Past dates and times are not shown and cannot be selected.
- Request booking stays disabled until a service, a date, a time, a name and a phone number are all given; a click on it is ignored.
- Name must not be blank; a blank name is refused with a red message on that field.
- Phone may contain only digits, spaces, +, -, and parentheses, with 7 to 15 digits; otherwise refused with a red message.
- Email, if entered, must contain one @ with a dot after it; otherwise refused with a red message. Blank email is accepted.
- If the chosen slot was taken before submission, the request is refused, the slot turns grey, and the error banner says that time has just been taken; the client must choose another.
- A refused submission changes nothing: entered details, chosen service, date and time stay as they were.
- A successful submission creates one booking with status Requested; repeated clicks create no further bookings.
- Only staff outside the interface can change a booking from Requested to Confirmed; the page never sets Confirmed.
- The page never takes payment or a deposit.