#!/usr/bin/env python3
"""
Provable GraphRAG CLI.
Extracts AST property graph from backend, resolves cross-layer entities,
and retrieves grounded subgraphs with line-level provenance for agent context injection.

Usage:
  python graph_rag.py "Requirement Invariant"
  python graph_rag.py "Component Router" --hops 2
"""

import os
import sys
import argparse

# Ensure backend is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from knowledge.extractor import CodebaseGraphExtractor
from knowledge.fusion import CrossLayerEntityFuser
from knowledge.retriever import GraphRAGRetriever


def main():
    parser = argparse.ArgumentParser(description="Query Provable Codebase Knowledge Graph via GraphRAG")
    parser.add_argument("query", type=str, help="Natural language query or concept name (e.g. 'Requirement', 'UnitOfWork')")
    parser.add_argument("--hops", type=int, default=1, help="Max graph traversal hops (default: 1)")
    parser.add_argument("--backend-path", type=str, default=backend_dir, help="Path to backend directory")
    args = parser.parse_args()

    # Build and fuse property graph
    extractor = CodebaseGraphExtractor(args.backend_path)
    graph = extractor.build_graph()

    fuser = CrossLayerEntityFuser(graph)
    fused_graph = fuser.fuse()

    # Retrieve subgraph
    retriever = GraphRAGRetriever(fused_graph)
    result = retriever.retrieve_subgraph(args.query, max_hops=args.hops)

    print(result.to_triples_markdown())


if __name__ == "__main__":
    main()
