"""
Onboarding Orchestrator — runs the full onboarding pipeline for a new project folder.

Pipeline:
  1. workspace_discovery_agent   → generates .provable.yaml
  2. requirements_generator      → AI-generates requirements.sdoc from markdown docs
  3. test_importer               → decorates existing E2E tests with BDD/Allure tags
  4. requirements_synthesizer    → derives requirements from unlinked test functions
  5. config_loader               → registers project + sets active workspace
  6. store (DB layer)            → switches to per-project provable.db and syncs sdoc
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.workspace_discovery_agent import discover_project_config, write_provable_yaml
from onboarding.requirements_generator import auto_generate_sdoc_requirements
from onboarding.test_importer import import_and_decorate_tests
from onboarding.requirements_synthesizer import synthesize_requirements_from_tests
from config_loader import set_active_project, add_project, get_project_settings
import db.store as store
from integrations.strictdoc_client import sync_sdoc_to_db


def onboard_project(project_path: str, run_synthesis: bool = True):
    """
    Onboard a local project folder into Provable.

    Args:
        project_path:   Absolute path to the project root.
        run_synthesis:  If True, run reverse-TDD requirement synthesis from tests.
    """
    project_path = os.path.abspath(project_path)
    if not os.path.exists(project_path):
        print(f"❌ Onboarding failed: Path {project_path} does not exist.")
        return

    print(f"\n🚀 Onboarding project: {project_path}\n{'='*60}")

    # ── Step 1: Workspace Discovery ────────────────────────────────
    provable_yaml_path = os.path.join(project_path, '.provable.yaml')
    if not os.path.exists(provable_yaml_path):
        print("\n📡 Step 1: Discovering project configuration...")
        config = discover_project_config(project_path)
        write_provable_yaml(project_path, config)
    else:
        print(f"\n📡 Step 1: .provable.yaml already exists — skipping discovery.")

    # ── Step 2: Requirements Generation ───────────────────────────
    sdoc_path = os.path.join(project_path, 'requirements', 'requirements.sdoc')
    if not os.path.exists(sdoc_path):
        print("\n📄 Step 2: Generating requirements from project documentation...")
        sdoc_path = auto_generate_sdoc_requirements(project_path)
    else:
        print(f"\n📄 Step 2: requirements.sdoc already exists — skipping generation.")

    # ── Step 3: Test Import & BDD Decoration ──────────────────────
    print("\n🧪 Step 3: Importing and decorating existing tests...")
    import_and_decorate_tests(project_path, sdoc_path)

    # ── Step 4: Requirement Synthesis from Tests ───────────────────
    if run_synthesis:
        print("\n🔬 Step 4: Synthesizing requirements from unlinked test functions...")
        count = synthesize_requirements_from_tests(project_path)
        print(f"   → {count} new requirements synthesized.")
    else:
        print("\n🔬 Step 4: Synthesis skipped (run_synthesis=False).")

    # ── Step 5: Register & Activate Project ───────────────────────
    print("\n⚙️  Step 5: Registering and activating project...")
    settings = get_project_settings()
    project_name = settings.get('name', os.path.basename(project_path))
    add_project(project_name, project_path)
    set_active_project(project_path)

    # ── Step 6: Switch Database & Sync Requirements ────────────────
    print("\n🗃️  Step 6: Switching to per-project database and syncing requirements...")
    db_path = os.path.join(project_path, 'requirements', 'provable.db')
    store.set_active_db(db_path)
    store.init_db()
    sync_sdoc_to_db(clear_first=True)

    print(f"\n{'='*60}")
    print(f"🎉 Onboarding complete!")
    print(f"   Project:  {project_name}")
    print(f"   Path:     {project_path}")
    print(f"   Database: {db_path}")
    print(f"   Preview:  {settings.get('dev_server', {}).get('base_url', 'N/A')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python onboard.py <project_path> [--no-synthesis]")
        sys.exit(1)
    run_synth = '--no-synthesis' not in sys.argv
    onboard_project(sys.argv[1], run_synthesis=run_synth)
