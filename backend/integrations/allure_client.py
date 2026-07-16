"""
Allure Client — Handles configuration and reporting links for Allure Test Reports.
Since Allure is mounted as a volume, test results are automatically synced by Docker.
"""
import os
import yaml
import db.store as store
from typing import Dict, Any

SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'integrations.yaml'))


def load_allure_config() -> Dict[str, Any]:
    if not os.path.exists(SETTINGS_FILE):
        return {"enabled": False, "server_url": "http://localhost:5050", "project_id": "default"}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('allure', {"enabled": False, "server_url": "http://localhost:5050", "project_id": "default"})
    except Exception:
        return {"enabled": False, "server_url": "http://localhost:5050", "project_id": "default"}


def get_allure_report_url() -> str:
    """Return the direct iframe URL to the latest generated Allure HTML report."""
    cfg = load_allure_config()
    server_url = cfg.get('server_url', 'http://localhost:5050').rstrip('/')
    project_id = cfg.get('project_id', 'default')
    
    # URL structure for frankescobar/allure-docker-service report index:
    # http://localhost:5050/allure-docker-service/projects/default/reports/latest/index.html
    return f"{server_url}/allure-docker-service/projects/{project_id}/reports/latest/index.html"


def get_coverage_summary() -> Dict[str, Any]:
    """Calculate requirements and test coverage metrics from the SQLite database."""
    conn = store.get_connection()
    try:
        # 1. Get total requirements
        total_reqs = conn.execute("SELECT COUNT(*) FROM requirements WHERE type = 'Requirement'").fetchone()[0]
        
        # 2. Get requirements with passing test cases
        # A requirement is considered passing if it has at least one test case and ALL of its linked test cases are passing
        all_reqs_cursor = conn.execute("SELECT id FROM requirements WHERE type = 'Requirement'")
        passing_count = 0
        failing_count = 0
        uncovered_count = 0
        
        for row in all_reqs_cursor:
            req_id = row['id']
            # Find linked test cases
            tcs = conn.execute("SELECT last_result FROM test_cases WHERE requirement_id = ?", (req_id,)).fetchall()
            
            if not tcs:
                uncovered_count += 1
            else:
                if all(tc['last_result'] == 'pass' for tc in tcs):
                    passing_count += 1
                else:
                    failing_count += 1
                    
        return {
            "total_requirements": total_reqs,
            "passing": passing_count,
            "failing": failing_count,
            "uncovered": uncovered_count
        }
    except Exception as e:
        print(f"Failed to get coverage summary: {e}")
        return {
            "total_requirements": 0,
            "passing": 0,
            "failing": 0,
            "uncovered": 0
        }
    finally:
        conn.close()
