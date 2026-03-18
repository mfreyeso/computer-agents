---
name: Create Unit Tests
description: Generate comprehensive pytest unit tests following best practices including fixtures, parametrize, and the AAA pattern.
---

# Create Unit Tests with Pytest

When asked to create unit tests, follow every guideline below to produce high-quality, maintainable tests.

## General Principles

- Every test must be **isolated** — no test should depend on the state left by another.
- Tests must be **deterministic** — same result on every run, no randomness or time-dependence.
- Tests must be **fast** — avoid network calls, disk I/O, or sleeps unless absolutely necessary.
- Run tests with: `uv run pytest`.

## Test File & Naming

- Place test files in a `tests/` directory mirroring the source structure.
- Name test files `test_<module>.py`.
- Name test functions: `test_<function_name>_<scenario>_<expected_result>`.

  ```python
  def test_parse_date_valid_iso_format_returns_datetime(): ...
  def test_parse_date_empty_string_raises_value_error(): ...
  ```

- Group related tests in a class prefixed with `Test`:

  ```python
  class TestParseDate:
      def test_valid_iso_format_returns_datetime(self): ...
      def test_empty_string_raises_value_error(self): ...
  ```

## Arrange-Act-Assert (AAA)

Structure every test body in three clearly separated sections:

```python
def test_add_positive_numbers_returns_sum():
    # Arrange
    a, b = 3, 7

    # Act
    result = add(a, b)

    # Assert
    assert result == 10
```

## Fixtures (`@pytest.fixture`)

- Use fixtures for **setup and teardown** logic instead of duplicating code.
- Define narrowly scoped fixtures (default `function` scope) — widen only when necessary.
- Place shared fixtures in `conftest.py` at the appropriate directory level.
- Always type-annotate fixture return values.

```python
import pytest

@pytest.fixture
def sample_user() -> User:
    return User(name="Ada", email="ada@example.com")

def test_user_greeting(sample_user: User):
    assert sample_user.greeting() == "Hello, Ada!"
```

## Parametrize (`@pytest.mark.parametrize`)

- Use parametrize for **data-driven tests** — test the same logic with multiple inputs.
- Keep the parametrize decorator close to the test function.
- Use descriptive `id` strings to identify each case in the test output.

```python
import pytest

@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        pytest.param("hello", "HELLO", id="lowercase"),
        pytest.param("Hello World", "HELLO WORLD", id="mixed-case"),
        pytest.param("", "", id="empty-string"),
    ],
)
def test_to_upper_returns_uppercase(input_value: str, expected: str):
    assert to_upper(input_value) == expected
```

## Exception Testing (`pytest.raises`)

- Always test that functions raise the expected exceptions with a context manager.
- Use the `match` parameter to verify the error message when relevant.

```python
import pytest

def test_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        divide(1, 0)
```

## Mocking & Monkeypatching

- Prefer `monkeypatch` (built-in) over `unittest.mock.patch` for simple attribute or env var overrides.
- Use `unittest.mock.Mock` / `MagicMock` for complex interaction verification.
- Mock at the **boundary** — external APIs, databases, file systems — not internal logic.

```python
def test_fetch_data_uses_timeout(monkeypatch: pytest.MonkeyPatch):
    recorded: list[int] = []
    monkeypatch.setattr(
        "myapp.client.requests.get",
        lambda url, timeout: recorded.append(timeout) or MockResponse(),
    )
    fetch_data("https://example.com")
    assert recorded == [30]
```

## Temporary Files

- Use `tmp_path` (per-test) or `tmp_path_factory` (per-session) for any file I/O.
- Never write to the real file system.

```python
def test_write_report_creates_file(tmp_path):
    output = tmp_path / "report.txt"
    write_report(output)
    assert output.read_text() == "Report content"
```

## Markers

- Mark slow tests with `@pytest.mark.slow` and exclude them from fast CI runs.
- Use `@pytest.mark.skipif` and `@pytest.mark.xfail` to document known limitations.

## Coverage

- After generating all tests, run `uv run pytest --cov --cov-report=term-missing` to check coverage.
- Aim for **high coverage on business logic**; don't chase 100% on boilerplate.

## Checklist Before Finishing

- [ ] Every public function/method has at least one test.
- [ ] Edge cases and error paths are covered.
- [ ] Parametrize is used where 2+ inputs test the same behaviour.
- [ ] Fixtures are used for any shared setup.
- [ ] All tests pass: `uv run pytest`.
- [ ] No test depends on execution order.
