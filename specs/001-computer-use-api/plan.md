# Implementation Plan: Computer Use Control Plane

**Branch**: `001-computer-use-api` | **Date**: 2026-03-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-computer-use-api/spec.md`

## Summary

The project consists of implementing a robust, containerized FastAPI backend that acts as the control plane between Anthropic's Claude API, a frontend client, and a target VNC environment. It leverages WebSockets for real-time bidirectional streaming of thoughts and tool requests, using true CPU-bound parallelism via Python 3.13 free-threading to execute PyAutoGUI/VNC tools without blocking the `asyncio` event loop. Isolated PostgreSQL persistence is designed to gracefully handle session history logging while avoiding race conditions via strict per-session concurrency locks.

## Technical Context

**Language/Version**: Python 3.13+ (Free-threading enabled)
**Primary Dependencies**: FastAPI, Uvicorn, WebSockets, PyAutoGUI, Anthropic SDK, asyncpg (or psycopg2-binary + SQLAlchemy)
**Storage**: PostgreSQL (Persistent), In-memory (Active Session WebSocket connection)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux Server (Docker container orchestration)
**Project Type**: Backend Web Service / Integration API
**Performance Goals**: Stream start <500ms, VNC action + UI encoding <2s
**Constraints**: Strict isolation, preventing blocking of the async event loop during CPU-bound screenshot base64 encoding
**Scale/Scope**: Multitenant concurrent independent user sessions.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Async-First I/O (Non-blocking networking)
- [x] Strict Concurrency & Thread-Safety (Python 3.13+ free-threading preparation)
- [x] Containerization & Session Isolation
- [x] Clean Data Engineering & Reliable Persistence
- [x] Quality & Type Safety (uv, ty, ruff, pytest)

## Project Structure

### Documentation (this feature)

```text
specs/001-computer-use-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md           # API Contract definition
└── tasks.md             # Phase 2 output (to be generated next)
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── routes.py
│   └── endpoints/
├── core/
│   ├── config.py
│   ├── logging.py
│   └── concurrency.py      # ConnectionManager, Locks
├── database/
│   ├── models.py
│   └── session.py
├── services/
│   ├── anthropic_client.py # Claude API Integration
│   └── computer_use.py     # Offloaded VNC/PyAutoGUI Threads
└── main.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Standard monolithic web service structure mapping cleanly to the constitutional requirement of a containerized application with segregated responsibilities.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*All constitution checks passed elegantly with Python 3.13 free-threading and WebSocket integration.*
