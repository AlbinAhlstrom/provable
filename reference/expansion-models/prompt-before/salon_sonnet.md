# A Booking Page for a Hair Salon

## 1. Persona and Journey
**Salon client** is the only person using the page. They want to see what the salon offers, find a time that suits them, and book without phoning.
- Sees: services with durations, and open times.
- Decides: which service, which day and time.
- Accomplishes: submits their name and contact details and gets a clear confirmation that the request was received.

*Salon staff (outside the interface)* review requests and confirm them. They have no screens or controls here.

## 2. Presentation and Interaction
A single, simple page that reads top to bottom in three steps:
1. **Choose a service:** tappable cards showing name and duration (e.g. "Cut, 45 min").
2. **Choose a time:** a familiar week strip or month calendar. Picking a day shows its open times as buttons, and times already taken are absent or greyed out. The selected time is highlighted.
3. **Your details:** a short form with name, phone, email and an optional note. A summary of the choices sits beside or above the "Request booking" button.

After submission the page shows a confirmation summary with a status badge reading **Requested**. The tone is clean, warm and reassuring: soft neutral colours, one accent colour for selections and the main button, large touch-friendly controls, and a layout that works well on phones.

## 3. Scope
The loop is: pick service, pick slot, submit details, see the request acknowledged. There are no accounts, payments, stylist choice or extras.

## 4. Core Concepts
- **Service:** name and duration.
- **Time slot:** a start time and the length of time it covers, either open or taken.
- **Booking:** the chosen service, the chosen slot, the client's name, contact details and optional note, and a status.

**Booking status:** *Requested* on submission, then *Confirmed* once the salon accepts it. The page shows the current status to the client.

A slot is open until a booking holds it. It becomes taken when a booking requests it.

## 5. Business Rules
- A booking must have exactly one service and one slot.
- Only open slots can be selected or submitted.
- A slot must be long enough for the chosen service's duration. Slots too short are not offered for that service.
- Slots in the past cannot be booked.
- A slot can belong to at most one active booking. If someone else takes it first, the submission is rejected, no booking is created, and the client is asked to pick another time while their details stay filled in.
- Name is required. At least one valid contact method (phone or email) is required.
- Invalid submissions are rejected with plain messages next to the affected fields, and nothing is saved.
- A new booking always starts as *Requested*.
- Status moves only *Requested* → *Confirmed*, never backwards or skipping, and confirmation is done by the salon outside this interface.
- Submitting twice in quick succession creates only one booking.