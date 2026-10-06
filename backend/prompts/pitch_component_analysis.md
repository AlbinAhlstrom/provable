
You are a Lead Product Architect. Analyze the following business pitch:
"{business_pitch}"

Deconstruct the application into:
1. Active Components: Identify all UI components required for this application idea.
   - For standard capabilities, map to canonical keys: "catalog" (menu/product grid), "cart" (shopping cart/checkout), "tracking" (order tracking pipeline), "kds" (admin/kitchen dashboard), "reviews" (ratings & feedback), "auth" (user login/profiles), "calendar" (booking/appointments).
   - For custom concepts mentioned in pitch (e.g. "interactive calculator", "custom builder", "crypto wallet"), specify a clean canonical_key (e.g. "rate_calculator"), descriptive title, and component_type "custom".
2. Suggested Prompts: Generate 3 to 6 dynamic, domain-aware feature suggestions that the user might want to add next (e.g. "Add payment system", "Add live chat", "Add analytics").

Return ONLY valid JSON in this exact format (no markdown, no preamble):
{
  "components": [
    {
      "canonical_key": "catalog",
      "title": "Item Catalog",
      "component_type": "premade",
      "description": "Product grid with category filters"
    },
    {
      "canonical_key": "rate_calculator",
      "title": "Interactive Rate Calculator",
      "component_type": "custom",
      "description": "Dynamic calculator tool embedded in application"
    }
  ],
  "suggestions": [
    "Add payment system",
    "Add loyalty points",
    "Add table reservation"
  ]
}
