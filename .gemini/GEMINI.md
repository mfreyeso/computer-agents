# Project Context

This is a **Python 3.12+** project managed with **[uv](https://docs.astral.sh/uv/)**.

## Package Management

- Use `uv` for all dependency and environment operations.
- Dependencies are declared in `pyproject.toml`.
- The lock file (`uv.lock`) must be committed and kept up to date.
- Run scripts via `uv run <command>` (e.g., `uv run pytest`, `uv run ty check`).
- Add dependencies with `uv add <package>` and dev dependencies with `uv add --dev <package>`.

## Code Review Guidelines

When reviewing code, evaluate every change against this checklist:

### Correctness

- Logic errors, off-by-one mistakes, unhandled edge cases.
- Proper error handling with specific exception types — never bare `except`.
- Resource cleanup (`with` statements, context managers).

### Typing

- All public functions and methods must have complete type annotations.
- Use modern syntax: `X | Y` instead of `Union[X, Y]`, `list[T]` instead of `List[T]`.
- Validate consistency between annotations and runtime behaviour.

### Security

- No secrets, credentials, or API keys in source code.
- Input validation and sanitisation where applicable.
- Safe handling of file paths, subprocess calls, and user-supplied data.

### Performance

- Avoid unnecessary copies, redundant loops, or O(n²) patterns when a better alternative exists.
- Prefer generators/iterators for large data pipelines.
- Appropriate use of caching and data structures.

### Readability & Maintainability

- Clear, descriptive names for variables, functions, classes, and modules.
- Functions do one thing; keep them short and focused.
- Docstrings on all public APIs (modules, classes, functions).
- No dead code, commented-out blocks, or TODO items without a tracking reference.

### Testing

- Every new feature or bug fix should include or update tests.
- Test names describe the scenario: `test_<function>_<scenario>_<expected>`.
- Use `pytest` with fixtures and parametrize for data-driven cases.

@styleguide.md
