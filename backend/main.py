"""
Provable Backend Platform — Main Entrypoint & Backward Compatibility Shim.
Re-exports the FastAPI app, entrypoint schemas, routers, and helper functions
to guarantee 100% backward compatibility with all test suites, Uvicorn, and run.py.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from app import app, lifespan
from entrypoints.schemas import *
from entrypoints.routers.projects import (
    list_projects, get_active_project_settings, switch_project,
    add_project_endpoint, reset_all_projects
)
from entrypoints.routers.requirements import (
    get_requirements, update_requirements, delete_requirement,
    synthesize_requirements, create_folder, move_requirement,
    create_requirement, edit_requirement, update_requirement_param,
    toggle_requirement_feature
)
from entrypoints.routers.testing import (
    generate_test_for_requirement, get_coverage, create_test_case,
    fix_test_case, run_all_tests, run_single_test
)
from entrypoints.routers.kickstart import (
    discover_domain_model, refine_domain_model, get_kickstart_state,
    kickstart_analyze, kickstart_synthesize, synthesize_domain_endpoint
)
from entrypoints.routers.components import (
    add_dynamic_component, delete_dynamic_component,
    add_sub_requirement_api, delete_sub_requirement_api,
    get_component_suggestions, get_active_domain_params,
    resolve_canonical_feature, sync_workspace_app_shell, CANONICAL_FEATURE_MAP
)

from config_loader import get_workspace_base
from onboarding.verification import audit_domain_vocabulary, verify_preview_health
from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold
from onboarding.requirement_generator import generate_dynamic_requirements
from onboarding.synthesis import synthesize_domain_code

__all__ = [
    "app", "lifespan", "get_workspace_base", "get_active_domain_params", "resolve_canonical_feature",
    "sync_workspace_app_shell", "audit_domain_vocabulary", "verify_preview_health",
    "create_default_workspace_scaffold", "generate_dynamic_requirements",
    "synthesize_domain_code", "add_dynamic_component", "delete_dynamic_component",
    "add_sub_requirement_api", "delete_sub_requirement_api", "get_component_suggestions"
]

