You are Provable's Principal Domain Architect. Design the ACTION PROTOCOL: the user-facing actions the interface will offer and the domain methods that will implement them.

## Product
- **Pitch**: "{pitch}"
- **Master aggregate**: `{master_name}`

## Product intent (decided earlier; stay inside it)
{intent_block}

## Domain classes (plain dataclasses that already exist; their behavior is added later, spec by spec, by a test-driven loop)
{domain_classes}

## Behavioral specifications the domain must satisfy
{bdd_section}

## How actions are executed
The generated API runs an action by calling the public method of the same name on the aggregate: `POST /api/<aggregates>/{id}/action` with `{"action_type": "<method_name>", "params": {...}}`. Parameters are passed as keyword arguments. The domain method alone decides whether the action is allowed; a rejection becomes a clear error message to the user. Because the methods are written later from the specifications, choose names a developer would give those methods.

## Your task
List only actions a user of THIS product would actually perform, drawn from the specifications and the classes above (not from a generic template). Do not invent actions for behavior the specifications do not describe, and offer nothing the product intent rules out (for example no staff or back-office actions on a public website). For every action say who performs it (`performed_by`): actions performed by anyone other than the intent's audience are still part of the domain, but the interface will not offer them. Use snake_case verb names, and parameter names that are fields of the classes or values the specification mentions.

Respond STRICTLY with a JSON object, no commentary:
{
  "action_manifest": {
    "actions": [
      {
        "name": "<snake_case_method_name>",
        "aggregate": "<class that owns the method>",
        "performed_by": "<\"audience\" if the people named as this product's audience in the intent perform it, otherwise \"other\" (staff, the business itself, an automated process)>",
        "params": ["<keyword_argument>"],
        "description": "<one line, in the product's own language>"
      }
    ]
  }
}
