"""
Draft theme: the colours of the app a visitor sees before its page is written.

The Studio shows the generated app from the moment its skeleton exists. Until the page is written that is the
skeleton's stand-in, and the page's look is decided a minute earlier, in the UX plan's visual direction. The plan ends
that section with one token line (`TOKENS background=#... surface=#... text=#... accent=#... on_accent=#... heading=serif`),
which is read here as a typed `DraftTheme` and written to `src/theme.css`. The stand-in is coloured by those variables,
so the written page arrives as the same app filling in.

The same section states the form of the main view as one layout line (`LAYOUT columns=7 rows=5`, or `rows=auto`
for a view that grows with its records), read here as a typed `DraftLayout`. The stand-in draws it as an empty outline
above its records: the view's columns and rows, in the plan's colours, before anything is in them.

- The skeleton writes the file with neutral values and no outline; the UX plan stage replaces it.
- A direction without a complete layout line gives no outline.
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
_LAYOUT_LINE = re.compile(r"\bLAYOUT\b(.*)$", re.MULTILINE)
_LAYOUT_VALUE = re.compile(r"(columns|rows)=(\d+|auto)\b")
OPEN_ROWS = "auto"          # the view has as many rows as it has records
# How the outline of a view with open rows is drawn: it has no proportions of its own to keep
_OPEN_ROWS_DRAWN = 3
_OPEN_ROW_HEIGHT = "5rem"
_FIXED_GRID_HEIGHT = "60vh"  # a fixed grid keeps its proportions and stays within the first screen


@dataclass
class DraftTheme:
    background: str = "#f8fafc"
    surface: str = "#ffffff"
    text: str = "#0f172a"
    accent: str = "#334155"
    on_accent: str = "#ffffff"
    heading: str = "sans"      # serif | sans | mono


@dataclass
class DraftLayout:
    columns: int
    rows: Optional[int]        # None: as many as there are records


def parse_draft_layout(direction: Optional[str]) -> Optional[DraftLayout]:
    """The layout a visual direction's layout line states, or None when the line is missing or incomplete."""
    line = _LAYOUT_LINE.search(direction or "")
    values = dict(_LAYOUT_VALUE.findall(line.group(1))) if line else {}
    if "columns" not in values or "rows" not in values or values["columns"] == OPEN_ROWS:
        return None
    columns, rows = int(values["columns"]), None if values["rows"] == OPEN_ROWS else int(values["rows"])
    if columns < 1 or (rows is not None and rows < 1):
        return None
    return DraftLayout(columns=columns, rows=rows)


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


def _shape_css(layout: Optional[DraftLayout]) -> str:
    """The outline of the main view: one block cut into the layout's columns and rows by strips of the page colour."""
    if layout is None:
        return ".draft-shape { display: none; }\n"
    if layout.rows is None:
        rows, size = _OPEN_ROWS_DRAWN, f"  height: calc({_OPEN_ROWS_DRAWN} * {_OPEN_ROW_HEIGHT});\n"
    else:
        rows = layout.rows
        size = (f"  width: min(100%, calc({_FIXED_GRID_HEIGHT} * {layout.columns} / {rows}));\n"
                f"  aspect-ratio: {layout.columns} / {rows};\n")
    return f""".draft-shape {{
  margin: 1.5rem auto 0;
{size}  border-radius: 0.5rem;
  background-color: color-mix(in srgb, var(--draft-text) 9%, var(--draft-surface));
  background-image: linear-gradient(to right, var(--draft-bg) 4px, transparent 4px),
                    linear-gradient(to bottom, var(--draft-bg) 4px, transparent 4px);
  background-size: calc(100% / {layout.columns}) calc(100% / {rows});
  animation: draft-shape-wait 1.8s ease-in-out infinite;
}}
@keyframes draft-shape-wait {{ 50% {{ opacity: 0.55; }} }}
"""


def theme_css(theme: DraftTheme, layout: Optional[DraftLayout] = None) -> str:
    return f""":root {{
  --draft-bg: {theme.background};
  --draft-surface: {theme.surface};
  --draft-text: {theme.text};
  --draft-accent: {theme.accent};
  --draft-on-accent: {theme.on_accent};
  --draft-heading-font: {_FAMILIES[theme.heading]};
}}
""" + _shape_css(layout)


def write_draft_theme(workspace_dir: str, theme: DraftTheme, layout: Optional[DraftLayout] = None) -> List[str]:
    """Writes the theme and the outline wherever the skeleton put its neutral one; returns the workspace-relative files written."""
    written = []
    for root in (workspace_dir, os.path.join(workspace_dir, "frontend")):
        path = os.path.join(root, THEME_FILE)
        if os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(theme_css(theme, layout))
            written.append(os.path.relpath(path, workspace_dir).replace(os.sep, "/"))
    return written
