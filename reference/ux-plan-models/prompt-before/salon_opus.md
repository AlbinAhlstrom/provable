### 1. Default Landing & Cold-Start Behavior
- The page opens straight onto the booking card, with step 1 (Service) active. Steps 2–4 are muted.
- **Services loading:** three grey placeholder rows.
- **No services:** a calm note, "No services are open for booking right now."
- **Services failed to load:** "We couldn't load services. Try again." The "Try again" link reloads them.
- **Day and time steps:** the same three states apply. Loading shows placeholders. If no days in the range have free times, the step shows "No free days in the coming weeks."
- There is never a blank screen. The muted steps carry guidance instead (see section 3).

### 2. Primary Navigation & View Structure
There is one page with no navigation and two states.
1. **Booking form**, with four numbered steps:
   - Service
   - Day
   - Time
   - Your details
2. **Confirmation panel**, which replaces the form after submit.

There are no staff views, accounts or edit/cancel screens.

### 3. Workflow Prerequisites & Form Ergonomics
**Each muted step shows one grey hint line:**
- Day: "Choose a service first."
- Time: "Choose a day first."
- Details stay usable at all times.

**Disabled button.** The text under "Request booking" lists what is still missing, for example "Still needed: a time, your phone number." It updates live.

**Fields:**
- **Name:** text input, `autocomplete=name`, max 80.
- **Phone:** `type=tel`, `autocomplete=tel`. Hint: "7–15 digits; spaces, + and - are fine."
- **Email:** `type=email`, `autocomplete=email`.

**Validation and errors:**
- Fields are validated when you leave them. An invalid field gets a red outline and a message below it.
- Errors are announced via `aria-live`.
- If the slot was taken in the meantime, the time is cleared and the grid refreshes.

**Keyboard and screen readers:**
- Services, days and times are radio groups.
- Tab reaches each group, and Enter or Space selects an option.
- Faded options are `aria-disabled` and skipped by the keyboard.

### 4. Human Copy & Action Labeling
**Content from records:**
- Service rows show `Service.name` on the left and `Service.duration_minutes` + " min" on the right.
- Day buttons show the weekday and date from `TimeSlot.slot_date`.
- Time buttons show `TimeSlot.start_time`.

**Field messages:**
- Name: "Please enter your name (up to 80 characters)."
- Phone: "Enter a phone number with 7–15 digits."
- Email: "Enter a valid email address."

**Other wording:**
- **Empty day:** "No times left on this day."
- **Summary:** "{Service.name} · {date} · {start_time}–{end_time}"
- **Button:** "Request booking". While sending, it shows "Sending…".
- **Error banners:**
  - Slot taken: "That time was just taken. Please pick another."
  - Sending failed: "We couldn't send your request. Please try again."
- **Confirmation:**
  - Heading: "Request sent"
  - The summary line, followed by the **Requested** badge (amber).
  - "The salon will confirm your appointment."
  - **Confirmed** badge (green) when the status is confirmed.
  - Link: "Book another".

### 5. Contextual Action Placement
- Each choice is made in place, inside its own step.
- The summary, error banner and single primary button sit together at the foot of the card.
- "Book another" appears only on the confirmation panel.
- Changing the service collapses the chosen time back to the Time step, which shows "Choose a time" again.

### 6. Visual Direction
- **Feel:** a warm, friendly salon appointment widget, like a familiar booking form. Calm, with soft rose touches.
- **Palette:**
  - Page background: #FAF6F2 (stone-50 warm)
  - Surface: white
  - Text: #2B2B2B (neutral-800)
  - Muted text: #9A9A9A
  - Borders: #D9D2CB
  - Accent: dusty rose #C77D8E, pressed #A9606F
  - Selected fill: #F8E6EA
  - Error: #C0392B
  - Requested badge: amber #E0A030
  - Confirmed badge: green #3E8E5A
- **Type:**
  - Headings use `font-serif`. The header title is `text-3xl font-semibold`.
  - Body text uses `font-sans` at `text-base`.
  - Step headings are bold sans with number circles.
- **First screen:**
  - A white header band with the title and "Book your appointment".
  - Below it, the card begins immediately with step 1's service rows. There is no intro text.
- **Form of the main view:**
  - One card, max 640px wide, full width on phones, with steps stacked inside it.
  - Service rows are full width and equal height.
  - Day buttons sit in a horizontally scrolling row of equal-width chips.
  - Times sit in a 4-column grid of equal-size buttons (3 columns on phones).
- **Shape and rhythm:**
  - Card: `rounded-2xl`, `shadow-md`.
  - Options: `rounded-lg`, 1px borders.
  - Spacing: 32px between steps, 8px between options.
  - Comfortable density.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=serif