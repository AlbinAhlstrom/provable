---
name: commit-task
description: Commit a finished task following the project's standing policy (scoped staging, conventional subject, amend or fixup for follow-ups). Use automatically when a task is done, before reporting back to the user; also invocable as /commit-task.
---

# Commit a finished task

Run this as the last step of every task, so work never piles up into one large commit. The commit guard runs the full test suite (and the frontend build when `frontend/` is staged), so do not run them by hand first.

1. `git status --porcelain` and `git diff --stat`. The tree may hold unrelated uncommitted work; list which files this task touched.
2. Stage only those files with `git add -- <paths>`. Never `git add -A` or `git add .`. Never stage `.env`, anything under `workspace/`, or logs.
3. Choose how to record it:
   - **New commit**: the default, for any new subject.
   - **Amend** (`git commit --amend`) only if all hold: the change is a follow-up that fixes, refines or finishes the latest commit's own subject, that commit was made in this session, and it is not pushed (`git rev-list @{u}..HEAD` lists it, or there is no upstream).
   - **Fixup** (`git commit --fixup=<sha>`) when the target commit is already pushed. Never rewrite pushed history: no amend, rebase or force-push. Fixups are squashed when the PR is merged (squash-merge), or by the author with `git rebase -i --autosquash`.
   - Unsure whether it is the same subject: make a new commit. Two small commits are cheaper than a muddled one.
4. Subject: `type(scope): imperative summary` with type one of `feat`, `fix`, `test`, `refactor`, `docs`, `chore`. Add a short body when the why is not obvious.
5. End the message with the attribution trailers the session's system reminder asks for.
6. Pushing and opening the PR follow the session's branch instructions. Report the commit hash and subject in one line.
