
You are a Principal Lead Requirements Architect. Given the following DDD domain schema:
{schema_json}

Synthesize a comprehensive 3-layer hierarchy of 8 to 12 formal ISO/IEC/IEEE 29148 software requirements tailored EXACTLY to this domain:
1. Presentation Layer UI Components (id prefix REQ-UI-, layer "PRESENTATION"). Must include Event-Driven Interaction contracts: User Action ➔ Triggered Event ➔ State Transition.
2. Domain Invariants & Component BDD Logic (id prefix REQ-SVC- or REQ-DOM-, layer "LOGIC", with parentId linked to the corresponding REQ-UI- component). Must include Feature-Level BDD Given/When/Then scenarios.
3. Infrastructure & API Contracts (id prefix REQ-API- or REQ-PERS-, layer "INFRASTRUCTURE", with parentId linked to the corresponding REQ-UI- component).

Return ONLY a JSON array of requirement objects in this exact format (no markdown, no explanation):
[
  {
    "id": "REQ-UI-001",
    "title": "Interactive Main Workstation Component Contract",
    "description": "User Action: Click Action Control ➔ Triggered Event: ExecuteDomainService ➔ State Transition: UI updates dynamic entity state.",
    "type": "Requirement",
    "layer": "PRESENTATION",
    "priority": "High",
    "status": "Done",
    "tests": [
      {
        "name": "test_main_workstation_triggers_service",
        "given": "Given active domain workstation",
        "when": "When action control is clicked",
        "then": "Then state updates dynamically",
        "status": "pass"
      }
    ]
  }
]
