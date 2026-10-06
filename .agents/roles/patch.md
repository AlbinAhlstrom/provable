# Role: patch-role

## 1. Goal
Implement targeted code modifications to fix a bug identified by `root_cause-role`.

## 2. Inputs
- Root cause diagnosis and target files from `root_cause-role`.

## 3. Allowed Actions & Tools
- Code editing tools (`replace_file_content`, `write_to_file`).
- Modifying production and test files to apply the fix.
- **FORBIDDEN**: Developing unrelated new features or refactoring architectural boundaries outside the bug scope.

## 4. Output Contract
A targeted diff / patch:
- Code modifications applied to source files.
- Regression test added or updated to prevent recurrence.
- Handed back to `debug-role` for verification.
