# Hair Salon Booking Page: Product & Behavioral Specification

## 1. Persona & Value Journey
**Salon Client** (sole user): wants to see what the salon offers, how long each service takes, and when it is free, then book without phoning.
Journey: open page → pick a service → pick a day and an open time → enter name, phone, email, optional note → submit → see a "Requested" confirmation with booking summary.

*Salon staff (outside the interface) confirm requests; they have no screens here.*

## 2. Presentation & Interaction
The page looks like a familiar salon booking page, laid out as one scrolling page in three numbered steps:
1. **Service list**: cards showing name, duration (e.g. "45 min") and a short description. Tapping a card selects it and highlights it.
2. **Time picker**: a horizontal strip of days, with a grid of time "pills" for the chosen day. Open times are tappable. Taken or past times are greyed out. Times are shown only once a service is chosen.
3. **Your details**: a short form with name, phone, email and note. A sticky summary bar shows "Cut & Style · Tue 14 May · 10:30 · 45 min" and a **Request booking** button.

After submitting, a confirmation panel shows the booking details with a status badge: amber **Requested** or green **Confirmed**.

Tone: warm, calm, uncluttered, with soft neutrals, one accent colour, generous spacing and friendly copy. It should work well on a phone.

## 3. MVP Scope
The page covers browsing services, viewing open times, submitting a request and seeing its status. Staff rosters, payments, products and loyalty are out of scope.

## 4. Core Concepts
- **Service**: name, description, duration in minutes.
- **Time Slot**: start time on a date. It is either open or taken.
- **Booking**: service, slot, client contact details, optional note, status.
  - Status moves one way: **Requested → Confirmed** (confirmation is done by staff).

## 5. Business Rules
- A booking requires exactly one service and one time slot.
- The client's name is required and cannot be blank.
- A phone number or an email is required. Any value given must be well-formed.
- The note is optional and limited to 500 characters.
- Only open slots can be chosen. A slot in the past cannot be booked.
- The slot must have enough continuous open time to cover the service's full duration.
- A slot is held by at most one booking. Requested and Confirmed bookings both make the slot taken.
- If the slot is taken while the client is filling in the form, submission is refused. The client is told "That time was just taken" and asked to choose another. No booking is created.
- Every new booking starts as Requested.
- Only Requested bookings can become Confirmed. Confirmed is final within this scope.
- When a submission is refused, nothing is saved, the client's entries are kept, and each problem is shown next to its field.