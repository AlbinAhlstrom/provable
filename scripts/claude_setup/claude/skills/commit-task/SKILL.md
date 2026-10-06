---
name: commit-task
description: Commit a finished task following the project's standing policy (scoped staging, conventional subject, amend when it is a follow-up on the same subject). Use automatically when a task is done and tests are green; also invocable as /commit-task.
---

# Commit a finished task

Preconditions: the task is complete and the tests are green (full suite run locally, or confirmed by the user in a cloud session). Never push.

1. `git status --porcelain` and `git diff --stat`. The tree usually holds unrelated uncommitted work; list which files this task touched.
2. Stage only those files with `git add -- <paths>`. Never `git add -A` or `git add .`. Never stage `.env`, anything under `workspace/`, or logs.
3. Decide new commit versus amend:
   - **Amend** (`git commit --amend`, keep or lightly edit the message) only if all hold: the change is a follow-up on the same subject as the latest commit, that commit carries a `Claude-Session:` trailer, and it is not pushed (`git rev-list @{u}..HEAD` includes it).
   - Otherwise create a new commit. Never amend a commit made by someone else or already pushed.
4. Subject: conventional style used in this repo, `type(scope): imperative summary`, with type one of `feat`, `fix`, `test`, `refactor`, `docs`, `chore`. Add a short body when the why is not obvious.
5. End the message with the attribution trailers from the session's system reminder (the `Co-Authored-By:` and `Claude-Session:` lines) when one is present.
6. Report the commit hash and subject in one line.
