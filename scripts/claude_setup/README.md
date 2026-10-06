# Claude Code setup for Provable

`.claude/` cannot be written from remote or cloud sessions, so the configuration lives here (versioned) and one command installs it.

```
python scripts/claude_setup/install.py          # first time, or after pulling changes
python scripts/claude_setup/install.py --force  # overwrite local edits with the versioned copy
```

| Piece | Purpose |
| --- | --- |
| `claude/settings.json` | Permission rules (no pushes, no `git add -A`, no `.env` reads, no `run.py` from a session, workspace edits denied) and hooks. |
| `scripts/claude_hooks/workspace_guard.py` | PreToolUse hook: any agent write into `workspace/` is blocked and the run halts with a notice. |
| `scripts/claude_hooks/canary_stop.py` | Stop hook: forces the `[🛡️ Clanker Active]` canary at the end of every response. |
| `claude/rules/*.md` | Path-scoped rules that load only when relevant files are touched (engine/TDD, PM Studio, generated-app behaviour). |
| `claude/agents/` | Subagents: `architecture-verifier`, `code-smell-verifier`, `workspace-inspector`. |
| `claude/skills/` | `acceptance`, `fix-pipeline-bug` (`/fix-pipeline-bug <problem>`), `commit-task`, `take-ui-screenshot`. |

After installing, verify in Claude Code: `/permissions`, `/hooks`, `/agents`. The hooks run with the system `python`; if your Windows setup only has `py`, change the two `command` strings in `.claude/settings.json`.

The older Antigravity files in `.agents/` are untouched and can stay until you no longer use that tool.
