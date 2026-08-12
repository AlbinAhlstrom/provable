#!/usr/bin/env python3
"""
backend/run_server.py — Uvicorn launcher for Provable.
Patches Uvicorn's BaseReload.restart on Windows so file hot-reloads use process termination
instead of broadcasting console-wide CTRL_C_EVENT signals that stop parent scripts (run.py).
"""

import sys
import os

if sys.platform == "win32":
    try:
        import uvicorn.supervisors.basereload
        _orig_restart = uvicorn.supervisors.basereload.BaseReload.restart

        def _patched_restart(self):
            if hasattr(self, "process") and self.process and self.process.is_alive():
                self.process.terminate()
                self.process.join()
            self.process = self.get_subprocess()
            self.process.start()

        uvicorn.supervisors.basereload.BaseReload.restart = _patched_restart
    except Exception as e:
        print(f"[run_server] Notice: Uvicorn reload patch fallback: {e}", flush=True)

if __name__ == "__main__":
    import uvicorn.main
    uvicorn.main.main()
