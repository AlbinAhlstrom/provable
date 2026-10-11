### 1. Default Landing & Cold-Start Behavior
The page opens directly on the booking flow, with step 1 "Service" active and steps 2 to 4 muted. No empty dashboard, no splash screen. While `Service.name` and `Service.duration_minutes` load, the service list shows three grey placeholder rows with the text "Loading services…". If no services are published, the card shows "No services are offered online yet. Please call the salon." If loading fails, it shows "We couldn't load services. Try again." with a Retry button. Days and times stay hidden until a service is chosen, so no step is ever blank for lack of context.

### 2. Primary Navigation & View Structure
One page, one card, four numbered steps in fixed order: 1 Service, 2 Day, 3 Time, 4 Your details. Steps are not tabs; the client moves forward by choosing, and any step before the current one stays open for revision. The header carries the salon name (`Salon.name` from the business record, falling back to the page title "Book an appointment") and the line "Book your appointment". The confirmation panel replaces the card content; there are no other views.

### 3. Workflow Prerequisites & Form Ergonomics
Each gated step explains what to do first, in place of a silent disabled state:
- Day step, before a service: "Choose a service above to see available days."
- Time step, before a day: "Pick a day to see its free times."
- Button, while incomplete: "Choose a time and add your details to continue." Naming the first missing item (for example "Add your phone number to continue") once a time is chosen.

Form controls match their data: Name is a text input with autocomplete "name"; Phone is a `tel` input with autocomplete "tel" and an inputmode of tel; Email is an `email` input. Labels stay visible above each field. Guidance sits under the label: "Phone: 7 to 15 digits, spaces and dashes allowed." Validation runs when a field is left. Day buttons and time slots are real buttons with keyboard Enter and Space support.

### 4. Human Copy & Action Labeling
- Step names: Service, Day, Time, Your details.
- Button: "Request booking"; while sending "Sending…"; after success "Book another".
- Summary line: "{Service.name}, {date}, {start time} to {end time}."
- Empty day: "No times left on this day."
- Name error: "Enter your name (up to 80 characters)."
- Phone error: "Enter a phone number with 7 to 15 digits."
- Email error: "Enter an email address like name@example.com."
- Taken slot banner: "That time was just taken. Please choose another."
- Failure banner: "We couldn't send your request. Please try again."
- Confirmation heading: "Request received". Body: "The salon will confirm your booking shortly." Badge: "Requested" (amber); "Confirmed" (green) when `Booking.status` is confirmed.

### 5. Contextual Action Placement
Every action sits in the step where it applies. Service rows open the Day step beneath them; day buttons sit above the time grid; the summary and "Request booking" button sit together at the foot of the card, where the client's eye ends. Errors appear directly above the button. "Book another" lives inside the confirmation panel only. No cancel, edit or staff controls appear anywhere on the page.

### 6. Visual Direction
**Feel**: a calm, friendly appointment widget, like a neat paper booking card in a warm salon.
Layout: the page background is flat off-white; a flat white header band holds the title; a single white card, up to 640px wide, sits centred with a soft shadow and generous margins. Steps are stacked with numbered headings. Service rows are outlined in light grey; day buttons form a horizontal row; time slots form a grid of small outlined buttons. Selected items fill dusty rose; unavailable items fade and strike through. Corners are gently rounded (8px), borders are one light line, shadows are soft, and spacing between steps is generous, so the page reads as airy and not dense.
Type: `font-sans` for headings and body; the page headline is `text-2xl font-bold` (the salon name). Body text is `text-base`.
Palette (Tailwind-compatible): background stone-50 (#FAF6F2), surface white (#FFFFFF), text charcoal (#2B2B2B), muted step text grey (#9A9A9A), accent dusty rose (#C77D8E) for selected items and the primary button, and the pressed rose (#A9606F). The middle-tone rose on the button keeps white text readable.

LAYOUT columns=1 rows=auto

TOKENS background=#faf6f2 surface=#ffffff text=#2b2b2b accent=#c77d8e on_accent=#ffffff heading=sans