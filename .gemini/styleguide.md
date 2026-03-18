# Python Style Guide

## General

- Follow **PEP 8** for formatting and **PEP 257** for docstrings.
- Maximum line length: **88 characters** (Black default).
- Use **4 spaces** for indentation — never tabs.
- End every file with a single newline.

## Modern Python (3.12+)

- Use **f-strings** for string interpolation — never `%` or `.format()`.
- Prefer `match`/`case` over long `if`/`elif` chains where it improves clarity.
- Use the `type` statement for type aliases: `type Vector = list[float]`.
- Use `Self` from `typing` for methods that return the current class instance.
- Prefer `ExceptionGroup` and `except*` when handling concurrent error scenarios.

## Typing

- Annotate **all** public and private function signatures (parameters + return type).
- Use built-in generics: `list[str]`, `dict[str, int]`, `tuple[int, ...]`.
- Use `X | Y` union syntax — never `typing.Union` or `typing.Optional`.
- Use `None` explicitly in return types: `-> str | None`, not `-> Optional[str]`.
- Use `typing.TypeVar` or the new 3.12 generic syntax `def foo[T](x: T) -> T:` when appropriate.
- Use `collections.abc` for abstract types: `Sequence`, `Mapping`, `Iterable`, etc.

## Imports

Organise imports in three groups separated by blank lines:

1. Standard library
2. Third-party packages
3. Local / project packages

Each group is sorted alphabetically. Use absolute imports; avoid wildcard imports (`from x import *`).

## Naming Conventions

| Element         | Convention          | Example              |
|-----------------|---------------------|----------------------|
| Module          | `snake_case`        | `data_loader.py`     |
| Class           | `PascalCase`        | `DataLoader`         |
| Function/Method | `snake_case`        | `load_data()`        |
| Constant        | `UPPER_SNAKE_CASE`  | `MAX_RETRIES`        |
| Private         | `_leading_underscore` | `_parse_row()`     |

## Docstrings

Use **Google style** docstrings:

```python
def fetch_data(url: str, *, timeout: int = 30) -> bytes:
    """Fetch raw data from the given URL.

    Args:
        url: The endpoint to request.
        timeout: Seconds before the request times out.

    Returns:
        The raw response body as bytes.

    Raises:
        ConnectionError: If the server is unreachable.
    """
```

## Error Handling

- Catch **specific** exceptions — never bare `except:` or `except Exception:` without re-raising.
- Use `raise ... from ...` to chain exceptions and preserve tracebacks.
- Define custom exception classes in a dedicated `exceptions.py` module when the project grows.

## Project Structure (uv)

- Define project metadata and dependencies in `pyproject.toml`.
- Use `uv run` to execute project scripts and tools within the managed environment.
- Keep `uv.lock` committed for reproducible builds.
- Separate development dependencies with `uv add --dev`.
