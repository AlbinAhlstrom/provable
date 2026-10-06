"""
System Capabilities & Hybrid Engine API Router.
Exposes real-time connectivity status for OpenCode, Aider, and Native Scaffold engines.
"""

from fastapi import APIRouter
from service_layer.execution_router import ExecutionRouter

router = APIRouter(prefix="/api/system", tags=["System Capabilities"])


@router.get("/capabilities")
def get_system_capabilities_endpoint():
    """Returns the availability and status of local AI engines (OpenCode, Aider, Native)."""
    execution_router = ExecutionRouter()
    return execution_router.get_system_capabilities()
