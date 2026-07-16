"""
Jira Client — Synchronizes tasks and statuses with Jira Cloud.
Falls back to Mock mode if disabled or credentials are placeholders.
"""
import os
import yaml
import requests
from requests.auth import HTTPBasicAuth
import db.store as store
from typing import Dict, Any, Optional

SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'integrations.yaml'))


def load_jira_config() -> Dict[str, Any]:
    if not os.path.exists(SETTINGS_FILE):
        return {"enabled": False, "server_url": "", "username": "", "api_token": "", "project_key": "MOCK"}
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('jira', {"enabled": False, "server_url": "", "username": "", "api_token": "", "project_key": "MOCK"})
    except Exception:
        return {"enabled": False, "server_url": "", "username": "", "api_token": "", "project_key": "MOCK"}


def is_jira_mock_mode() -> bool:
    cfg = load_jira_config()
    if not cfg.get('enabled'):
        return True
    # Check if credentials are placeholders
    if 'your-domain' in cfg.get('server_url', '') or 'YOUR_JIRA_API_TOKEN' in cfg.get('api_key_env', cfg.get('api_token', '')):
        return True
    return False


def _get_auth_headers(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def create_jira_ticket(title: str, description: str, req_id: str) -> str:
    """Create a ticket in Jira linked to a requirement and return the ticket key."""
    cfg = load_jira_config()
    project_key = cfg.get('project_key', 'PROV')
    
    if is_jira_mock_mode():
        import random
        mock_key = f"{project_key}-{random.randint(100, 999)}"
        print(f"🎫 [JIRA MOCK]: Created ticket {mock_key} - '{title}' for {req_id}")
        return mock_key

    server_url = cfg.get('server_url', '').rstrip('/')
    username = cfg.get('username', '')
    api_token = cfg.get('api_token', '')
    
    url = f"{server_url}/rest/api/2/issue"
    auth = HTTPBasicAuth(username, api_token)
    headers = _get_auth_headers(cfg)
    
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": f"[{req_id}] {title}",
            "description": f"Linked Requirement: {req_id}\n\n{description}",
            "issuetype": {
                "name": "Task"
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=10)
        response.raise_for_status()
        data = response.json()
        key = data.get('key')
        print(f"🎫 [JIRA]: Created ticket {key} successfully.")
        return key
    except Exception as e:
        print(f"🎫 [JIRA]: Failed to create ticket: {e}. Falling back to mock ID.")
        import random
        return f"{project_key}-ERR-{random.randint(100, 999)}"


def get_ticket_status(key: str) -> str:
    """Fetch status from Jira and return standard status (Backlog, InProgress, Done)."""
    if is_jira_mock_mode() or "ERR" in key:
        # Mock mode status helper: load requirement from SQLite
        conn = store.get_connection()
        row = conn.execute("SELECT status FROM requirements WHERE jira_key = ?", (key,)).fetchone()
        conn.close()
        return row['status'] if row else "Backlog"

    cfg = load_jira_config()
    server_url = cfg.get('server_url', '').rstrip('/')
    username = cfg.get('username', '')
    api_token = cfg.get('api_token', '')
    
    url = f"{server_url}/rest/api/2/issue/{key}"
    auth = HTTPBasicAuth(username, api_token)
    
    try:
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()
        data = response.json()
        jira_status = data['fields']['status']['name'].lower()
        
        # Map Jira status name to Provable status
        if 'done' in jira_status or 'resolved' in jira_status or 'closed' in jira_status:
            return "Done"
        elif 'progress' in jira_status or 'review' in jira_status:
            return "InProgress"
        else:
            return "Backlog"
    except Exception as e:
        print(f"🎫 [JIRA]: Failed to get ticket status for {key}: {e}")
        return "Backlog"


def update_ticket_status(key: str, status: str):
    """Transition Jira issue status to map with SQLite status."""
    if is_jira_mock_mode():
        print(f"🎫 [JIRA MOCK]: Transitioned ticket {key} status to '{status}'")
        return

    cfg = load_jira_config()
    server_url = cfg.get('server_url', '').rstrip('/')
    username = cfg.get('username', '')
    api_token = cfg.get('api_token', '')
    
    auth = HTTPBasicAuth(username, api_token)
    headers = _get_auth_headers(cfg)
    
    # 1. Fetch available transitions
    transitions_url = f"{server_url}/rest/api/2/issue/{key}/transitions"
    try:
        res = requests.get(transitions_url, auth=auth, timeout=10)
        res.raise_for_status()
        transitions = res.json().get('transitions', [])
        
        # Map target status to expected Jira transition names
        target_names = []
        if status == 'Done':
            target_names = ['done', 'resolved', 'close issue', 'close']
        elif status == 'InProgress':
            target_names = ['in progress', 'start progress', 'start work', 'progress']
        else:
            target_names = ['to do', 'backlog', 'reopen', 'reopen issue']
            
        transition_id = None
        for t in transitions:
            t_name = t['name'].lower()
            if any(name in t_name for name in target_names):
                transition_id = t['id']
                break
                
        if not transition_id:
            # Fallback to first transition if no name matches
            if transitions:
                transition_id = transitions[0]['id']
                
        if transition_id:
            # 2. Post transition
            payload = {"transition": {"id": transition_id}}
            post_res = requests.post(transitions_url, json=payload, headers=headers, auth=auth, timeout=10)
            post_res.raise_for_status()
            print(f"🎫 [JIRA]: Successfully transitioned {key} to {status} (transition ID {transition_id}).")
    except Exception as e:
        print(f"🎫 [JIRA]: Failed to update ticket status for {key}: {e}")


def sync_jira_to_db():
    """Fetch active tickets from Jira and synchronize their status back to SQLite."""
    if is_jira_mock_mode():
        return

    cfg = load_jira_config()
    server_url = cfg.get('server_url', '').rstrip('/')
    username = cfg.get('username', '')
    api_token = cfg.get('api_token', '')
    project_key = cfg.get('project_key', 'PROV')
    
    auth = HTTPBasicAuth(username, api_token)
    
    # Search for all issues in project
    jql = f"project = {project_key} ORDER BY updated DESC"
    url = f"{server_url}/rest/api/2/search?jql={jql}&maxResults=100"
    
    try:
        response = requests.get(url, auth=auth, timeout=15)
        response.raise_for_status()
        issues = response.json().get('issues', [])
        
        conn = store.get_connection()
        for issue in issues:
            key = issue['key']
            jira_status = issue['fields']['status']['name'].lower()
            
            # Map status
            if 'done' in jira_status or 'resolved' in jira_status or 'closed' in jira_status:
                status = "Done"
            elif 'progress' in jira_status or 'review' in jira_status:
                status = "InProgress"
            else:
                status = "Backlog"
                
            # Update SQLite requirement status if the JIRA key matches
            conn.execute(
                "UPDATE requirements SET status = ? WHERE jira_key = ?",
                (status, key)
            )
        conn.commit()
        conn.close()
        print(f"🎫 [JIRA]: Synced {len(issues)} issues to SQLite.")
    except Exception as e:
        print(f"🎫 [JIRA]: Sync failed: {e}")
