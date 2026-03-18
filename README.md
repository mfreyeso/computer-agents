# energent-code

A Python 3.12+ project managed with [uv](https://docs.astral.sh/uv/).

## Setup

```bash
uv sync
```

## Development

| Command         | Description              |
| --------------- | ------------------------ |
| `make install`  | Install all dependencies |
| `make check`    | Run ty type checker      |
| `make lint`     | Run ruff linter          |
| `make format`   | Format code with ruff    |
| `make test`     | Run pytest               |
| `make all`      | Lint + check + test      |
