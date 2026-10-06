"""
Kickstart & Domain Modeling API Router — Handles pitch analysis, domain discovery, refinement, and code synthesis via DDD Service Layer & Unit of Work.
"""

from fastapi import APIRouter
from entrypoints.schemas import (
    DomainDiscoveryRequest, DomainRefinementRequest, DomainSynthesisRequest,
    KickstartAnalyzeRequest, KickstartSynthesisRequest
)
from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services

router = APIRouter()


@router.post("/api/domain/discover")
def discover_domain_model(req: DomainDiscoveryRequest):
    """Uses LLM Pitch Analysis Agent to extract candidate entities, services, exceptions, and invariants."""
    uow = SqliteUnitOfWork()
    return services.discover_domain_model(pitch=req.business_pitch, uow=uow)


@router.post("/api/domain/refine")
def refine_domain_model(req: DomainRefinementRequest):
    """Refines domain model schema based on developer natural language feedback."""
    uow = SqliteUnitOfWork()
    return services.refine_domain_model(current_schema=req.current_schema, feedback=req.feedback, uow=uow)


@router.get("/api/kickstart/state")
def get_kickstart_state():
    """Return active kickstart session state (pitch, blocks, requirements, synthesized status)."""
    uow = SqliteUnitOfWork()
    return services.get_kickstart_state(uow=uow)


@router.post("/api/kickstart/analyze")
def kickstart_analyze(req: KickstartAnalyzeRequest):
    """Analyze pitch to recommend pre-baked feature blocks and extract domain requirements."""
    uow = SqliteUnitOfWork()
    return services.analyze_kickstart_pitch(
        business_pitch=req.business_pitch,
        uow=uow
    )


@router.post("/api/kickstart/synthesize")
def kickstart_synthesize(req: KickstartSynthesisRequest):
    """Synthesize working application stack from selected feature blocks & pitch."""
    uow = SqliteUnitOfWork()
    return services.synthesize_kickstart_stack(
        business_pitch=req.business_pitch,
        pitch=req.pitch,
        selected_blocks=req.selected_blocks,
        selected_block_ids=req.selected_block_ids,
        requirements=req.requirements,
        extracted_requirements=req.extracted_requirements,
        uow=uow
    )


@router.post("/api/domain/synthesize")
def synthesize_domain_endpoint(req: DomainSynthesisRequest):
    """Synthesize domain code directly from schema."""
    uow = SqliteUnitOfWork()
    return services.synthesize_domain_schema(domain_schema=req.domain_schema, uow=uow)
