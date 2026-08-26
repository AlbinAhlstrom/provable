#!/usr/bin/env python3
"""
Reset workspace utility — calls http://localhost:8000/api/onboarding/reset
to purge corrupted domain artifacts and restore default clean workspace state.
"""

import sys
import json
import urllib.request
import urllib.error

def reset_workspace():
    url = "http://localhost:8000/api/onboarding/reset"
    print(f"Calling POST {url} to reset workspace...")
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps({}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"Reset Response (via HTTP): {data}")
            return data
    except Exception as e:
        print(f"HTTP reset unavailable ({e}). Performing direct DDD service reset...")
        import os
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from service_layer.unit_of_work import SqliteUnitOfWork
        from service_layer import services
        res = services.reset_all_projects(uow=SqliteUnitOfWork())
        print(f"Reset Response (via Service Layer): {res}")
        return res

if __name__ == "__main__":
    reset_workspace()
