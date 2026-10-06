"""
AST-Driven Codebase Knowledge Graph Extractor.
Parses Python source code deterministically using `ast` and builds a Property Graph in NetworkX.
"""

import os
import ast
from typing import Dict, Any, List, Optional
import networkx as nx

from knowledge.models import GraphNode, GraphEdge


class CodebaseGraphExtractor:
    """
    Extracts Domain Entities, UoW, Repositories, Routers, Endpoints, and Invariants.
    """

    def __init__(self, backend_root: str):
        self.backend_root = os.path.abspath(backend_root)
        self.graph = nx.MultiDiGraph()

    def build_graph(self) -> nx.MultiDiGraph:
        """
        Runs the extraction pipeline across all architectural layers.
        """
        self._extract_domain_models()
        self._extract_repositories()
        self._extract_unit_of_work()
        self._extract_routers()
        self._link_layers()
        return self.graph

    def _add_node(self, node: GraphNode):
        self.graph.add_node(node.id, data=node)

    def _add_edge(self, edge: GraphEdge):
        self.graph.add_edge(edge.source, edge.target, key=edge.relation, data=edge)

    def _extract_domain_models(self):
        domain_file = os.path.join(self.backend_root, "domain", "model.py")
        if not os.path.exists(domain_file):
            return

        with open(domain_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=domain_file)

        # Check pure domain invariant: no FastAPI/ORM imports
        for item in tree.body:
            if isinstance(item, (ast.Import, ast.ImportFrom)):
                mod_name = item.module if isinstance(item, ast.ImportFrom) else ""
                names = [alias.name for alias in item.names]
                if mod_name in ("fastapi", "sqlalchemy", "pydantic") or any(n in ("fastapi", "sqlalchemy") for n in names):
                    viol_node = GraphNode(
                        id="inv_breach_impure_domain",
                        name="ImpureDomainModelBreach",
                        type="InvariantViolation",
                        file_path="backend/domain/model.py",
                        line_start=item.lineno,
                        attributes={"details": f"Direct import of {mod_name or names} in domain model"}
                    )
                    self._add_node(viol_node)

        # Identify known Aggregate Roots
        known_aggregates = {"Requirement", "Component", "Project", "Spec", "RuleCard", "RuleCardDeck"}

        for item in tree.body:
            if isinstance(item, ast.ClassDef):
                is_dataclass = any(
                    (isinstance(d, ast.Name) and d.id == "dataclass") or
                    (isinstance(d, ast.Call) and getattr(d.func, "id", "") == "dataclass")
                    for d in item.decorator_list
                )
                node_type = "AggregateRoot" if item.name in known_aggregates else "DomainEntity"

                fields = []
                has_default = False
                has_default_ordering_bug = False

                for stmt in item.body:
                    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                        field_name = stmt.target.id
                        default_val = stmt.value is not None
                        if default_val:
                            has_default = True
                        elif has_default:
                            has_default_ordering_bug = True
                        fields.append(field_name)

                node = GraphNode(
                    id=f"domain_{item.name.lower()}",
                    name=item.name,
                    type=node_type,
                    file_path="backend/domain/model.py",
                    line_start=item.lineno,
                    line_end=getattr(item, "end_lineno", item.lineno),
                    attributes={"fields": fields, "is_dataclass": is_dataclass},
                    aliases=[item.name.lower(), item.name]
                )
                self._add_node(node)

                # Link Invariant: NonDefaultArgsPrecedeDefault
                inv_node = GraphNode(
                    id="inv_non_default_args_precede_default",
                    name="NonDefaultArgsPrecedeDefault",
                    type="Invariant",
                    file_path="backend/domain/model.py",
                    attributes={"rule": "Non-default dataclass arguments must precede default arguments"}
                )
                self._add_node(inv_node)

                if has_default_ordering_bug:
                    viol = GraphNode(
                        id=f"inv_breach_default_ordering_{item.name.lower()}",
                        name=f"DefaultArgOrderingBreach_{item.name}",
                        type="InvariantViolation",
                        file_path="backend/domain/model.py",
                        line_start=item.lineno,
                        attributes={"details": f"Class {item.name} has non-default argument after default argument"}
                    )
                    self._add_node(viol)
                    self._add_edge(GraphEdge(
                        source=node.id,
                        target=viol.id,
                        relation="VIOLATES_INVARIANT",
                        file_path="backend/domain/model.py",
                        line_number=item.lineno
                    ))
                else:
                    self._add_edge(GraphEdge(
                        source=node.id,
                        target=inv_node.id,
                        relation="MAINTAINS_INVARIANT",
                        evidence="Valid dataclass field ordering",
                        file_path="backend/domain/model.py",
                        line_number=item.lineno
                    ))

    def _extract_repositories(self):
        repo_file = os.path.join(self.backend_root, "adapters", "repository.py")
        if not os.path.exists(repo_file):
            return

        with open(repo_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=repo_file)

        for item in tree.body:
            if isinstance(item, ast.ClassDef) and "Repository" in item.name:
                node = GraphNode(
                    id=f"repo_{item.name.lower()}",
                    name=item.name,
                    type="Repository",
                    file_path="backend/adapters/repository.py",
                    line_start=item.lineno,
                    line_end=getattr(item, "end_lineno", item.lineno),
                    aliases=[item.name.lower()]
                )
                self._add_node(node)

    def _extract_unit_of_work(self):
        uow_file = os.path.join(self.backend_root, "service_layer", "unit_of_work.py")
        if not os.path.exists(uow_file):
            return

        with open(uow_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=uow_file)

        for item in tree.body:
            if isinstance(item, ast.ClassDef) and "UnitOfWork" in item.name:
                node = GraphNode(
                    id=f"uow_{item.name.lower()}",
                    name=item.name,
                    type="UnitOfWork",
                    file_path="backend/service_layer/unit_of_work.py",
                    line_start=item.lineno,
                    line_end=getattr(item, "end_lineno", item.lineno),
                    aliases=["uow", item.name.lower()]
                )
                self._add_node(node)

    def _extract_routers(self):
        routers_dir = os.path.join(self.backend_root, "entrypoints", "routers")
        if not os.path.exists(routers_dir):
            return

        for fname in os.listdir(routers_dir):
            if not fname.endswith(".py") or fname == "__init__.py":
                continue

            fpath = os.path.join(routers_dir, fname)
            rel_path = os.path.relpath(fpath, os.path.dirname(self.backend_root)).replace("\\", "/")

            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=fpath)
            router_name = fname[:-3]
            router_node_id = f"router_{router_name}"

            router_node = GraphNode(
                id=router_node_id,
                name=f"{router_name.capitalize()}Router",
                type="FastAPIRouter",
                file_path=rel_path,
                line_start=1,
                aliases=[router_name, f"{router_name}_router", fname]
            )
            self._add_node(router_node)

            # Invariant check: Routers must NOT import db.store directly
            for item in tree.body:
                if isinstance(item, (ast.Import, ast.ImportFrom)):
                    mod = getattr(item, "module", "") or ""
                    names = [alias.name for alias in item.names]
                    if "db.store" in mod or "db.store" in names or mod == "store":
                        breach_id = f"inv_breach_store_import_{router_name}"
                        breach_node = GraphNode(
                            id=breach_id,
                            name=f"DirectStoreImportBreach_{router_name}",
                            type="InvariantViolation",
                            file_path=rel_path,
                            line_start=item.lineno,
                            attributes={"details": "Presentation router directly imported db.store bypassing UoW"}
                        )
                        self._add_node(breach_node)
                        self._add_edge(GraphEdge(
                            source=router_node_id,
                            target=breach_id,
                            relation="VIOLATES_INVARIANT",
                            file_path=rel_path,
                            line_number=item.lineno
                        ))

            # Extract endpoints and UoW dependencies
            for item in tree.body:
                if isinstance(item, ast.FunctionDef):
                    is_endpoint = False
                    http_method = "UNKNOWN"
                    path = ""

                    for dec in item.decorator_list:
                        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                            if getattr(dec.func.value, "id", "") == "router":
                                is_endpoint = True
                                http_method = dec.func.attr.upper()
                                if dec.args and isinstance(dec.args[0], ast.Constant):
                                    path = dec.args[0].value

                    if is_endpoint:
                        endpoint_id = f"ep_{router_name}_{item.name}"
                        ep_node = GraphNode(
                            id=endpoint_id,
                            name=f"{http_method} {path or item.name}",
                            type="Endpoint",
                            file_path=rel_path,
                            line_start=item.lineno,
                            line_end=getattr(item, "end_lineno", item.lineno),
                            attributes={"function": item.name, "http_method": http_method, "path": path}
                        )
                        self._add_node(ep_node)

                        self._add_edge(GraphEdge(
                            source=router_node_id,
                            target=endpoint_id,
                            relation="EXPOSES_ENDPOINT",
                            evidence=f"def {item.name}",
                            file_path=rel_path,
                            line_number=item.lineno
                        ))

                        # Check for UoW dependency in parameters
                        for arg in item.args.args:
                            if "uow" in arg.arg.lower():
                                # Link to AbstractUnitOfWork
                                self._add_edge(GraphEdge(
                                    source=endpoint_id,
                                    target="uow_abstractunitofwork",
                                    relation="INVOKES_UOW",
                                    evidence=f"{arg.arg}: AbstractUnitOfWork",
                                    file_path=rel_path,
                                    line_number=item.lineno
                                ))

    def _link_layers(self):
        """
        Links repositories to aggregates and UoW to repositories based on naming conventions.
        """
        # Link UoW -> Repositories
        if "uow_sqliteunitofwork" in self.graph.nodes:
            for node_id, data in list(self.graph.nodes(data=True)):
                node: GraphNode = data.get("data")
                if node and node.type == "Repository" and "Sqlite" in node.name:
                    self._add_edge(GraphEdge(
                        source="uow_sqliteunitofwork",
                        target=node.id,
                        relation="COORDINATES_REPOSITORY",
                        evidence="SqliteUnitOfWork.__enter__ coordinates repository",
                        file_path="backend/service_layer/unit_of_work.py",
                        line_number=50
                    ))

        # Link Repositories -> AggregateRoots
        for node_id, data in list(self.graph.nodes(data=True)):
            node: GraphNode = data.get("data")
            if node and node.type == "Repository":
                # Match e.g. SqliteRequirementRepository -> domain_requirement
                for agg_id, agg_data in list(self.graph.nodes(data=True)):
                    agg: GraphNode = agg_data.get("data")
                    if agg and agg.type == "AggregateRoot":
                        if agg.name.lower() in node.name.lower():
                            self._add_edge(GraphEdge(
                                source=node.id,
                                target=agg.id,
                                relation="PERSISTS_AGGREGATE",
                                evidence=f"{node.name} persists {agg.name}",
                                file_path=node.file_path,
                                line_number=node.line_start
                            ))
