"""
Unit tests for Universal Domain Ontology Stormer.
Verifies that arbitrary pitches (Scuba Diving, Heavy Machinery, Pizza, Tutoring, etc.)
produce rich, typed DomainOntologySpec objects with ZERO domain-specific hardcoded switchboards.
"""

import pytest
from onboarding.domain_ontology import (
    storm_domain_ontology,
    DomainOntologySpec,
    MasterEntitySpec,
    EntityAttributeSpec
)

def test_ontology_stormer_arbitrary_domain_scuba():
    pitch = "An app to book scuba diving excursions and boat charters in Maui"
    ontology = storm_domain_ontology(pitch)

    assert isinstance(ontology, DomainOntologySpec)
    assert ontology.domain_category in ["calendar_service", "catalog_cart"]
    assert ontology.brand_name != ""
    assert ontology.hero_headline != ""
    assert ontology.guarantee_badge != ""
    assert isinstance(ontology.master_entity, MasterEntitySpec)
    assert ontology.master_entity.entity_name != ""
    assert ontology.master_entity.entity_plural != ""
    assert ontology.master_entity.action_verb != ""
    assert len(ontology.master_entity.attributes) >= 2
    assert len(ontology.master_entity.seed_items) >= 2
    
    # Assert master entity has attributes like name, price
    attr_names = [a.name for a in ontology.master_entity.attributes]
    assert "name" in attr_names
    assert "price" in attr_names or "rate" in attr_names


def test_ontology_stormer_arbitrary_domain_heavy_machinery():
    pitch = "Commercial heavy construction equipment rental and job site delivery"
    ontology = storm_domain_ontology(pitch)

    assert isinstance(ontology, DomainOntologySpec)
    assert ontology.brand_name != ""
    assert ontology.master_entity.entity_name != ""
    assert len(ontology.master_entity.seed_items) >= 2
    # Ensure zero babysitter or pizza leakage
    ontology_str = str(ontology.__dict__).lower()
    assert "sitter" not in ontology_str
    assert "babysit" not in ontology_str
    assert "margherita" not in ontology_str


def test_ontology_stormer_standard_pizza():
    pitch = "An app to order pizzas"
    ontology = storm_domain_ontology(pitch)

    assert isinstance(ontology, DomainOntologySpec)
    assert ontology.master_entity.entity_name.lower() in ["pizza", "item", "product", "dish"]
    assert len(ontology.master_entity.seed_items) >= 2
    # Verify seed items have name and price
    for item in ontology.master_entity.seed_items:
        assert "name" in item
        assert "price" in item
