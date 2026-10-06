"""
GraphRAG Subgraph Retriever & Path Serializer.
Resolves queries against graph entities and extracts compact, provable 1-to-2 hop subgraphs.
"""

from typing import List, Set, Dict, Any, Optional
import networkx as nx

from knowledge.models import GraphNode, GraphEdge, SubGraphResult
from knowledge.fusion import CrossLayerEntityFuser


class GraphRAGRetriever:
    """
    Retrieves grounded subgraphs with line-level provenance for LLM context injection.
    """

    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

    def link_entities(self, query: str) -> List[str]:
        """
        Finds graph node IDs matching keywords or stems in the query.
        """
        query_lower = query.lower()
        query_stems = {CrossLayerEntityFuser.extract_canonical_stem(w) for w in query_lower.split() if len(w) > 2}

        matched_node_ids = set()

        for node_id, data in self.graph.nodes(data=True):
            node: GraphNode = data.get("data")
            if not node:
                continue

            node_name_lower = node.name.lower()
            # Exact name or id match
            if node_name_lower in query_lower or node.id.lower() in query_lower:
                matched_node_ids.add(node_id)
                continue

            # Alias match
            for alias in node.aliases:
                if alias.lower() in query_lower:
                    matched_node_ids.add(node_id)
                    break

            # Stem match
            if node.type in ("AggregateRoot", "CanonicalConcept", "UnitOfWork", "FastAPIRouter"):
                stem = CrossLayerEntityFuser.extract_canonical_stem(node.name)
                if stem in query_stems:
                    matched_node_ids.add(node_id)

        return list(matched_node_ids)

    def retrieve_subgraph(self, query: str, max_hops: int = 1, max_nodes: int = 25) -> SubGraphResult:
        """
        Extracts the k-hop neighborhood around matched query entities.
        """
        seed_nodes = self.link_entities(query)
        if not seed_nodes:
            return SubGraphResult(query_entities=[], nodes=[], edges=[])

        collected_node_ids: Set[str] = set(seed_nodes)
        frontier: Set[str] = set(seed_nodes)

        # Expand k-hops
        for _ in range(max_hops):
            next_frontier: Set[str] = set()
            for current_node in frontier:
                # Outgoing edges
                for _, target, _ in self.graph.out_edges(current_node, keys=True):
                    if target not in collected_node_ids:
                        next_frontier.add(target)
                        collected_node_ids.add(target)

                # Incoming edges
                for source, _, _ in self.graph.in_edges(current_node, keys=True):
                    if source not in collected_node_ids:
                        next_frontier.add(source)
                        collected_node_ids.add(source)

                if len(collected_node_ids) >= max_nodes:
                    break

            frontier = next_frontier
            if len(collected_node_ids) >= max_nodes:
                break

        # Collect node and edge objects
        nodes: List[GraphNode] = []
        for nid in collected_node_ids:
            data = self.graph.nodes[nid].get("data")
            if data:
                nodes.append(data)

        edges: List[GraphEdge] = []
        for u, v, k, edge_data in self.graph.edges(keys=True, data=True):
            if u in collected_node_ids and v in collected_node_ids:
                edge: GraphEdge = edge_data.get("data")
                if edge:
                    edges.append(edge)

        return SubGraphResult(
            query_entities=[self.graph.nodes[nid]["data"].name for nid in seed_nodes if nid in self.graph.nodes],
            nodes=nodes,
            edges=edges
        )
