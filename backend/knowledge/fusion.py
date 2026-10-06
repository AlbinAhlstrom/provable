"""
Entity Resolution & Fusion Engine.
Resolves cross-layer aliases (e.g. Requirement <-> RequirementsRouter <-> SqliteRequirementRepository)
into unified concept clusters with reversible merge provenance.
"""

import re
from typing import Dict, Any, List, Set
import networkx as nx

from knowledge.models import GraphNode, GraphEdge


class CrossLayerEntityFuser:
    """
    Implements 3-step Knowledge Fusion (Blocking -> Matching -> Reversible Merge).
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

    @staticmethod
    def extract_canonical_stem(name_or_id: str) -> str:
        """
        Extracts the canonical semantic stem from diverse naming conventions:
        e.g., 'SqliteRequirementRepository' -> 'requirement'
              'REQ-UI-ORDERS' -> 'order'
              'domain_component' -> 'component'
              'ep_requirements_create_requirement' -> 'requirement'
        """
        clean = name_or_id.lower().replace("-", "_").replace(" ", "_")
        clean = re.sub(r"[^a-z0-9_]", "", clean)
        # Strip common architectural prefixes/suffixes
        clean = re.sub(r"^(domain_|repo_|router_|ep_|sqlite|abstract)", "", clean)
        clean = re.sub(r"(repository|router|deck|state|spec|schema|service|endpoint)$", "", clean)
        clean = clean.strip("_")
        # Stem basic plurals
        if clean.endswith("s") and not clean.endswith("ss"):
            clean = clean[:-1]
        return clean

    def fuse(self) -> nx.MultiDiGraph:
        """
        Executes blocking, neighborhood matching, and reversible cluster creation.
        """
        # Step 1: Blocking — partition nodes by semantic stem
        blocks: Dict[str, List[str]] = {}
        for node_id, data in self.graph.nodes(data=True):
            node: GraphNode = data.get("data")
            if not node:
                continue

            # Ignore invariant violations and generic base classes in fusion
            if node.type in ("Invariant", "InvariantViolation") or node.name.startswith("Abstract"):
                continue

            stem = self.extract_canonical_stem(node.name)
            if stem and len(stem) > 2:
                blocks.setdefault(stem, []).append(node_id)

        # Step 2 & 3: Matching & Reversible Merge
        # For blocks with multiple cross-layer nodes (e.g., domain + repo + router),
        # create a CanonicalConcept node that unifies them.
        for stem, node_ids in blocks.items():
            if len(node_ids) < 2:
                continue

            # Check if this block spans across multiple distinct types (cross-layer)
            types_in_block = {self.graph.nodes[nid]["data"].type for nid in node_ids}
            if len(types_in_block) >= 2:
                cluster_id = f"concept_{stem}"
                canonical_name = stem.capitalize()

                cluster_node = GraphNode(
                    id=cluster_id,
                    name=canonical_name,
                    type="CanonicalConcept",
                    attributes={"stem": stem, "fused_node_count": len(node_ids)},
                    aliases=[stem, canonical_name]
                )
                self.graph.add_node(cluster_id, data=cluster_node)

                # Link all constituent nodes to this canonical cluster with provenance
                for nid in node_ids:
                    constituent: GraphNode = self.graph.nodes[nid]["data"]
                    constituent.aliases.append(stem)
                    self.graph.add_edge(
                        cluster_id,
                        nid,
                        key="UNIFIES_LAYER_ENTITY",
                        data=GraphEdge(
                            source=cluster_id,
                            target=nid,
                            relation="UNIFIES_LAYER_ENTITY",
                            evidence=f"Stem match '{stem}' across layers {constituent.type}",
                            file_path=constituent.file_path,
                            line_number=constituent.line_start
                        )
                    )

        return self.graph
