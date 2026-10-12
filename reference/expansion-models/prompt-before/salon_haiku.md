# Hair Salon Booking Page

## 1. Personas & Value Journeys

**Client (the audience)**
- Sees the salon's services with their durations and the open appointment time slots.
- Chooses one service and one time slot, then enters contact details to submit a booking request.
- Sees whether the booking is *requested* or *confirmed*.

**Salon staff (outside the interface)**
- Receive booking requests and confirm them through a process outside this page. They have no screens or controls in this product.

## 2. Presentation & Interaction

- Looks like a familiar single-page online booking form: a clean, light page with the salon's name at the top, a short list of services, then a calendar-style or list of time slots, then a contact form and a clear "Request booking" button.
- Selecting a service updates the available slots to fit its duration.
- Selecting a slot highlights it; taken or past slots appear greyed out and cannot be selected.
- Required fields (name, phone or email) are marked; errors appear beside the field in plain language.
- After submission, a status badge shows **Requested** (amber) or **Confirmed** (green), with the chosen service, date, and time repeated for the client's reference.
- Tone: calm, friendly, and reassuring, suited to clients booking a personal appointment.

## 3. MVP Scope

Covers only the single value loop: browse services and slots → choose → enter contact details → submit → see status.

Excluded: staff rosters, stylist choice, payments or deposits, product sales, loyalty features, accounts, and rescheduling or cancellation by the client (not implied by the pitch).

## 4. Core Concepts & States

- **Service**: name, description, duration.
- **Time Slot**: start time and length; either *open* or *taken*.
- **Booking Request**: chosen service, chosen slot, client name, contact identifier (phone or email), optional note; status moves from *Requested* to *Confirmed*.

Status transitions: a new submission is always created as *Requested*. Only the salon's outside process may move it to *Confirmed*.

## 5. Business Rules & Invariants

- **Service required**: a booking needs exactly one service.
- **Slot required**: a booking needs exactly one slot.
- **Slot fits service**: the slot length must be at least the service duration.
- **Slot availability**: a slot can be held by only one non-withdrawn booking; if it is already taken at submission, the request is rejected with a message asking the client to choose another time, and no booking is created.
- **Past times**: slots in the past cannot be selected or submitted.
- **Contact details**: name and at least one contact identifier (phone or email) are required; malformed values are rejected with a field-level message.
- **Initial status**: every new booking starts as *Requested*.
- **Status progression**: *Requested* may become *Confirmed*; *Confirmed* does not revert to *Requested* through this page.
- **Rejected operations**: any invalid submission leaves existing bookings and slots unchanged and shows the reason to the client.