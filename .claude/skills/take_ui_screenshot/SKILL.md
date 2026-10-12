---
name: take_ui_screenshot
description: Takes a screenshot of a specific URL/view of the web application using headless Chrome (Selenium, with a Playwright fallback).
---
# Take UI Screenshot

This skill navigates to the application, selects a specific view, and captures a high-resolution screenshot.

## Instructions

Run the Python helper script to take a screenshot:
```bash
python3 .claude/skills/take_ui_screenshot/scripts/take_screenshot.py --url http://localhost:5173 --view "<tab text>" --output /path/to/screenshot.png
```

Parameters:
- `--url`: The base URL of the application (default: `http://localhost:5173`).
- `--view`: Visible text of a button/tab to click before capturing (matched case-insensitively against `button`, `a`, and `[role=tab]` elements; omit to capture the landing view).
- `--output`: File path to save the screenshot (default: `screenshot.png`).
- `--viewport`: Viewport resolution, e.g., `1280x800` (default) or `375x812`.

## Notes
- Tries Selenium first; if it cannot start a browser (e.g. a chromedriver/Chrome version mismatch in a cloud sandbox) it falls back to Playwright (`pip install playwright`; in cloud sessions Chromium is pre-installed under `/opt/pw-browsers`; never run `playwright install`).
- Studio must be up on :5173. Check or start it with `bash .claude/hooks/ensure_app_running.sh`; never start Vite or `run.py` by hand.
- `python scripts/agent_preflight_check.py` calls this script in Phase 6 and writes `logs/latest_ui_render.png` (gitignored).
