# Hair Salon Booking Page

## 1. People and their journey
**Client** (the only role in the interface). A client arrives on the page wanting a haircut or other service. They need to see which services exist, how long each takes, and which times are free. They pick a service, pick a day and a free time, enter their name, phone and email, and submit. A confirmation panel shows the booking as "Requested". They can return to the page later, enter their booking reference and email, and see whether it is still Requested or has been Confirmed.

**Salon staff** (outside the interface) confirm requested bookings. They have no screens here.

## 2. How it looks
The product looks like a familiar online appointment booker. It is a single centred column of three numbered steps (Service, Time, Your details), and a summary bar sits beneath them. The palette is warm: cream, deep plum and soft rose.

- **Page background:** flat cream (#FAF6F0) filling the whole window, behind everything.
- **Header bar:** full width at the top, flat deep plum (#4A2545), showing the salon name in white serif text on the left and a "Check my booking" text link in rose (#E8A0B4) on the right. The link is underlined on hover.
- **Content column:** a centred column, at most 720px wide, on a raised white card with a soft grey shadow and 12px rounded corners.
- **Step headings:** a plum circle holding a white number (1, 2 or 3) followed by a plum heading. The circle turns into a rose circle with a white tick once that step is complete.
- **Service list (step 1):** stacked outlined rows with a 1px light grey border. Each row shows the service name on the left and the duration ("45 min") in grey on the right.
  - On hover, the row has a cream background.
  - When selected, the row has a plum border, a pale rose fill (#FBEAF0) and a plum tick at the far left.
- **Day strip (step 2):** a horizontal row of 14 day chips starting from today. Each chip shows the weekday abbreviation over the date number, with left and right plum arrows at the ends.
  - A normal chip is outlined in grey.
  - The selected chip is filled plum with white text.
  - A day with no free times has grey text and a strikethrough, and cannot be chosen.
  - Today's chip carries a small rose dot beneath the date.
- **Time grid (step 2):** free start times sit in a grid of pill buttons, four per row.
  - A free time is outlined plum with plum text.
  - A hovered time has a cream fill.
  - The selected time is filled plum with white text.
  - A taken time is not shown.
- **Time grid empty state:** when no service is chosen, a grey line reads "Choose a service first". When the day has no free times, a grey line reads "No times left this day".
- **Details form (step 3):** three sunken fields (light grey fill, grey bottom border), labelled Name, Phone and Email. An optional Notes box sits below them.
  - A focused field has a plum bottom border.
  - An invalid field has a red (#C0392B) bottom border and a small red message beneath it.
- **Summary bar:** at the bottom of the card on a flat pale rose strip, showing the chosen service, day, time and duration, for example "Cut & blow-dry · Tue 14 May · 10:30–11:15".
- **Request booking button:** sits in the summary bar on the right, filled plum with white text and raised with a shadow.
  - It is darker plum while pressed.
  - It is grey with no shadow while any step is incomplete.
  - It shows a white spinner while sending.
- **Error banner:** a flat red strip above the button with white text, for example "That time was just taken. Please pick another." It appears when submission fails.
- **Confirmation panel:** replaces the steps after a successful submission. It shows a large rose tick, "Booking requested", the booking reference in bold plum monospace, the summary, and a status badge.
- **Status badge:** a pill showing the booking's status.
  - Requested: amber fill (#F5C26B) with dark text.
  - Confirmed: green fill (#3E9B6B) with white text.
- **Check my booking panel:** replaces the steps when opened from the header link. It has sunken Reference and Email fields, a plum "Look up" button, and below them the summary with the status badge, or a red "No booking found" line.

## 3. How it is used
- **Choose a service:** click or tap a service row to select it, which deselects any other. The day strip and time grid then update for that service's duration.
- **Change the service:** click or tap a different row. Any chosen time is cleared if it no longer fits the new duration.
- **Move through days:** click or tap the arrows to move the day strip by 7 days. On touch screens, the strip can also be swiped sideways.
- **Choose a day:** click or tap an available day chip to show its free times.
- **Choose a time:** click or tap a free time pill to select it. Clicking or tapping the selected pill again deselects it.
- **Fill in details:** type in the Name, Phone, Email and Notes fields. Each field is checked when you leave it.
- **Send the request:** click or tap Request booking, or press Enter in the last field. This submits the request and then shows the confirmation panel or the error banner.
- **Copy the reference:** click or tap the booking reference to copy it. A "Copied" tooltip shows for 2 seconds.
- **Book another appointment:** click or tap "Book another" on the confirmation panel to return to empty steps.
- **Open the lookup:** click or tap "Check my booking" in the header to open the lookup panel.
- **Look up a booking:** type the reference and email, then click or tap Look up to see the status.
- **Return to booking:** click or tap the salon name in the header to go back to the booking steps.

## 4. Scope
The single loop is: pick a service, pick a day within the next 14 days, pick a free start time, give contact details, and submit. A booking starts as Requested, and the client can check later whether it has been Confirmed.

The choices offered along the way are which service and which day. The form asks only for name, phone, email and optional notes.

Left out are stylist choice, payment, deposits, product sales and loyalty schemes.

## 5. Things and their states
- **Service:** holds a name and a duration in minutes. It has no states.
- **Opening hours:** hold the opening and closing time for each weekday, or closed. They are fixed salon settings.
- **Time slot:** a start time on a day. A slot is free or taken, and becomes taken when a booking covers it.
- **Booking:** holds a reference, service, day, start time, end time, name, phone, email, notes and status.
  - It is created as **Requested** on submit.
  - It becomes **Confirmed** when salon staff confirm it, outside the interface.

## 6. Rules
- **Start times:** start times fall every 15 minutes within opening hours.
- **Fit before closing:** a start time is offered only if the whole service duration ends at or before closing time.
- **No overlaps:** a start time is offered only if its whole duration overlaps no Requested or Confirmed booking. The salon takes one booking at a time.
- **Past and near times:** times in the past, and times less than 1 hour from now, are not offered.
- **Booking window:** only today and the next 13 days can be chosen. Days outside the window are not shown.
- **Closed days:** closed days appear struck through and cannot be chosen.
- **Submit requires everything:** submit is refused (the button stays grey) until a service, day and time are chosen and the details are valid.
- **Name:** required, 2–80 characters.
- **Phone:** required, 7–15 digits. Spaces, "+", "(", ")" and "-" are allowed.
- **Email:** required, in the form name@domain.
- **Notes:** optional, at most 300 characters. Typing beyond 300 characters is ignored.
- **Slot taken at submit:** if the slot was taken by someone else before submission, the request is refused, the error banner shows, the time grid refreshes, and the selection is cleared.
- **Reference:** each booking gets a unique 6-character reference of letters and digits.
- **Starting status:** a new booking is always Requested. Clients cannot confirm, edit or cancel a booking on this page.
- **Lookup matching:** a lookup shows a booking only when both the reference and the email match. Otherwise it shows "No booking found".
- **Double submission:** pressing Request booking again while it is sending is ignored.