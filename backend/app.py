"""
Provable Platform Application Factory & Entrypoint.
Initializes FastAPI, configures CORS, handles Lifespan startup/shutdown, and mounts entrypoint routers.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')

import os
import dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from root .env file if present
dotenv.load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

import db.store as store
from config_loader import get_workspace_base, is_serverless
from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip live DB initialization and sync during test suite execution
    if not (os.environ.get("DATABASE_URL") or "pytest" in sys.modules):
        _ws_base = get_workspace_base()
        _active_db = os.path.join(_ws_base, 'requirements', 'provable.db')
        store.set_active_db(_active_db)
        store.init_db()

        # Re-sync the App.tsx shell of an already synthesized domain (never generates one from the default pitch)
        from service_layer import services
        services.sync_workspace_app_shell_on_startup()

        # Guarantee a valid working React scaffold exists so Vite port 5174 is always active
        if not (os.path.exists(os.path.join(_ws_base, 'package.json')) and os.path.exists(os.path.join(_ws_base, 'src', 'App.tsx'))):
            create_default_workspace_scaffold(_ws_base)

        try:
            from integrations.strictdoc_client import sync_sdoc_to_db
            sync_sdoc_to_db(clear_first=True)
        except Exception as e:
            print(f"📦 Startup: Failed to sync SDoc: {e}")

        # Auto-create Allure project if enabled (needs the local Allure container; skipped on serverless)
        try:
            if is_serverless():
                raise RuntimeError("serverless deployment: no Allure container")
            from integrations.allure_client import load_allure_config, get_allure_project_id
            allure_cfg = load_allure_config()
            if allure_cfg.get('enabled'):
                import requests
                _proj_slug = get_allure_project_id()
                allure_url = f"{allure_cfg.get('server_url', 'http://localhost:5050').rstrip('/')}/projects"
                res = requests.post(allure_url, json={"id": _proj_slug}, timeout=1)
                print(f"📊 Allure Integration: Project '{_proj_slug}' init response: {res.status_code}")
        except Exception as allure_init_err:
            print(f"📊 Allure Integration: Could not auto-create project: {allure_init_err}")

        # Launch dev server for active project if enabled (cannot run background servers on serverless)
        try:
            if is_serverless():
                raise RuntimeError("serverless deployment: no background dev servers")
            from onboarding.server_manager import start_project_servers
            start_project_servers()
        except Exception as server_err:
            print(f"⚠️ Startup: Failed to start project servers: {server_err}")
    yield
    if not (os.environ.get("DATABASE_URL") or "pytest" in sys.modules):
        from onboarding.server_manager import stop_project_servers
        stop_project_servers()


app = FastAPI(title="Provable Backend Platform API", lifespan=lifespan)

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from entrypoints.routers.projects import router as projects_router
from entrypoints.routers.requirements import router as requirements_router
from entrypoints.routers.testing import router as testing_router
from entrypoints.routers.kickstart import router as kickstart_router
from entrypoints.routers.components import router as components_router
from entrypoints.routers.specs import router as specs_router
from entrypoints.routers.onboarding import router as onboarding_router
app.include_router(projects_router)
app.include_router(requirements_router)
app.include_router(testing_router)
app.include_router(kickstart_router)
app.include_router(components_router)
app.include_router(specs_router)
app.include_router(onboarding_router)


