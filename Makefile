.PHONY: install check lint format test all

install:
	uv sync

check:
	uv run ty check

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest

all: lint check test
