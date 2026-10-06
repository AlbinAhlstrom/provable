"""
Unit tests for the Provable Knowledge Graph Engine (Workflows 2, 4, 7, 9).
Verifies AST extraction, invariant detection, cross-layer entity fusion, and GraphRAG retrieval.
"""

import os
import pytest
from knowledge.models import GraphNode, GraphEdge, SubGraphResult
from knowledge.extractor import CodebaseGraphExtractor
from knowledge.fusion import CrossLayerEntityFuser
from knowledge.retriever import GraphRAGRetriever


@pytest.fixture
def backend_path():
    # Points to the backend directory
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_ast_extractor_extracts_domain_and_routers(backend_path):
    extractor = CodebaseGraphExtractor(backend_path)
    graph = extractor.build_graph()

    # Must contain key aggregates
    assert "domain_requirement" in graph.nodes
    assert "domain_component" in graph.nodes
    assert "domain_project" in graph.nodes

    req_node: GraphNode = graph.nodes["domain_requirement"]["data"]
    assert req_node.type == "AggregateRoot"
    assert "backend/domain/model.py" in req_node.file_path
    assert req_node.line_start > 0

    # Must contain invariant check
    assert "inv_non_default_args_precede_default" in graph.nodes

    # Must contain routers
    assert "router_requirements" in graph.nodes
    assert "router_components" in graph.nodes

    # Check for endpoints
    endpoint_nodes = [d["data"] for n, d in graph.nodes(data=True) if d["data"].type == "Endpoint"]
    assert len(endpoint_nodes) > 10

    # Ensure zero direct db.store import breaches in presentation routers
    breaches = [d["data"] for n, d in graph.nodes(data=True) if d["data"].type == "InvariantViolation"]
    assert len(breaches) == 0, f"Detected unexpected architectural breaches: {breaches}"


def test_cross_layer_entity_fuser(backend_path):
    extractor = CodebaseGraphExtractor(backend_path)
    graph = extractor.build_graph()

    fuser = CrossLayerEntityFuser(graph)
    fused = fuser.fuse()

    # Must create canonical concept clusters for core cross-layer entities
    concept_nodes = {d["data"].name: d["data"] for n, d in fused.nodes(data=True) if d["data"].type == "CanonicalConcept"}

    assert "Requirement" in concept_nodes
    assert "Component" in concept_nodes

    req_concept = concept_nodes["Requirement"]
    assert req_concept.attributes["fused_node_count"] >= 2

    # Check that concept cluster has UNIFIES_LAYER_ENTITY edges to domain and router
    out_edges = fused.out_edges(req_concept.id, data=True)
    unified_targets = [v for u, v, d in out_edges if d.get("data", {}).relation == "UNIFIES_LAYER_ENTITY"]
    assert "domain_requirement" in unified_targets


def test_graph_rag_retriever_and_serialization(backend_path):
    extractor = CodebaseGraphExtractor(backend_path)
    graph = extractor.build_graph()
    CrossLayerEntityFuser(graph).fuse()

    retriever = GraphRAGRetriever(graph)

    # 1. Entity linking
    matched = retriever.link_entities("Requirement")
    assert len(matched) > 0
    assert any("requirement" in m.lower() for m in matched)

    # 2. Subgraph retrieval
    result = retriever.retrieve_subgraph("Requirement", max_hops=1)
    assert isinstance(result, SubGraphResult)
    assert len(result.nodes) > 0
    assert len(result.edges) > 0

    # 3. Serialization format
    md = result.to_triples_markdown()
    assert "### Matched Graph Entities" in md
    assert "### Verified Relationships & Invariant Paths" in md
    assert "backend/domain/model.py" in md
    assert "--[" in md and "]-->" in md


def test_graph_rag_nonexistent_query(backend_path):
    extractor = CodebaseGraphExtractor(backend_path)
    graph = extractor.build_graph()
    retriever = GraphRAGRetriever(graph)

    result = retriever.retrieve_subgraph("nonexistent_quantum_fluctuation_xyz")
    assert len(result.nodes) == 0
    assert len(result.edges) == 0
    assert "_No matching graph nodes found._" in result.to_triples_markdown()
