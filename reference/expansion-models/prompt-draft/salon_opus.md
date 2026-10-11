# Hair Salon Booking Page

## 1. People and their journey
**Client** (the only role). Needs to see the services, how long each takes, and which times are free. Decides on one service and one time. Accomplishes a booking request with their contact details.
Path: arrives on the page → picks a service → picks a day → picks a free time → enters name, phone and email → submits → sees a "Requested" confirmation with the booking details → later, returning with the booking reference, sees the status turn to "Confirmed".

*Salon staff (outside the interface): confirm requested bookings. They get no screens or controls here.*

## 2. How it looks
The page is a single scrolling column in three numbered steps, like a familiar salon booking form: a service list, then a week strip with a grid of time buttons, then a contact form, with a summary bar fixed at the bottom. It uses a warm, calm salon look: cream background, deep plum accents, rounded corners.

- **Page background**: flat cream (#FAF6F1) across the whole page; content sits in a centred column 640 px wide, full width on phones with 16 px side margins.
- **Header**: flat plum (#4A2545) band across the top, showing the salon name in white serif type and the subtitle "Book an appointment" in pale pink (#F3D9E5).
- **Step headings**: plum numbered circles (1, 2, 3) with white numerals beside the dark charcoal (#2B2B2B) titles "Choose a service", "Choose a time" and "Your details".
- **Service card**: raised white card with a soft shadow showing the service name, the duration ("45 min") in grey (#6B6B6B), and a one-line description. When selected it gets a 2 px plum outline, a pale pink fill and a plum check mark at the right.
- **Day strip**: a row of seven outlined white day chips showing the weekday and date, with grey arrows at either end. The selected day is solid plum with white text. Closed days are flat grey (#E4E0DC) with struck-through text. The left arrow is greyed out on the current week.
- **Time slot button**: outlined plum pill showing the start time ("10:30"), in rows of four (three on phones). Selected: solid plum, white text. Unavailable: flat grey with grey text, no outline. While pressed it is slightly darker plum.
- **No-slots message**: grey italic line "No free times this day. Try another day." shown in place of the grid when the chosen day has no time that fits.
- **Time step placeholder**: grey line "Choose a service first", shown before a service is picked. The day strip and grid are hidden until then.
- **Form fields**: sunken white boxes with grey 1 px borders for Full name, Phone, Email and Note (optional, three lines). A focused field gets a plum border. A field that failed shows a red (#B3261E) border and a red message beneath it.
- **Summary bar**: raised white bar pinned to the bottom with a top shadow, showing "Service · Day · Time" or "Nothing chosen yet" in grey.
- **Request booking button**: inside the summary bar, solid plum with white text. It is pale plum (#C9B3C5) and unavailable until a service, a time and valid details are given. While sending it reads "Sending…" with a white spinner.
- **Slot-taken banner**: red-outlined pale red (#FBE9E8) box above step 2 reading "That time was just taken. Please choose another." It appears when a submit fails for that reason.
- **Confirmation panel**: replaces steps 1–3 after a successful submit. It is a raised white card with an amber (#C77C02) "Requested" badge, the booking details, the reference code in large monospace, and the line "The salon will confirm shortly."
- **Status check**: below the header, a small outlined box with the field "Booking reference" and a "Check" button. It shows the booking card with an amber "Requested" or green (#2E7D32) "Confirmed" badge, or red "No booking found".

## 3. How it is used
- Click or tap a service card to select it. Selecting another service replaces the choice and clears any chosen time.
- Click or tap a day chip to show that day's time slots. Closed days do nothing.
- Click or tap the arrows (or swipe the day strip on touch) to move a week back or forward, up to four weeks ahead.
- Click or tap a free time button to select it. Tapping the selected time again deselects it. Unavailable times do nothing.
- Type into the name, phone, email and note fields. Each field checks itself when you leave it.
- Click or tap "Request booking" to submit. On success the confirmation panel appears. On failure the message shows and your entries stay.
- Click "Copy" beside the reference code to copy it.
- Type a reference in the status check and press Enter or click "Check" to see that booking's status.
- Click "Book another" on the confirmation panel to return to an empty form.

## 4. Scope
The loop: choose a service → choose a free time that fits its duration → give contact details → submit a request → see it as Requested, later Confirmed via the reference.

Left out: stylist choice and staff rosters, payments and deposits, product sales, loyalty, accounts and logins, cancelling or rescheduling online. The form asks only for name, phone, email and an optional note.

## 5. Things and their states
- **Service**: name, description, duration in minutes. It has no states and is set by the salon.
- **Time slot**: a start time on a day, within opening hours, in 15-minute steps. It is *free* or *taken*. It becomes taken when a booking overlaps it.
- **Booking**: reference code, service, day, start time, end time (start plus duration), name, phone, email, note, and submitted time. It moves from *Requested* (on submit) to *Confirmed* (when staff confirm, outside the interface).

## 6. Rules
- Exactly one service and one start time are needed to submit. Otherwise the button stays unavailable and pressing it does nothing.
- A start time is offered only if the whole service duration fits before closing time.
- A start time is offered only if the whole service duration overlaps no Requested or Confirmed booking.
- Times earlier than now plus 2 hours are shown as unavailable.
- Days more than four weeks ahead cannot be reached. The forward arrow greys out.
- Days the salon is closed are shown as closed and cannot be selected.
- Full name is required, 2–80 characters. Otherwise the message "Please enter your name" appears and the submit is refused.
- Phone is required, 7–15 digits (spaces, +, and dashes allowed). Otherwise the message "Please enter a valid phone number" appears and the submit is refused.
- Email is required and must be shaped like name@domain. Otherwise the message "Please enter a valid email" appears and the submit is refused.
- Note is optional, up to 300 characters. Further typing is ignored.
- If the time becomes taken between choosing and submitting, the submit is refused, the slot-taken banner shows, that time greys out, and the other entries are kept.
- A double click on "Request booking" creates one booking only. Further presses while sending are ignored.
- Every new booking starts as Requested and gets a unique 6-character reference.
- Only salon staff can change a booking to Confirmed. Clients cannot change the status.
- A status check with an unknown reference shows "No booking found" and reveals nothing else.
- A status check shows only that booking's service, day, time, first name and status. It shows no phone or email.