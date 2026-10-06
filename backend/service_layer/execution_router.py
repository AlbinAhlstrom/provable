"""
Execution Router — Provable Hybrid Autonomous Engine.
Coordinates the Excavator and the Scalpel:
- Greenfield One-Shotting ➔ Native Scaffold + OpenCode Gateway
- Precision In-File Editing & Class Extension ➔ Aider Bridge
- Resilient Fallback ➔ Native Provable Synthesis Engine
"""

from enum import Enum
from typing import Dict, Any, Optional, List

from onboarding.wayfinder import BddClause
from service_layer.opencode_gateway import OpenCodeGateway
from service_layer.aider_bridge import ProvableAiderBridge


class TaskIntent(str, Enum):
    GREENFIELD_ONE_SHOT = "GREENFIELD_ONE_SHOT"
    PRECISION_EDIT = "PRECISION_EDIT"
    DIAGNOSTIC_REPAIR = "DIAGNOSTIC_REPAIR"


class ExecutionRouter:
    """
    Intelligent dispatch router selecting the optimal execution engine
    based on task lifecycle stage and local daemon capabilities.
    """

    def __init__(
        self,
        opencode_gateway: Optional[OpenCodeGateway] = None,
        aider_bridge: Optional[ProvableAiderBridge] = None
    ):
        self.opencode = opencode_gateway or OpenCodeGateway()
        self.aider = aider_bridge or ProvableAiderBridge()

    def get_system_capabilities(self) -> Dict[str, Any]:
        """Probes available local runtime engines and returns capability report."""
        opencode_online = self.opencode.is_available()
        aider_ready = self.aider.is_available()

        return {
            "native_scaffold_ready": True,
            "opencode_connected": opencode_online,
            "aider_available": aider_ready,
            "active_greenfield_engine": "OPENCODE_GATEWAY" if opencode_online else "NATIVE_SCAFFOLD",
            "active_precision_engine": "AIDER_BRIDGE" if aider_ready else "NATIVE_SYNTHESIS"
        }

    def route_task(
        self,
        intent: TaskIntent,
        prompt: str,
        target_files: Optional[List[str]] = None,
        bdd_clause: Optional[BddClause] = None,
        workspace_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Routes a task to the optimal execution engine with guaranteed fallback."""
        capabilities = self.get_system_capabilities()

        if intent == TaskIntent.GREENFIELD_ONE_SHOT:
            if capabilities["opencode_connected"]:
                return {
                    "engine": "OPENCODE_GATEWAY",
                    "status": "DISPATCHING_OPENCODE",
                    "action": "DELEGATE_TO_OPENCODE_SERVER",
                    "prompt": prompt
                }
            else:
                return {
                    "engine": "NATIVE_SCAFFOLD",
                    "status": "READY_FOR_SYNTHESIS",
                    "action": "EXECUTE_NATIVE_FASTAPI_VITE_SCAFFOLD",
                    "prompt": prompt
                }

        elif intent in (TaskIntent.PRECISION_EDIT, TaskIntent.DIAGNOSTIC_REPAIR):
            if capabilities["aider_available"]:
                return {
                    "engine": "AIDER_BRIDGE",
                    "status": "READY_FOR_AIDER",
                    "action": "EXECUTE_SURGICAL_IN_FILE_DIFF",
                    "target_files": target_files or [],
                    "bdd": bdd_clause.to_dict() if bdd_clause else None
                }
            else:
                return {
                    "engine": "NATIVE_SYNTHESIS",
                    "status": "FALLBACK_NATIVE",
                    "action": "EXECUTE_INTERNAL_RULE_MUTATION",
                    "target_files": target_files or [],
                    "bdd": bdd_clause.to_dict() if bdd_clause else None
                }

        return {
            "engine": "NATIVE_SYNTHESIS",
            "status": "UNKNOWN_INTENT_FALLBACK",
            "prompt": prompt
        }
