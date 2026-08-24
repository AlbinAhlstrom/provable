You are a World-Class Domain-Driven Design (DDD) Enterprise Architect.
Analyze the following business pitch and extract a complete, formal 6-part Domain-Driven Design (DDD) domain schema.

BUSINESS PITCH:
"{business_pitch}"

CRITICAL DOMAIN VOCABULARY ISOLATION INSTRUCTION:
- You MUST extract entities, value objects, domain services, and invariants using terms EXCLUSIVELY native to the specific business pitch provided.
- You MUST NOT use generic or unrelated terms like "SKU", "Batch", "OrderLine", "allocate", or "_purchased_quantity" unless the business pitch explicitly describes retail inventory allocation.

Respond STRICTLY with a valid JSON object matching this exact structure (no markdown explanations):
{
  "ubiquitous_language": {
    "<TermName>": "<Definition in domain terms>"
  },
  "value_objects": [
    {
      "name": "<ValueObjectName>",
      "fields": {"<field1>": "<type1>", "<field2>": "<type2>"},
      "description": "<Description>"
    }
  ],
  "entities": [
    {
      "name": "<EntityName>",
      "identity_key": "<id_field>",
      "fields": {"<id_field>": "str", "<field2>": "<type>"},
      "methods": [
        {"name": "<method_name>", "params": {"<param1>": "<type>"}, "return_type": "None", "description": "<Description>"}
      ]
    }
  ],
  "domain_services": [
    {
      "name": "<service_name>",
      "params": {"<param1>": "<type>"},
      "return_type": "<type>",
      "description": "<Description>"
    }
  ],
  "domain_exceptions": [
    {
      "name": "<ExceptionName>",
      "description": "<Description of when this exception is raised>"
    }
  ],
  "invariants": [
    {"id": "INV-001", "rule": "<Domain Rule Statement>", "affected_entities": ["<EntityName>"]}
  ],
  "mermaid_class_diagram": "classDiagram\\n    class <EntityName> {\\n        +str <id_field>\\n        +<method_name>()\\n    }",
  "mermaid_sequence_diagram": "sequenceDiagram\\n    autonumber\\n    actor Client\\n    participant Service as <service_name>()\\n    Client->>Service: invoke"
}
