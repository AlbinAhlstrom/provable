import os
import sys
import re
from typing import Dict, Any, List

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_orchestrator import call_gemini

# The canonical folder hierarchy all projects must use
CANONICAL_HIERARCHY = """
[DOCUMENT]
TITLE: Project System Requirements

[SECTION]
TITLE: Functional

[SECTION]
TITLE: GUI

[SECTION]
TITLE: Pages
... (page-level requirements)
[/SECTION]

... (other GUI sub-sections like "Game Board", "Dashboard", "Modals" as needed)

[/SECTION]

[SECTION]
TITLE: Business Logic
... (sub-sections like "Core Engine", "Auth", "API" as needed)
[/SECTION]

[/SECTION]

[SECTION]
TITLE: Non-Functional

[SECTION]
TITLE: Performance
... (performance requirements)
[/SECTION]

[SECTION]
TITLE: Security
... (security requirements)
[/SECTION]

[/SECTION]
"""


def auto_generate_sdoc_requirements(project_path: str) -> str:
    """Scans the project for README, TODOs, and interaction specifications to construct a requirements.sdoc."""
    potential_doc_files = [
        "INTERACTION_REQUIREMENTS.md",
        "TODO.md",
        "README.md",
        "README.markdown",
        "todo.txt"
    ]

    docs_context = {}
    for filename in os.listdir(project_path):
        if filename.upper() in [f.upper() for f in potential_doc_files]:
            filepath = os.path.join(project_path, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        docs_context[filename] = f.read()
                except Exception as e:
                    print(f"Error reading doc file {filename}: {e}")

    if not docs_context:
        # Fallback if no doc files are found: scan folder structure
        src_dirs = [d for d in os.listdir(project_path)
                    if os.path.isdir(os.path.join(project_path, d)) and not d.startswith('.')]
        docs_context["Project Overview"] = f"A project with directories: {', '.join(src_dirs)}"

    doc_sections_summary = ""
    for name, content in docs_context.items():
        doc_sections_summary += f"--- FILE: {name} ---\n{content}\n\n"

    prompt = f"""
You are an expert system analyst and requirements engineer.
Your task is to take the provided documentation files from a software project and convert them into a structured StrictDoc requirements file (.sdoc format).

Here is the parsed documentation of the project:
{doc_sections_summary}

Generate a complete requirements.sdoc file using the EXACT canonical folder hierarchy below.
You MUST use this structure as the top-level skeleton and populate it with appropriate requirements.
You may add more sub-[SECTION] blocks as needed (e.g. "Game Board", "Auth", "API", "Data Storage"), but the top-level sections MUST be exactly:

  [SECTION] Functional
    [SECTION] GUI
      [SECTION] Pages   ← page-level requirements go here
      [/SECTION]
      ... (add more GUI sub-sections as needed, e.g. "Game Board UI", "Modals")
    [/SECTION]
    [SECTION] Business Logic
      ... (add sub-sections: "Core Engine", "Auth", "Matchmaking", etc. as needed)
    [/SECTION]
  [/SECTION]
  [SECTION] Non-Functional
    [SECTION] Performance
    [/SECTION]
    [SECTION] Security
    [/SECTION]
  [/SECTION]

Follow this format for each requirement:

[REQUIREMENT]
UID: REQ-<Unique 4-digit number, e.g. REQ-1001>
TITLE: <Short requirement title>
STATEMENT: <Detailed specification statement>
REQ_TYPE: <Requirement | Task | Bug>
PRIORITY: <High | Med | Low>
STATUS: <Backlog | Done>

Rules:
1. Capture as many of the actual listed requirements and todo items as possible.
2. Every [REQUIREMENT] must have a unique UID (like REQ-1001). Use BUG- prefix for bug items.
3. Place each requirement in the most fitting sub-section.
4. Return ONLY the raw requirements.sdoc content. Do not wrap it in markdown code blocks.
5. Always close every [SECTION] with a matching [/SECTION] tag.
"""

    print(f"🤖 Generating requirements.sdoc using Gemini...")
    sdoc_content = call_gemini(prompt)

    # Strip any markdown blocks if the model returned them
    sdoc_content = re.sub(r"^```[a-zA-Z0-9]*\n", "", sdoc_content)
    sdoc_content = re.sub(r"\n```$", "", sdoc_content)

    # Save the file to requirements/requirements.sdoc inside target project
    reqs_dir = os.path.join(project_path, 'requirements')
    os.makedirs(reqs_dir, exist_ok=True)
    sdoc_file = os.path.join(reqs_dir, 'requirements.sdoc')

    with open(sdoc_file, 'w', encoding='utf-8') as f:
        f.write(sdoc_content)

    print(f"✅ Generated and saved requirements to {sdoc_file}")
    return sdoc_file
