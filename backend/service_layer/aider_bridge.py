"""
Aider Precision In-File Bridge.
Coordinates Aider's Tree-sitter AST repo-map and SWE-bench surgical diff engine
for Day-2 class extension, invariant mutation, and atomic git rollbacks.
"""

import os
import subprocess
from typing import List, Dict, Any, Optional
from onboarding.wayfinder import BddClause

try:
    import aider
    from aider.coders import Coder
    from aider.models import Model
    from aider.io import InputOutput
    HAVE_AIDER = True
except ImportError:
    HAVE_AIDER = False


class ProvableAiderBridge:
    """
    Precision in-file editor bridge leveraging Aider.
    Applies surgical patches to existing codebases and enforces git-level reversibility.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.environ.get("AIDER_MODEL", "gemini/gemini-1.5-flash-latest")

    def is_available(self) -> bool:
        """Checks if the Aider package is installed and importable."""
        return HAVE_AIDER

    def format_bdd_implementation_prompt(self, bdd_clause: BddClause, test_code: str) -> str:
        """Formats an unambiguous BDD contract prompt for Aider's precision editor."""
        gherkin_lines = [
            f"GIVEN {bdd_clause.given}",
            f"WHEN {bdd_clause.when}",
            f"THEN {bdd_clause.then}"
        ]
        if bdd_clause.unless:
            gherkin_lines.append(f"UNLESS {bdd_clause.unless}")
        gherkin_text = "\n".join(gherkin_lines)

        return f"""
You are Provable's Precision Code Editor.
Your task is to implement the following formal BDD invariant contract:

```gherkin
{gherkin_text}
```

Here is the automated acceptance test that MUST pass:
```python
{test_code}
```

Instructions:
1. Make surgical, minimal edits to the target files to satisfy this specification.
2. Respect pure Domain-Driven Design: Domain models must NEVER import presentation routers or database layers.
3. Do not modify or weaken test assertions.
"""

    def apply_bdd_patch(
        self,
        workspace_path: str,
        target_files: List[str],
        bdd_clause: BddClause,
        test_code: str,
        test_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Applies a surgical diff to target files using Aider with atomic git rollback protection.
        """
        if not HAVE_AIDER:
            return {
                "success": False,
                "error": "Aider is not installed in this Python environment. Run 'pip install aider-chat'.",
                "files_modified": []
            }

        # 1. Create Git Checkpoint
        initial_commit = None
        try:
            initial_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=workspace_path,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            pass  # Non-git workspace fallback

        prompt = self.format_bdd_implementation_prompt(bdd_clause, test_code)

        try:
            io = InputOutput(yes=True)
            model = Model(self.model_name)
            coder = Coder.create(
                main_model=model,
                io=io,
                fnames=[os.path.join(workspace_path, f) if not os.path.isabs(f) else f for f in target_files],
                git_root=workspace_path,
                auto_commits=True,
                show_diffs=False
            )

            response = coder.run(prompt)

            # 2. Run Verification Command if provided
            if test_command:
                test_proc = subprocess.run(
                    test_command,
                    shell=True,
                    cwd=workspace_path,
                    capture_output=True,
                    text=True
                )
                if test_proc.returncode != 0:
                    # Test failed: Rollback via Git to preserve zero dark matter
                    if initial_commit:
                        subprocess.run(["git", "reset", "--hard", initial_commit], cwd=workspace_path, check=False)
                    return {
                        "success": False,
                        "error": f"Verification test failed (Exit {test_proc.returncode}). Rolled back to checkpoint.\n{test_proc.stderr}",
                        "files_modified": []
                    }

            return {
                "success": True,
                "response": response,
                "files_modified": target_files
            }

        except Exception as e:
            if initial_commit:
                subprocess.run(["git", "reset", "--hard", initial_commit], cwd=workspace_path, check=False)
            return {
                "success": False,
                "error": f"Aider execution failed: {str(e)}",
                "files_modified": []
            }
