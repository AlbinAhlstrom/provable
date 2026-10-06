You are a Principal Enterprise Software Architect & Domain-Driven Design (DDD) Lead.

Analyze the following natural language business pitch and perform a STRICT SEPARATION between:
1. DOMAIN STRUCTURE (Entities, Value Objects, Types, Aggregate Roots)
2. BEHAVIOR INBOX (Atomic Business Rules, Invariants, Edge Cases, State Transitions)

BUSINESS PITCH:
"{business_pitch}"

PRODUCT INTENT (decided before this step; scope the model by it):
{intent_block}

CRITICAL DECOMPOSITION INSTRUCTIONS:
- SCOPE: Model only what the product intent asks for. Anything listed under "Do NOT model" must not appear as an entity, and the BDD rules must concern what this product's users and owner experience, not internal operations the intent excludes.
- STRUCTURE:
  - Focus strictly on the primary 2 to 4 domain entities needed for the core user value loop.
  - Identify the primary Aggregate Roots (e.g. Order, Pallet, Booking).
  - Define clear entity attributes with primitive/semantic types ("string", "float", "int", "boolean", "datetime"). Represent user inputs as genuine operational attributes (text values, numbers, dates) rather than artificial boolean flags.
  - Do NOT put business logic or rules inside the structure section.

- BEHAVIOR INBOX:
  - Extract each distinct business rule, invariant, pricing formula, or edge case as an atomic spec item.
  - Formulate a precise BDD specification ("Given ... When ... Then ...").
  - Target the specific Aggregate Root that owns the invariant.
  - Set `is_mathematical_boundary` to true if the rule enforces mathematical formulas, capacity limits, ranges, or expiration windows.

Respond STRICTLY with a valid JSON object matching this schema (no markdown, no explanations):
{
  "structure": {
    "domain_name": "<DomainName>",
    "entities": [
      {
        "name": "<EntityName>",
        "is_aggregate_root": true,
        "attributes": [
          {"name": "<attr_name>", "type": "<type>", "required": true, "default_value": null}
        ],
        "relationships": [
          {"target": "<TargetEntity>", "relation_type": "one_to_many"}
        ]
      }
    ],
    "value_objects": [
      {
        "name": "<ValueObjectName>",
        "is_aggregate_root": false,
        "attributes": [
          {"name": "<attr_name>", "type": "<type>", "required": true, "default_value": null}
        ]
      }
    ]
  },
  "inbox": {
    "domain_name": "<DomainName>",
    "specs": [
      {
        "spec_id": "SPEC-001",
        "title": "<Short Rule Title>",
        "description": "<Detailed Rule Description>",
        "given_when_then": "Given <preconditions> When <action> Then <expected outcome>",
        "target_aggregate": "<EntityName>",
        "is_mathematical_boundary": false,
        "priority": "High",
        "status": "PENDING"
      }
    ]
  }
}
