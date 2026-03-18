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

ui-install:
	cd src/ui && npm install

ui:
	cd src/ui && npm run dev

up:
	docker compose --env-file .env up --build -d

down:
	docker compose --env-file .env down

logs:
	docker compose logs -f
