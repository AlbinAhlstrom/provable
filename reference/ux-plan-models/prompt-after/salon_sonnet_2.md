### 1. Default Landing & Cold-Start Behavior
- Arrival shows the single booking form, step 1 "Service" open and ready. Steps 2 to 4 are visible but muted grey (#9A9A9A).
- Header band shows the salon booking title and the line "Book your appointment". The title text comes from the salon's name record, never invented.
- Service step is filled by `Service.name` (left) and `Service.duration_minutes` (right, shown as "45 min"), one row per record.
- Service loading: three grey placeholder rows (#F3ECE6) of row height, no text. The Book button stays disabled.
- Service empty: one line "No services are available right now." in grey, in place of the rows.
- Service load failed: one line "Services could not be loaded." with a "Try again" button beside it that reloads.
- Day step on arrival: no day buttons. One muted line "Choose a service first." sits under heading 2.
- Time step on arrival: no grid. One muted line "Choose a day first." sits under heading 3.
- Details step on arrival: fields are shown but unclickable (disabled, muted) until a time is chosen. The line "Choose a time first." sits beneath heading 4.
- Time slots load per day: a grid of grey placeholder buttons while loading. If the load fails: "Times could not be loaded." with "Try again".
- Day with no free times for the service: the grid is replaced by "No times left on this day."
- Summary line is hidden until a time is chosen. The error banner is hidden until needed.

### 2. Primary Navigation & View Structure
- One view only: the booking page. There are no tabs, menus or navigation.
- After submit, the confirmation panel replaces the form in the same card. "Book another" returns to step 1.
- Steps run in order 1 to 4 and are stacked down the page. A step opens when the previous one is complete.

### 3. Workflow Prerequisites & Form Ergonomics
- Service comes first. Until chosen, steps 2 to 4 are muted, their controls unclickable, and each carries its one-line prompt from section 1.
- Choosing a service opens the day step. The day row shows days with free times; days with none are faded and unclickable.
- Choosing a day reveals its free times for that service. Choosing a time shows the summary and enables the details fields.
- Changing service clears the chosen time and recalculates the slots. The day stays if it still has free times.
- Booked or past slots ignore clicks silently. The selection does not change.
- Name: text input, label "Name", refused when empty with "Please enter your name." and when over 80 characters with "Name must be 80 characters or fewer."
- Phone: tel input, label "Phone", refused with "Enter a phone number with 7 to 15 digits." Spaces, plus signs and dashes are allowed.
- Email: email input, label "Email", refused with "Enter a valid email address."
- Fields are validated on leaving them. Invalid ones show the red outline and message.
- The Book button is disabled until all is valid. Beside it, a small grey line names what is missing: "Still needed: service, day, time, your details." Only the missing items are listed.
- Submitting shows "Sending…", the button disabled, and further clicks are ignored.
- If the slot was taken, the banner shows, the slot list refreshes, and the chosen time is cleared. If sending failed, the banner shows and the entries are kept.

### 4. Human Copy & Action Labeling
- **Seen**
- Header: `Salon.name` (from the salon's record) and "Book your appointment".
- Step headings: "1 Service", "2 Day", "3 Time", "4 Your details".
- Service rows: `Service.name`, `Service.duration_minutes` as "45 min".
- Day buttons: weekday and date, such as "Tue 14".
- Time slots: `TimeSlot.start_time`, such as "10:30".
- Prompts: "Choose a service first.", "Choose a day first.", "Choose a time first."
- Empty and error: "No services are available right now.", "Services could not be loaded.", "Times could not be loaded.", "Try again", "No times left on this day."
- Field labels: "Name", "Phone", "Email". Messages as in section 3.
- Summary line: "{Service.name} · {date} · {start time} to {end time}".
- Missing hint: "Still needed: …"
- Button: "Request booking", then "Sending…".
- Banner, slot taken: "That time was just taken. Please choose another."
- Banner, failure: "Your request could not be sent. Please try again."
- Confirmation: heading "Booking requested", the booking summary and the badge "Requested". The badge reads "Confirmed" when the status is confirmed. Link: "Book another".
- **Spoken only**
- Green check: "Success".
- Selected service, day and time: "Selected".
- Faded day and time options: "Unavailable".
- Banner: "Error".

### 5. Contextual Action Placement
- Service selection sits on each service row. Day selection sits on each day button in step 2. Time selection sits on each slot in step 3.
- "Try again" sits beside the load error line it relates to.
- "Request booking" is full-width at the foot of the form, below the summary line, the missing hint and the banner.
- "Book another" sits below the booking summary in the confirmation panel.
- No cancel or edit actions exist anywhere.

### 6. Visual Direction
- **Feel**: a simple appointment-booking widget, with stacked numbered steps on a warm white page. It is light, friendly and calm, as the specification describes.
- **Palette**: page #FAF6F2; header band and card #FFFFFF; text charcoal #2B2B2B; muted #9A9A9A; row outline #D9D2CB; hover #F3ECE6. Accent dusty rose #C77D8E with pale rose fill #F8E6EA, pressed #A9606F. Error red #C0392B with pale red banner #FBEAE8. Amber #E0A030 (Requested), green #3E8E5A (Confirmed and check). Disabled button light grey #E5E0DB with text #9A9A9A.
- **Type**: `font-sans` for headings and body. The title is 24px semibold; step headings are 18px bold; body is 16px; summary and hints are 14px.
- **First screen**: the white header band, then the centred card with step 1 and its service rows open, and steps 2 to 4 muted below. There is no introduction, and the Book button is disabled at the foot.
- **Form of the main view**: a stacked, numbered booking widget in one card, max 640px, full width on phones. Service rows are full-width, 56px high. Day buttons are 64px wide and 72px high in a horizontally scrolling row. Time slots are 88px by 40px in a wrapping grid, three across on phones. Rows and buttons are all alike whatever they hold.
- **Shape and rhythm**: radius 12px on the card, 8px on rows, buttons and inputs. The card has a soft shadow (0 4px 20px rgba(43,43,43,0.08)). Sections are 32px apart and rows 8px apart, with 24px card padding. The page is airy.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans