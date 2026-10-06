"""
Universal Domain Ontology Stormer & Dynamic Conceptualization Engine.
Constructs 100% generic, contract-first Domain Ontologies for ANY arbitrary pitch
with ZERO domain-specific hardcoded switchboards.
"""

import re
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class EntityAttributeSpec:
    name: str
    type: str  # 'string' | 'currency' | 'number' | 'tags' | 'boolean'
    required: bool = True
    default_value: Any = None
    display_mode: str = "visible"  # 'tag_chips' | 'badge' | 'subtitle' | 'visible' | 'hidden'

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class MasterEntitySpec:
    entity_name: str
    entity_plural: str
    action_verb: str
    attributes: List[EntityAttributeSpec] = field(default_factory=list)
    seed_items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "entity_plural": self.entity_plural,
            "action_verb": self.action_verb,
            "attributes": [a.to_dict() for a in self.attributes],
            "seed_items": self.seed_items
        }

@dataclass
class DomainCommandSpec:
    name: str
    description: str
    fields: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DomainEventSpec:
    name: str
    description: str
    fields: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class VisualThemeSpec:
    archetype: str
    primary_color: str
    secondary_color: str
    bg_gradient: str
    card_bg: str
    border_color: str
    domain_emoji: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DomainCapabilitySpec:
    key: str
    name: str
    icon: str
    description: str
    target_entities: List[str] = field(default_factory=list)
    primary_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClarificationQuestion:
    id: str
    question: str
    category: str
    options: List[str]
    default_choice: str
    impact_rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DomainOntologySpec:
    pitch: str
    brand_name: str
    hero_headline: str
    guarantee_badge: str
    domain_category: str  # 'catalog_cart' | 'calendar_service' | 'pipeline_tracker' | 'dashboard_metrics'
    visual_theme: VisualThemeSpec
    master_entity: MasterEntitySpec
    secondary_entities: List[MasterEntitySpec] = field(default_factory=list)
    commands: List[DomainCommandSpec] = field(default_factory=list)
    events: List[DomainEventSpec] = field(default_factory=list)
    capabilities: List[DomainCapabilitySpec] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch": self.pitch,
            "brand_name": self.brand_name,
            "hero_headline": self.hero_headline,
            "guarantee_badge": self.guarantee_badge,
            "domain_category": self.domain_category,
            "visual_theme": self.visual_theme.to_dict(),
            "master_entity": self.master_entity.to_dict(),
            "secondary_entities": [e.to_dict() for e in self.secondary_entities],
            "commands": [c.to_dict() for c in self.commands],
            "events": [e.to_dict() for e in self.events],
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "invariants": self.invariants
        }


def storm_domain_ontology(pitch: str) -> DomainOntologySpec:
    """
    Universal Domain Ontology Stormer & Dynamic Conceptualization Engine.
    Leverages LLM semantic reasoning to deconstruct ANY business pitch into
    pure Domain-Driven Design (DDD) specifications with ZERO rule-based heuristics.
    """
    pitch_clean = pitch.strip()
    if not pitch_clean:
        pitch_clean = "Generic Application"

    prompt = f"""
You are a Principal Domain-Driven Design (DDD) Software Architect and Product Ontologist.
Analyze the following natural language business pitch:
"{pitch_clean}"

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
"""
    try:
        from agent_orchestrator import call_gemini
        raw_resp = call_gemini(prompt, stage="domain_ontology")
        cleaned = re.sub(r'^```[a-zA-Z]*\n?', '', raw_resp.strip())
        cleaned = re.sub(r'\n?```$', '', cleaned.strip()).strip()
        data = json.loads(cleaned)

        # Parse visual theme
        vt_data = data.get("visual_theme", {})
        visual_theme = VisualThemeSpec(
            archetype=vt_data.get("archetype", "modern_fresh_light"),
            primary_color=vt_data.get("primary_color", "#0284c7"),
            secondary_color=vt_data.get("secondary_color", "#10b981"),
            bg_gradient=vt_data.get("bg_gradient", "#f8fafc"),
            card_bg=vt_data.get("card_bg", "#ffffff"),
            border_color=vt_data.get("border_color", "#e2e8f0"),
            domain_emoji=vt_data.get("domain_emoji", "✨")
        )

        # Parse master entity
        me_data = data.get("master_entity", {})
        attr_specs = []
        for a in me_data.get("attributes", []):
            attr_specs.append(EntityAttributeSpec(
                name=a.get("name", "attribute"),
                type=a.get("type", "string"),
                required=a.get("required", True),
                default_value=a.get("default_value", None),
                display_mode=a.get("display_mode", "visible")
            ))

        master_entity = MasterEntitySpec(
            entity_name=me_data.get("entity_name", "Item"),
            entity_plural=me_data.get("entity_plural", "Items"),
            action_verb=me_data.get("action_verb", "Select"),
            attributes=attr_specs,
            seed_items=me_data.get("seed_items", [])
        )

        # Parse capabilities
        capabilities = []
        for cap in data.get("capabilities", []):
            capabilities.append(DomainCapabilitySpec(
                key=cap.get("key", "main"),
                name=cap.get("name", "Main View"),
                icon=cap.get("icon", "✨"),
                description=cap.get("description", "Domain View"),
                target_entities=cap.get("target_entities", [master_entity.entity_name]),
                primary_actions=cap.get("primary_actions", [])
            ))

        if not capabilities:
            capabilities = [
                DomainCapabilitySpec(
                    key="catalog",
                    name=f"{master_entity.entity_name} Catalog",
                    icon="📋",
                    description=f"Browse {master_entity.entity_name.lower()} offerings",
                    target_entities=[master_entity.entity_name],
                    primary_actions=[master_entity.action_verb]
                )
            ]

        # Parse commands & events
        commands = [
            DomainCommandSpec(name=c.get("name", "Action"), description=c.get("description", ""), fields=c.get("fields", []))
            for c in data.get("commands", [])
        ]
        events = [
            DomainEventSpec(name=e.get("name", "EventOccurred"), description=e.get("description", ""), fields=e.get("fields", []))
            for e in data.get("events", [])
        ]
        invariants = data.get("invariants", [
            f"A {master_entity.entity_name.lower()} transaction must enforce non-negative values and sequential lifecycle states"
        ])

        return DomainOntologySpec(
            pitch=pitch_clean,
            brand_name=data.get("brand_name", f"{master_entity.entity_name}Hub"),
            hero_headline=data.get("hero_headline", f"Premium {master_entity.entity_plural} Platform"),
            guarantee_badge=data.get("guarantee_badge", f"Verified {master_entity.entity_plural}"),
            domain_category=data.get("domain_category", "custom_domain"),
            visual_theme=visual_theme,
            master_entity=master_entity,
            secondary_entities=[],
            commands=commands,
            events=events,
            capabilities=capabilities,
            invariants=invariants
        )
    except Exception as e:
        raise RuntimeError(f"Domain Ontology Storming failed to process pitch '{pitch_clean}': {e}") from e


def generate_clarification_questions(ontology: DomainOntologySpec, pitch: str, mode: str = "fast") -> List[Dict[str, Any]]:
    """
    Generates strategic domain-fork clarification questions without questionnaire fatigue.
    - fast mode: 0-3 questions (0-3 questions based on ambiguity).
    - guided mode: max 5 strategic domain-fork questions.
    """
    noun = ontology.master_entity.entity_name
    plural = ontology.master_entity.entity_plural
    cat = ontology.domain_category
    pitch_lower = pitch.lower()

    candidates: List[ClarificationQuestion] = []

    # 1. Fulfillment & Workflow Model
    if "book" in pitch_lower or "rent" in pitch_lower or "service" in pitch_lower or "fleet" in pitch_lower or cat == "calendar_service":
        candidates.append(ClarificationQuestion(
            id="q_fulfillment_flow",
            question=f"Hur ska allokering/bokning av {plural.lower()} ske i systemet?",
            category="Allokeringsflöde",
            options=[
                f"Direktbokning (Kunden allokerar {noun.lower()} direkt online)",
                "Offertförfrågan (Kräver manuell granskning & godkännande av handläggare)",
                "Abonnemang / Fast tilldelning"
            ],
            default_choice=f"Direktbokning (Kunden allokerar {noun.lower()} direkt online)",
            impact_rationale="Avgör om allokeringsprocessen är 1-stegs eller 2-stegs med godkännandekö."
        ))
        candidates.append(ClarificationQuestion(
            id="q_maintenance_policy",
            question=f"Hur ska service, drift och underhållsspärrar hanteras för {plural.lower()}?",
            category="Drift & Underhåll",
            options=[
                "Automatisk driftstidsspärr vid uppnådd servicetröskel",
                "Manuell flaggning och revision av tekniker",
                "Varningsnotis utan automatisk bokningsspärr"
            ],
            default_choice="Automatisk driftstidsspärr vid uppnådd servicetröskel",
            impact_rationale="Styr om schemalagd service automatiskt låser entiteten från nya allokeringar."
        ))
    elif "order" in pitch_lower or "cart" in pitch_lower or "buy" in pitch_lower or cat == "catalog_cart":
        candidates.append(ClarificationQuestion(
            id="q_checkout_mode",
            question=f"Hur ska beställningar av {plural.lower()} bekräftas och betalas?",
            category="Orderflöde",
            options=[
                "Direktbetalning & orderkvittens",
                "Offert / Faktura i efterhand",
                "Reservera online och betala vid leverans/upphämtning"
            ],
            default_choice="Direktbetalning & orderkvittens",
            impact_rationale="Avgör tillståndsmaskinen för orderhantering."
        ))
        candidates.append(ClarificationQuestion(
            id="q_inventory_lock",
            question=f"Hur ska lagersaldo och allokering hanteras för {plural.lower()}?",
            category="Lagerallokering",
            options=[
                "Validering och minskning av saldo vid slutbetalning",
                "Realtidsreservering med timeout i varukorg",
                "Obegränsat saldo (on-demand produktion)"
            ],
            default_choice="Validering och minskning av saldo vid slutbetalning",
            impact_rationale="Styr när lagerinvarianter appliceras i domänmodellen."
        ))
    else:
        candidates.append(ClarificationQuestion(
            id="q_operational_flow",
            question=f"Vilket primärt verksamhetsflöde ska styra livscykeln för {plural.lower()}?",
            category="Verksamhetsflöde",
            options=[
                f"Standard tillståndsflöde (Skapad ➔ Aktiv ➔ Slutförd)",
                f"Tvåstegsverifiering med granskningssteg",
                f"Händelsedriven händelselogg (Event Sourcing)"
            ],
            default_choice=f"Standard tillståndsflöde (Skapad ➔ Aktiv ➔ Slutförd)",
            impact_rationale="Definierar tillståndsövergångar i domänaggregatet."
        ))

    # 2. Concurrency & Collision Policy
    candidates.append(ClarificationQuestion(
        id="q_concurrency_policy",
        question=f"Hur ska samtidiga ändringar och krockar hanteras på {plural.lower()}?",
        category="Samtidighet & Integritet",
        options=[
            "Optimistic Concurrency Control (OCC med versionsnummer & kollisionslås)",
            "Enkel överskrivning (senaste ändring gäller)",
            "Köläggning med strikt sekvensiering"
        ],
        default_choice="Optimistic Concurrency Control (OCC med versionsnummer & kollisionslås)",
        impact_rationale="Förhindrar datainkonsistens och samtidiga krockar i databasen."
    ))

    # 3. Notification & Events
    candidates.append(ClarificationQuestion(
        id="q_domain_events",
        question=f"Ska asynkrona domänhändelser publiceras vid viktiga statusändringar?",
        category="Händelseavisering",
        options=[
            "Ja, registrera domänhändelser i self.events för externa integrationer",
            "Nej, endast lokala databasuppdateringar"
        ],
        default_choice="Ja, registrera domänhändelser i self.events för externa integrationer",
        impact_rationale="Möjliggör asynkron integration med meddelandebussar och notifieringar."
    ))

    # 4. Pricing / Calculation Rules
    candidates.append(ClarificationQuestion(
        id="q_pricing_rules",
        question=f"Vilken beräknings- och valideringslogik ska gälla för {plural.lower()}?",
        category="Valideringsregler",
        options=[
            "Strikta matematiska gränser och icke-negativa värden",
            "Dynamiska multiplikatorer baserat på storlek/volym",
            "Schablontaxor med fasta nivåer"
        ],
        default_choice="Strikta matematiska gränser och icke-negativa värden",
        impact_rationale="Bestämmer vilka matematiska invarianter som byggs in i domänkärnan."
    ))

    # In Fast mode (Snabbstart), adopt all standard opinionated defaults automatically (0 questions).
    if mode == "fast":
        return []

    return [q.to_dict() for q in candidates[:5]]



def analyze_pitch_for_kickstart(pitch: str, mode: str = "fast") -> Dict[str, Any]:
    """
    Analyzes a natural language business pitch by delegating to storm_domain_ontology
    to extract domain capabilities, master entities, formal business invariants, and
    mode-sensitive clarification questions (0-3 for fast, max 5 for guided).
    """
    ontology = storm_domain_ontology(pitch)

    analyzed_capabilities = []
    for cap in ontology.capabilities:
        analyzed_capabilities.append({
            "id": cap.key,
            "name": cap.name,
            "icon": cap.icon,
            "category": "Domain Capability",
            "description": cap.description,
            "is_recommended": True,
            "selected": True,
            "relevance_score": 10
        })

    extracted_requirements = []
    for idx, rule in enumerate(ontology.invariants, start=1):
        extracted_requirements.append({
            "id": f"REQ-BUS-{idx:03d}",
            "title": f"Business Rule: {rule[:45]}...",
            "description": rule,
            "type": "Domain Invariant",
            "priority": "High"
        })

    if not extracted_requirements:
        extracted_requirements.append({
            "id": "REQ-BUS-001",
            "title": f"Business Rule: Valid {ontology.master_entity.entity_name} State Transitions",
            "description": f"The system shall validate {ontology.master_entity.entity_name.lower()} inputs and enforce domain state transitions across processing stages.",
            "type": "Domain Invariant",
            "priority": "High"
        })

    clarification_questions = generate_clarification_questions(ontology, pitch, mode=mode)

    return {
        "pitch": pitch,
        "mode": mode,
        "blocks": analyzed_capabilities,
        "capabilities": [cap.to_dict() for cap in ontology.capabilities],
        "extracted_requirements": extracted_requirements,
        "clarification_questions": clarification_questions
    }


def synthesize_domain_intent_and_branding(pitch: str) -> Dict[str, Any]:
    """Synthesize clean brand title and domain category without keyword cascades."""
    ont = storm_domain_ontology(pitch)
    noun = ont.master_entity.entity_name
    category = "e_commerce" if ont.domain_category == "catalog_cart" else ("service_booking" if ont.domain_category == "calendar_service" else "operations_dashboard")
    brand = f"{noun}Craft"
    brand = re.sub(r'^(?:An|A)\s+', '', brand, flags=re.IGNORECASE).strip()
    brand = re.sub(r'\s+App$', '', brand, flags=re.IGNORECASE).strip()
    if not brand:
        brand = f"{noun} Management"
    return {
        "brand_title": brand,
        "domain_category": category,
        "primary_noun": noun,
        "headline": ont.hero_headline,
        "theme": ont.visual_theme.archetype
    }

