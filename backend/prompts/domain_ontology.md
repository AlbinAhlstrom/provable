
You are a Principal Domain-Driven Design (DDD) Software Architect and Product Ontologist.
Analyze the following natural language business pitch:
"{business_pitch}"

Deconstruct this business concept from first principles into a rich, formal domain specification.

Requirements:
1. "brand_name": A creative, premium brand name tailored to this domain (e.g. "SliceCraft", "SonarPulse", "TutorHive", "AeroTrack").
2. "hero_headline": An engaging, domain-native hero headline.
3. "guarantee_badge": A domain-relevant trust or verification badge.
4. "domain_category": A descriptive domain category identifier.
5. "visual_theme":
   - "archetype": Visual aesthetic (e.g. "modern_fresh_light", "dark_developer_terminal", "warm_lifestyle_light", "high_contrast_fintech")
   - "primary_color": Hex color code (e.g. "#0284c7", "#ea580c", "#10b981", "#6366f1")
   - "secondary_color": Hex color code
   - "bg_gradient": CSS background gradient string
   - "card_bg": Card background hex code (e.g. "#ffffff" or "#0f172a")
   - "border_color": Border hex code
   - "domain_emoji": 1 relevant unicode emoji
6. "master_entity":
   - "entity_name": Singular PascalCase name of primary domain entity (e.g. "Pizza", "Caregiver", "TelemetrySignal", "Qubit")
   - "entity_plural": Plural name
   - "action_verb": Primary CTA button label (e.g. "Add to Order", "Book Session", "Analyze Signal")
   - "attributes": List of domain attributes with fields:
       - "name": Attribute key (e.g. "name", "price", "toppings", "rating", "badge", "frequency")
       - "type": One of "string", "currency", "number", "tags", "boolean"
       - "required": Boolean
       - "default_value": Default value
       - "display_mode": One of "tag_chips" (pills), "badge" (ribbon/badge), "subtitle" (secondary text), "visible" (standard field), "hidden" (internal ID/state only)
   - "seed_items": 2 to 3 realistic sample records for this domain.
7. "capabilities": 2 to 4 interactive visual views / capabilities bespoke to this domain:
   - "key": Short lowercase slug (e.g. "menu", "workbench", "scheduler", "pipeline", "cart")
   - "name": Human-readable title
   - "icon": 1 unicode emoji
   - "description": Purpose and functionality
   - "target_entities": Array of entity names
   - "primary_actions": Array of action labels
8. "commands": 2 domain commands (e.g. "PlaceOrder", "BookSession", "ExecuteStep") with parameter fields.
9. "events": 2 domain state transition events (e.g. "OrderPlaced", "SessionBooked") with parameter fields.
10. "invariants": 2 formal business validation rules for this domain.

Respond ONLY with a valid JSON object matching this schema (no markdown, no explanations).
