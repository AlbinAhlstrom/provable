"""
Knowledge Graph Core Models.
Typed representation of code entities, relations, and subgraphs with provenance.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


@dataclass
class GraphNode:
    id: str
    name: str
    type: str  # e.g., 'AggregateRoot', 'DomainEntity', 'FastAPIRouter', 'Endpoint', 'Repository', 'UnitOfWork', 'Invariant'
    file_path: str = ""
    line_start: int = 0
    line_end: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdge:
    source: str
    target: str
    relation: str  # e.g., 'MAINTAINS_INVARIANT', 'INVOKES_UOW', 'PERSISTED_BY', 'COORDINATED_BY', 'EXPOSES_ENDPOINT', 'CALLS'
    evidence: str = ""
    file_path: str = ""
    line_number: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SubGraphResult:
    query_entities: List[str]
    nodes: List[GraphNode]
    edges: List[GraphEdge]

    def to_triples_markdown(self) -> str:
        """
        Serialize subgraph into compact, provable markdown lines:
        (head:Type)-[RELATION]->(tail:Type) | file:line | evidence
        """
        if not self.edges and not self.nodes:
            return "_No matching graph nodes found._"

        lines = []
        node_map = {n.id: n for n in self.nodes}

        # First list relevant nodes
        lines.append("### Matched Graph Entities")
        for node in self.nodes:
            loc = f" (`{node.file_path}:{node.line_start}`)" if node.file_path else ""
            lines.append(f"- **{node.name}** (`{node.type}`){loc}")

        if self.edges:
            lines.append("\n### Verified Relationships & Invariant Paths")
            for edge in self.edges:
                src = node_map.get(edge.source)
                tgt = node_map.get(edge.target)
                src_name = f"{src.name}:{src.type}" if src else edge.source
                tgt_name = f"{tgt.name}:{tgt.type}" if tgt else edge.target
                loc = f" | `{edge.file_path}:{edge.line_number}`" if edge.file_path else ""
                ev = f" | _{edge.evidence}_" if edge.evidence else ""
                lines.append(f"- `({src_name})` --[{edge.relation}]--> `({tgt_name})`{loc}{ev}")

        return "\n".join(lines)
