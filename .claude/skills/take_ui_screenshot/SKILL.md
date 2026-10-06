---
name: take_ui_screenshot
description: Takes a screenshot of a specific URL/view of the web application using headless Selenium.
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
