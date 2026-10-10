# Hair Salon Booking Page

## 1. People and their journey

- **Salon client:** a person who wants a hair salon service. They arrive, pick a service, a day and a time, give their name, phone and email, and send a booking request. They are done when they see the request marked "Requested".
- *Outside the interface:* salon staff, who review each request and mark it "Confirmed". They have no screens in this product.

## 2. How it looks

A single plain web page in the style of a simple online appointment form: a stacked, top-to-bottom sequence of steps on a calm, light background, with a clear, uncluttered look that a client can read in one scroll.

- **Page background:** flat pale warm grey (#F4F2EF), covers the whole screen.
- **Page heading:** flat text on the background at the top, dark charcoal (#2B2B2B), reads "Book an appointment".
- **Step 1 heading:** dark charcoal text, reads "1. Choose a service".
- **Service cards:** a vertical stack of raised white cards with soft shadow, each showing the service name in charcoal and its duration in grey (e.g. "60 min"). Pressed: shadow removed, card sinks slightly. Selected: 2 px dark teal (#1F6F6B) outline and pale teal fill (#E3F1F0).
- **Step 2 heading:** reads "2. Choose a day".
- **Day tiles:** a single row of seven outlined white tiles, each showing weekday above date, for the next 14 days (scrolls sideways for the rest). Selected: solid dark teal fill with white text. Day with no open times for the chosen service: light grey text, not selectable.
- **Step 3 heading:** reads "3. Choose a time".
- **Time panel:** a flat, slightly sunken pale panel holding time buttons in a grid of three per row. Open time: white fill, 1 px dark teal outline, charcoal text. Selected: solid dark teal fill, white text. Taken or past time: light grey fill, grey text, not selectable.
- **Step 4 heading:** reads "4. Your details".
- **Details panel:** a raised white panel with three labelled fields stacked: "Name", "Phone", "Email". Field: white with 1 px grey outline; focused: 2 px dark teal outline. Invalid field: red (#B3261E) outline with red message beneath.
- **Request button:** full-width solid dark teal, white text "Request booking". Disabled until all steps are complete: light grey fill, grey text. Pressed: darker teal (#18524F).
- **Confirmation panel:** replaces the form in the same place; raised white card showing service, day, time and a status badge reading "Requested" in amber (#F2A900) fill with charcoal text. Title reads "Your request has been sent".

## 3. How it is used

- **Tap or click a service card:** selects it, clears any earlier day and time choice, and shows that service's open days.
- **Tap or click a day tile:** selects that day and shows its open times; clears any earlier time choice.
- **Tap or click an open time button:** selects that time; the details panel becomes active.
- **Tap or click a selected service, day or time again:** does nothing; the choice stays.
- **Tap a field or click into it, then type:** enters name, phone or email; the field is focused.
- **Tap or click "Request booking":** sends the request when enabled and shows the confirmation panel with status "Requested".
- **Tap or click "Request booking" while disabled:** does nothing.
- **Tap or click a red-outlined field:** focuses it so the client can correct it.

## 4. Scope

The client chooses a service, then a day, then a time, enters name, phone and email, and sends a request. They see it marked "Requested". Choices offered: which service (with its duration), which of the next 14 days, and which open time. No accounts, no payment, no staff choice.

## 5. Things and their states

- **Service:** name, duration in minutes. Fixed; not changed by the client.
- **Time slot:** date, start time, length set by the chosen service. Moves from *open* to *taken* when a booking for it is made, and to *past* as its start time passes.
- **Booking request:** service, date, start time, name, phone, email, status. Created as *requested* when the client sends it. Moves to *confirmed* only when salon staff confirm it outside this page.

## 6. Rules

1. A service must be chosen before a day can be picked; a day before a time; a time before details are entered. Out-of-order taps are ignored.
2. A time slot already taken or past cannot be selected; the tap is ignored.
3. A time is offered only if enough consecutive open time follows it to cover the chosen service's duration; otherwise it is not shown as open.
4. Changing the service clears the day and time; changing the day clears the time.
5. "Request booking" stays disabled until service, day, time, name, phone and email are all filled in and valid.
6. Name must not be empty; phone must contain at least 7 digits; email must contain "@" followed by a domain with a dot. An invalid field is outlined red with a message and nothing is sent.
7. Sending a request creates it with status "Requested" and marks its time slot taken for everyone else at once.
8. A client cannot change status to "Confirmed"; the status control does not appear on this page.
9. Clients cannot cancel or change a request on this page; a request already sent stays as it is.
10. Days with no open time for the chosen service cannot be selected; the tap is ignored.