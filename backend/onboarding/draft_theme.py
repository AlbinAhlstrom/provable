"""
Draft theme: the colours of the app a visitor sees before its page is written.

The Studio shows the generated app from the moment its skeleton exists. Until the page is written that is the
skeleton's stand-in, and the page's look is decided a minute earlier, in the UX plan's visual direction. The plan ends
that section with one token line (`TOKENS background=#... surface=#... text=#... accent=#... on_accent=#... heading=serif`),
which is read here as a typed `DraftTheme` and written to `src/theme.css`. The stand-in is coloured by those variables,
so the written page arrives as the same app filling in.

- The skeleton writes the file with neutral values; the UX plan stage replaces it.
- A direction without a complete token line gives no theme: the neutral one stays, and the stage notes it.
- The written page does not depend on the file. It is styled by its own classes.
"""

import os
import re
from dataclasses import dataclass, fields
from typing import List, Optional

THEME_FILE = os.path.join("src", "theme.css")
_FAMILIES = {
    "serif": "Georgia, 'Times New Roman', serif",
    "sans": "inherit",
    "mono": "ui-monospace, SFMono-Regular, Menlo, monospace",
}
# The marker is found anywhere on its line: a planner often writes the line as a labelled bullet, inside code marks.
_TOKEN_LINE = re.compile(r"\bTOKENS\b(.*)$", re.MULTILINE)
_TOKEN = re.compile(r"(\w+)=(#[0-9a-fA-F]{6}\b|serif\b|sans\b|mono\b)")


@dataclass
class DraftTheme:
    background: str = "#f8fafc"
    surface: str = "#ffffff"
    text: str = "#0f172a"
    accent: str = "#334155"
    on_accent: str = "#ffffff"
    heading: str = "sans"      # serif | sans | mono


def parse_draft_theme(direction: Optional[str]) -> Optional[DraftTheme]:
    """The theme a visual direction's token line states, or None when the line is missing or incomplete."""
    line = _TOKEN_LINE.search(direction or "")
    if not line:
        return None
    tokens = {name: value.lower() for name, value in _TOKEN.findall(line.group(1))}
    names = [f.name for f in fields(DraftTheme)]
    if any(name not in tokens for name in names) or tokens["heading"] not in _FAMILIES:
        return None
    if any(not tokens[name].startswith("#") for name in names if name != "heading"):
        return None
    return DraftTheme(**{name: tokens[name] for name in names})


def theme_css(theme: DraftTheme) -> str:
    return f""":root {{
  --draft-bg: {theme.background};
  --draft-surface: {theme.surface};
  --draft-text: {theme.text};
  --draft-accent: {theme.accent};
  --draft-on-accent: {theme.on_accent};
  --draft-heading-font: {_FAMILIES[theme.heading]};
}}
"""


def write_draft_theme(workspace_dir: str, theme: DraftTheme) -> List[str]:
    """Writes the theme wherever the skeleton put its neutral one; returns the workspace-relative files written."""
    written = []
    for root in (workspace_dir, os.path.join(workspace_dir, "frontend")):
        path = os.path.join(root, THEME_FILE)
        if os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(theme_css(theme))
            written.append(os.path.relpath(path, workspace_dir).replace(os.sep, "/"))
    return written
