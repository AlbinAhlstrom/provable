"""
Components API Router — Handles active application component canvas, dynamic additions, deletions, sub-requirements, and suggestions.
"""

from fastapi import APIRouter
from entrypoints.schemas import (
    ComponentAddRequest, ComponentDeleteRequest,
    SubRequirementAddRequest, SubRequirementDeleteRequest,
    ComponentFixturesUpdateRequest, EntitySchemaUpdateRequest
)
from domain.model import resolve_canonical_feature
from service_layer import services
from service_layer.unit_of_work import SqliteUnitOfWork

router = APIRouter()


def get_active_domain_params() -> dict:
    """Assembles active domain schema via service layer and SqliteUnitOfWork."""
    return services.get_active_domain_params(uow=SqliteUnitOfWork())


def sync_workspace_app_shell():
    """Synchronizes workspace App.tsx shell live via service layer."""
    return services.sync_workspace_app_shell(uow=SqliteUnitOfWork())


@router.post("/api/components/add")
def add_dynamic_component(req: ComponentAddRequest):
    """
    Dynamically creates a new component requirement (premade or custom via LLM generation)
    and updates provable.db, requirements.sdoc, test suite, and workspace App.tsx.
    """
    try:
        uow = SqliteUnitOfWork()
        return services.add_dynamic_component(prompt=req.prompt, uow=uow)
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/components/delete")
def delete_dynamic_component(req: ComponentDeleteRequest):
    """
    Permanently deletes a component requirement tree from provable.db, strictDoc sdoc,
    and updates workspace App.tsx shell live.
    """
    try:
        uow = SqliteUnitOfWork()
        return services.delete_dynamic_component(canonical_key=req.canonical_key, uow=uow)
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/components/sub-requirements/add")
def add_sub_requirement_api(req: SubRequirementAddRequest):
    """Dynamically creates a sub-requirement under a parent component."""
    try:
        uow = SqliteUnitOfWork()
        return services.add_sub_requirement(
            parent_canonical_key=req.parent_canonical_key,
            prompt=req.prompt,
            uow=uow
        )
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/components/sub-requirements/delete")
def delete_sub_requirement_api(req: SubRequirementDeleteRequest):
    """Deletes a sub-requirement and updates workspace App.tsx live."""
    try:
        uow = SqliteUnitOfWork()
        return services.delete_sub_requirement(
            sub_id=req.sub_id,
            parent_canonical_key=req.parent_canonical_key,
            uow=uow
        )
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/api/components/suggestions")
def get_component_suggestions():
    """Returns 3 dynamic domain-relevant component suggestions based on current pitch."""
    try:
        uow = SqliteUnitOfWork()
        return services.get_component_suggestions(uow=uow)
    except Exception as e:
        return {"success": True, "suggestions": ["Loyalty Points", "Live Chat Support", "Customer Reviews"]}


@router.get("/api/components/fixtures")
def get_component_data_fixtures_api():
    """Returns active domain data fixtures grouped by canonical component key."""
    try:
        uow = SqliteUnitOfWork()
        return services.get_component_data_fixtures(uow=uow)
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/components/fixtures/update")
def update_component_data_fixtures_api(req: ComponentFixturesUpdateRequest):
    """Updates entity data fixtures for a component key and syncs workspace App.tsx live."""
    try:
        uow = SqliteUnitOfWork()
        return services.update_component_data_fixtures(
            canonical_key=req.canonical_key,
            fixtures=req.fixtures,
            uow=uow
        )
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/api/components/entities")
def get_component_entities_api():
    """Returns entity schemas and fixtures for active components."""
    try:
        uow = SqliteUnitOfWork()
        schemas_res = services.get_component_entity_schemas(uow=uow)
        fixtures_res = services.get_component_data_fixtures(uow=uow)
        return {
            "success": True,
            "schemas": schemas_res.get("schemas", {}),
            "fixtures": fixtures_res.get("fixtures", {})
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/api/components/entities/schema/update")
def update_component_entity_schema_api(req: EntitySchemaUpdateRequest):
    """Updates the entity schema definition for a component and syncs workspace App.tsx live."""
    try:
        uow = SqliteUnitOfWork()
        return services.update_component_entity_schema(
            canonical_key=req.canonical_key,
            entity_name=req.entity_name,
            attributes=[a.dict() for a in req.attributes],
            uow=uow
        )
    except Exception as e:
        return {"success": False, "error": str(e)}

