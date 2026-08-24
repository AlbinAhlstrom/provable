"""
Repository Adapter Pattern over Requirement domain model.
Includes AbstractRequirementRepository interface, SqliteRequirementRepository, and FakeRequirementRepository.
"""

import abc
import os
from typing import List, Optional, Set, Dict
from domain.model import Requirement, Project, KickstartState
import db.store as store

class AbstractRequirementRepository(abc.ABC):
    def __init__(self):
        self.seen: Set[Requirement] = set()

    def add(self, requirement: Requirement) -> None:
        self._add(requirement)
        self.seen.add(requirement)

    def get(self, req_id: str) -> Optional[Requirement]:
        req = self._get(req_id)
        if req:
            self.seen.add(req)
        return req

    def list(self) -> List[Requirement]:
        reqs = self._list()
        for r in reqs:
            self.seen.add(r)
        return reqs

    def delete(self, req_id: str) -> None:
        self._delete(req_id)
        self.seen = {r for r in self.seen if r.id != req_id}

    @abc.abstractmethod
    def _add(self, requirement: Requirement) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, req_id: str) -> Optional[Requirement]:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self) -> List[Requirement]:
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, req_id: str) -> None:
        raise NotImplementedError


class SqliteRequirementRepository(AbstractRequirementRepository):
    """Real database repository wrapping store.py SQLite access layer."""
    def _add(self, requirement: Requirement) -> None:
        store.create_requirement({
            "id": requirement.id,
            "title": requirement.title,
            "description": requirement.description,
            "status": requirement.status,
            "priority": requirement.priority,
            "type": requirement.type,
            "parentId": requirement.parent_id,
            "layer": requirement.layer,
            "tests": requirement.tests,
            "assignedAgents": requirement.assigned_agents,
            "proposedCode": requirement.proposed_code,
            "feedback": requirement.feedback
        })
        if requirement.tests:
            store.replace_test_results_for_requirement(requirement.id, requirement.tests)

    def _get(self, req_id: str) -> Optional[Requirement]:
        raw = store.get_requirement(req_id)
        if not raw:
            return None
        frontend_list = store.get_requirements_for_frontend()
        match = next((r for r in frontend_list if r["id"] == req_id), None)
        tests = match.get("tests", []) if match else []
        return Requirement(
            id=raw.get("id"),
            title=raw.get("title", ""),
            description=raw.get("description", ""),
            status=raw.get("status", "Backlog"),
            priority=raw.get("priority", "High"),
            type=raw.get("type", "Requirement"),
            parent_id=raw.get("parentId") or raw.get("parent_id"),
            layer=raw.get("layer", "LOGIC"),
            tests=tests,
            assigned_agents=raw.get("assignedAgents") or raw.get("assigned_agents") or [],
            proposed_code=raw.get("proposedCode") or raw.get("proposed_code"),
            feedback=raw.get("feedback"),
            dependencies=raw.get("dependencies") or [],
            component_type=raw.get("component_type"),
            component_meta=raw.get("component_meta")
        )

    def _list(self) -> List[Requirement]:
        raw_list = store.get_requirements_for_frontend()
        results = []
        for raw in raw_list:
            results.append(Requirement(
                id=raw.get("id"),
                title=raw.get("title", ""),
                description=raw.get("description", ""),
                status=raw.get("status", "Backlog"),
                priority=raw.get("priority", "High"),
                type=raw.get("type", "Requirement"),
                parent_id=raw.get("parentId") or raw.get("parent_id"),
                layer=raw.get("layer", "LOGIC"),
                tests=raw.get("tests") or [],
                assigned_agents=raw.get("assignedAgents") or raw.get("assigned_agents") or [],
                proposed_code=raw.get("proposedCode") or raw.get("proposed_code"),
                feedback=raw.get("feedback"),
                dependencies=raw.get("dependencies") or [],
                component_type=raw.get("component_type"),
                component_meta=raw.get("component_meta")
            ))
        return results

    def _delete(self, req_id: str) -> None:
        store.delete_requirement_cascade(req_id)


class FakeRequirementRepository(AbstractRequirementRepository):
    """In-memory fake repository for lightning-fast unit tests."""
    def __init__(self, requirements: Optional[List[Requirement]] = None):
        super().__init__()
        self._requirements: Dict[str, Requirement] = {
            r.id: r for r in (requirements or [])
        }

    def _add(self, requirement: Requirement) -> None:
        self._requirements[requirement.id] = requirement

    def _get(self, req_id: str) -> Optional[Requirement]:
        return self._requirements.get(req_id)

    def _list(self) -> List[Requirement]:
        return list(self._requirements.values())

    def _delete(self, req_id: str) -> None:
        to_delete = [r_id for r_id, r in self._requirements.items() if r.parent_id == req_id]
        for child_id in to_delete:
            self._delete(child_id)
        self._requirements.pop(req_id, None)


class AbstractProjectRepository(abc.ABC):
    def __init__(self):
        self.seen: Set[Project] = set()

    def add(self, project: Project) -> None:
        self._add(project)
        self.seen.add(project)

    def get(self, path: str) -> Optional[Project]:
        proj = self._get(path)
        if proj:
            self.seen.add(proj)
        return proj

    def list(self) -> List[Project]:
        projs = self._list()
        for p in projs:
            self.seen.add(p)
        return projs

    def set_active(self, path: str) -> None:
        self._set_active(path)

    @abc.abstractmethod
    def _add(self, project: Project) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, path: str) -> Optional[Project]:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self) -> List[Project]:
        raise NotImplementedError

    @abc.abstractmethod
    def _set_active(self, path: str) -> None:
        raise NotImplementedError


class SqliteProjectRepository(AbstractProjectRepository):
    """Repository wrapping integrations.yaml config and active workspace state."""
    def _add(self, project: Project) -> None:
        import config_loader
        config_loader.add_project(project.name, project.path)

    def _get(self, path: str) -> Optional[Project]:
        projs = self._list()
        norm_path = os.path.normcase(os.path.abspath(path))
        for p in projs:
            if os.path.normcase(os.path.abspath(p.path)) == norm_path:
                return p
        return None

    def _list(self) -> List[Project]:
        import config_loader
        projects = config_loader.get_all_projects()
        active_path = config_loader.get_workspace_base()
        norm_active = os.path.normcase(os.path.abspath(active_path)) if active_path else ""
        results = []
        for p in projects:
            p_path = p.get("path", "")
            norm_p = os.path.normcase(os.path.abspath(p_path)) if p_path else ""
            results.append(Project(
                name=p.get("name", os.path.basename(p_path)),
                path=p_path,
                active=(norm_p == norm_active)
            ))
        return results

    def _set_active(self, path: str) -> None:
        import config_loader
        config_loader.set_active_project(path)


class FakeProjectRepository(AbstractProjectRepository):
    """In-memory Fake Project repository for lightning-fast unit tests."""
    def __init__(self, projects: Optional[List[Project]] = None):
        super().__init__()
        self._projects: Dict[str, Project] = {}
        if projects is not None:
            for p in projects:
                norm_p = os.path.normcase(os.path.abspath(p.path))
                self._projects[norm_p] = p

    def _add(self, project: Project) -> None:
        norm_p = os.path.normcase(os.path.abspath(project.path))
        self._projects[norm_p] = project

    def _get(self, path: str) -> Optional[Project]:
        norm_p = os.path.normcase(os.path.abspath(path))
        return self._projects.get(norm_p)

    def _list(self) -> List[Project]:
        return list(self._projects.values())

    def _set_active(self, path: str) -> None:
        norm_target = os.path.normcase(os.path.abspath(path))
        found = False
        for norm_p, proj in self._projects.items():
            if norm_p == norm_target:
                proj.active = True
                found = True
            else:
                proj.active = False
        if not found:
            new_proj = Project(name=os.path.basename(path) or "Project", path=os.path.abspath(path), active=True)
            self._add(new_proj)


class AbstractKickstartRepository(abc.ABC):
    @abc.abstractmethod
    def get(self) -> KickstartState:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, state: KickstartState) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> None:
        raise NotImplementedError


class SqliteKickstartRepository(AbstractKickstartRepository):
    """Real database repository wrapping store.py kickstart state SQLite access."""
    def get(self) -> KickstartState:
        raw = store.get_kickstart_state()
        raw_schemas = raw.get("entity_schemas", {})
        entity_schemas = {}
        for k, v in raw_schemas.items():
            if isinstance(v, dict):
                attrs = [
                    EntityAttribute(
                        name=a.get("name", ""),
                        type=a.get("type", "string"),
                        required=bool(a.get("required", False)),
                        default_value=a.get("default_value")
                    ) if isinstance(a, dict) else a
                    for a in v.get("attributes", [])
                ]
                entity_schemas[k] = DomainEntitySchema(
                    entity_name=v.get("entity_name", "Item"),
                    canonical_key=v.get("canonical_key", k),
                    attributes=attrs
                )
            elif isinstance(v, DomainEntitySchema):
                entity_schemas[k] = v

        return KickstartState(
            business_pitch=raw.get("business_pitch", "An app to order pizzas"),
            blocks=raw.get("blocks", []),
            extracted_requirements=raw.get("extracted_requirements", []),
            synthesized=raw.get("synthesized", False),
            custom_fixtures=raw.get("custom_fixtures", {}),
            entity_schemas=entity_schemas
        )

    def save(self, state: KickstartState) -> None:
        store.save_kickstart_state(state.to_dict())

    def clear(self) -> None:
        try:
            conn = store.get_connection()
            conn.execute("DELETE FROM kickstart_state")
            conn.commit()
            conn.close()
        except Exception:
            pass


class FakeKickstartRepository(AbstractKickstartRepository):
    """In-memory fake repository for kickstart session state."""
    def __init__(self, state: Optional[KickstartState] = None):
        self._state = state or KickstartState()

    def get(self) -> KickstartState:
        return self._state

    def save(self, state: KickstartState) -> None:
        self._state = state

    def clear(self) -> None:
        self._state = KickstartState()




