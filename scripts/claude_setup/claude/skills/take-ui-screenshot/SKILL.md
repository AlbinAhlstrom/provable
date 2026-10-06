---
name: take-ui-screenshot
description: Capture a screenshot of a PM Studio view with headless Selenium to review UI changes. Requires the stack to be running, so ask the user to start python run.py first.
---

# Take a UI screenshot

The stack must already be running (`python run.py` in the user's terminal). Then:

```bash
python .agents/skills/take_ui_screenshot/scripts/take_screenshot.py --url http://localhost:5173 --view Requirements --output logs/ui_check.png --viewport 1280x800
```

- `--view`: tab to click (for example `Tests`, `Kanban`, `Requirements`, `Review`).
- `--viewport`: `1280x800` (default) or `375x812` for mobile.

Open the image and review it against the checklist in `.claude/rules/frontend-ui.md`.
