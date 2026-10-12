### 1. Default Landing & Cold-Start Behavior
- The page opens on the booking form itself, with step 1 (Service) active and the later steps muted. There is no empty sub-view and no bookings list, since the client has none.
- While `Service` records load, step 1 shows three skeleton rows. If the list is empty, it shows "No services are open for booking right now. Please check back soon." If loading fails, it shows "We couldn't load the services." with a "Try again" link.
- Steps 2 and 3 are muted and carry one line of guidance each: "Choose a service first." and "Choose a day first."
- The header shows the salon's title, then "Book your appointment".

### 2. Primary Navigation & View Structure
There are no tabs or menus. The page has two states of one view:
1. **Booking form**, a stacked card with four numbered steps: 1 Service, 2 Day, 3 Time, 4 Your details. The summary line, error banner and button sit at the foot.
2. **Confirmation panel**, which replaces the form and ends with "Book another".

Each step opens in sequence and stays editable. Changing an earlier step clears the later choices that depend on it.

### 3. Workflow Prerequisites & Form Ergonomics
- **Prerequisites**: service, then day, then time, then details. Each muted step says what to do first.
- **Day**: a horizontal row of buttons (weekday and date). Days with no free times are faded and unclickable, with a small note "Faded days have no free times." The row scrolls sideways on phones.
- **Time**: a grid of start times in a radio-group pattern. Taken and past times are struck through. A day with no slots shows "No times left on this day."
- **Fields**:
  - Name: text input, `autocomplete=name`, max 80 characters.
  - Phone: `type=tel`, hint "7–15 digits. Spaces, + and - are fine."
  - Email: `type=email`.
  - Each field has a visible label and is validated on blur.
- **Gated button**: while it is disabled, a line above it names what is missing, e.g. "Still needed: a time, your phone number." It disappears when the form is valid.
- **Keyboard**: rows, days and times are focusable and respond to Enter or Space. Focus rings are dusty rose. Submit-time errors move focus to the banner.

### 4. Human Copy & Action Labeling
- Step headings: Service, Day, Time, Your details.
- Service row: `Service.name` and `Service.duration_minutes` shown as "45 min".
- Summary: "`Service.name`, `TimeSlot.slot_date`, `TimeSlot.start_time` to `TimeSlot.end_time`".
- Field errors: "Please enter your name." / "Name must be 80 characters or fewer." / "Enter a phone number with 7 to 15 digits." / "Enter a valid email address."
- Button: "Request booking", then "Sending…".
- Banners: "That time was just taken. Please choose another." / "We couldn't send your request. Please try again."
- Confirmation: heading "Request sent", the booking summary, a badge showing `Booking.status` ("Requested" amber, "Confirmed" green), and the line "The salon will confirm your appointment." Link: "Book another".

### 5. Contextual Action Placement
- Each choice is made inside its own step, and tapping it advances the flow. There are no global controls.
- "Request booking" is the only primary action, at the foot of the card after the summary and error banner.
- "Try again" appears inline in a failed service load.
- "Book another" appears only in the confirmation panel.
- Cancel and edit controls are absent.

### 6. Visual Direction
- **Feel**: a simple appointment-booking widget, warm, soft and friendly, a used tool, so the form opens directly with no hero.
- **Palette**: page `stone-50` (#FAF6F2), surface `white`, text charcoal (#2B2B2B), accent dusty rose (#C77D8E, pressed #A9606F, pale fill #F8E6EA), muted grey #9A9A9A, error #C0392B, amber #E0A030, green #3E8E5A.
- **Type**: `font-sans` throughout. The title is `text-2xl` semibold. Step headings are bold `text-lg`.
- **First screen**: a white header band, then a centred card (max 640px) with step 1 service rows ready to tap.
- **Form of the main view**: a stacked appointment widget as one card. Service rows are equal in height. Day buttons are equal in width. Time slots are equal-sized grid cells.
- **Shape and rhythm**: `rounded-xl` card with a soft shadow, `rounded-lg` controls, 1px #D9D2CB borders, generous 24px gaps between steps, relaxed density.

LAYOUT columns=1 rows=auto
TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans