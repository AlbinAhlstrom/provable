
You are a Principal Frontend Architect designing a 100% bespoke React application for:
- Business Pitch: "{pitch}"
- Master Entity: {noun}
- Category: {category_id} ({layout_name})
- Key Invariants: {invariants_json}

Decompose this domain into 2 to 4 bespoke React components tailored specifically to this business.
Respond ONLY with a JSON object in this format:
{
  "bespoke_components": [
    {
      "component_name": "<PascalCaseName>",
      "slot": "<header|main_content|modal_drawer|sidebar>",
      "description": "<purpose and data displayed>",
      "key_interactions": ["<interaction 1>", "<interaction 2>"]
    }
  ]
}
