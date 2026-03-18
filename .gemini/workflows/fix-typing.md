---
description: Check for typing issues and fix them using ty
---

# Fix Typing Issues

Follow these steps to find and fix all typing issues in the project.

## Steps

1. **Run the type checker**
   Execute `uv run ty check` from the project root and capture the full output.

2. **Parse and group errors**
   Group the reported errors by file path. For each file, list the line numbers and error messages.

3. **Fix each file**
   For each file with errors, starting from the one with the most issues:
   - Open the file and read the relevant lines.
   - Understand the root cause of each type error.
   - Apply the minimal fix that resolves the error without changing runtime behaviour.
   - Common fixes include:
     - Adding or correcting type annotations.
     - Narrowing types with `isinstance()` or `assert` guards.
     - Using `cast()` only as a last resort, with a comment explaining why.
     - Replacing `Any` with concrete types where possible.
     - Adding `# type: ignore[code]` **only** when the checker is wrong, with a justification comment.

4. **Re-run the type checker**
   Execute `uv run ty check` again and confirm all previous errors are resolved. If new errors appear, repeat from step 3.

5. **Summary**
   Provide a summary listing:
   - Total errors found → total errors fixed.
   - Files modified and a one-line description of each change.
