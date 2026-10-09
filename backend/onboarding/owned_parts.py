"""
Owned parts: an entity that only exists inside another is stored inside its owner.

The decomposition marks such an entity itself: it is not an aggregate root and it relates to one root (a board square
belongs to a game session, a line item to an order). Stored as a collection of its own, the owner's methods and rules
cannot see it: a chess game then knows whose turn it is and has no board. So the owner's aggregate gains a list
attribute holding its parts, and the part stops being a stored entity: no module, repository, router or client of
its own. It is read and changed through its owner, as an aggregate's parts are.

Only a part with exactly one owning root is embedded. Anything else stays the collection the decomposition made it.
"""

from typing import Dict, List, Optional

from onboarding.router_engine import AttributeSpec, BusinessSpec, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import _pluralize, to_snake_case


def _owner_of(part: EntitySpec, roots: List[EntitySpec]) -> Optional[EntitySpec]:
    """The one aggregate root this entity belongs to, by either side's relationship."""
    owners = []
    for root in roots:
        owns = any(r.get("target") == part.name and r.get("relation_type") == "one_to_many" for r in root.relationships)
        belongs = any(r.get("target") == root.name and r.get("relation_type") == "many_to_one" for r in part.relationships)
        if owns or belongs:
            owners.append(root)
    return owners[0] if len(owners) == 1 else None


def embed_owned_parts(structure: DomainStructureSchema, specs: List[BusinessSpec]) -> Dict[str, str]:
    """Moves every owned part into its owner as a list attribute, and points the specs that targeted a part at its
    owner (the class that now holds it). Changes `structure` and `specs` in place; returns {part: owner}."""
    roots = [e for e in structure.entities if e.is_aggregate_root]
    owners: Dict[str, str] = {}
    for part in [e for e in structure.entities if not e.is_aggregate_root]:
        owner = _owner_of(part, roots)
        if owner is None:
            continue
        back_reference = f"{to_snake_case(owner.name)}_id"
        owner.attributes.append(AttributeSpec(
            name=_pluralize(to_snake_case(part.name)), type="list", required=False, default_value=[],
            item_name=part.name, item_attributes=[a for a in part.attributes if a.name != back_reference]))
        owner.relationships = [r for r in owner.relationships if r.get("target") != part.name]
        structure.entities.remove(part)
        owners[part.name] = owner.name
    for spec in specs:
        if spec.target_aggregate in owners:
            spec.target_aggregate = owners[spec.target_aggregate]
    return owners
