---

description: "Task list template for feature implementation"
---

# Tasks: Computer Use Control Plane

**Input**: Design documents from `/specs/001-computer-use-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan (src, tests)
- [ ] T002 Initialize Python 3.13 project with `uv` and dependencies (FastAPI, WebSockets, PyAutoGUI, SQLAlchemy)
- [ ] T003 [P] Configure linting and formatting tools (`ruff`, `ty`, `pytest`) in `pyproject.toml`
- [ ] T004 [P] Create `docker-compose.yml` and `Dockerfile` for orchestrated app, DB, and VNC containers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Setup database schema/models (`Session`, `Message`, `VncEnvironment`) in `src/database/models.py`
- [ ] T006 Initialize FastAPI application and base routing structure in `src/main.py`
- [ ] T007 Configure core application settings and environment variables in `src/core/config.py`
- [ ] T008 Configure async database engine and session maker in `src/database/session.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-time Agent Stream (Priority: P1) 🎯 MVP

**Goal**: Establish the basic WebSocket connection and stream Claude text chunks back to the user.

**Independent Test**: Can be fully tested by sending a prompt over WS and validating that intermediate JSON/text tokens are streamed continuously to the UI.

### Implementation for User Story 1

- [ ] T009 [P] [US1] Create REST endpoint for creating a session (`POST /api/v1/sessions`) in `src/api/endpoints/sessions.py`
- [ ] T010 [P] [US1] Create global ConnectionManager for WebSockets in `src/core/concurrency.py`
- [ ] T011 [US1] Create WebSocket endpoint base (`WS /ws/v1/sessions/{session_id}`) in `src/api/endpoints/websockets.py`
- [ ] T012 [P] [US1] Implement Anthropic Client wrapper and streaming async generator in `src/services/anthropic_client.py`
- [ ] T013 [US1] Integrate Anthropic Client inside the WebSocket endpoint to stream chunks continuously back to the client

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Transparent Tool Loop Execution (Priority: P1)

**Goal**: Execute PyAutoGUI/VNC tool calls requested by Claude and feed them back completely independently.

**Independent Test**: Can be fully tested by mocking an agent tool call, having the backend perform the action, and verifying the result is returned to the agent loop orchestrator.

### Implementation for User Story 2

- [ ] T014 [P] [US2] Import and adapt `anthropic-quickstarts/computer-use-demo` scripts into `src/services/computer_use.py`
- [ ] T015 [P] [US2] Configure Python 3.13 free-threading ThreadPoolExecutor in `src/core/concurrency.py`
- [ ] T016 [US2] Wire Claude tool loop logic to invoke offloaded VNC actions via the ThreadPool in `src/services/anthropic_client.py`
- [ ] T017 [US2] Capture and Base64 encode VNC screenshots natively handling resolution mapping returning gracefully to Claude

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently as a full Computer Use Loop.

---

## Phase 5: User Story 3 - Strict Session Isolation and Lock (Priority: P2)

**Goal**: Prevent cross-contamination and reject user interruptions during agent execution.

**Independent Test**: Can be tested by simulating multiple concurrent web requests and attempting to post new messages to a session that is currently marked as "executing".

### Implementation for User Story 3

- [ ] T018 [P] [US3] Instantiate `asyncio.Lock` mapped by `session_id` within the `ConnectionManager` in `src/core/concurrency.py`
- [ ] T019 [US3] Acquire the session lock synchronously before initiating the Anthropic API loop in `src/api/endpoints/websockets.py`
- [ ] T020 [US3] Catch client payloads over WebSocket while locked and emit strict error messages "Task is in progress" avoiding contamination

**Checkpoint**: All sessions execute fully locked parallel instances safely.

---

## Phase 6: User Story 4 - Conversation History Resumption (Priority: P3)

**Goal**: Persist events cleanly after completion and allow REST retrieval for previous contextual bootstrapping.

**Independent Test**: Terminate a session, fetch its ID from the persistent store, and successfully send a new prompt over WS that leverages context.

### Implementation for User Story 4

- [ ] T021 [P] [US4] Implement `GET /api/v1/sessions/{session_id}/history` REST endpoint in `src/api/endpoints/sessions.py`
- [ ] T022 [P] [US4] Build bulk history DB insert/flush method based on `end_turn` detection in `src/database/session.py`
- [ ] T023 [US4] Fetch historical messages array during WebSocket startup to hydrate Claude's context window internally.

**Checkpoint**: Seamless restarts mapped completely.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T024 Code cleanup and refactoring across models and schemas
- [ ] T025 Confirm all Free-threading parallel tasks are isolated from the main async loop
- [ ] T026 Add comprehensive error logging in `src/core/logging.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup**: No dependencies - can start immediately
- **Foundational**: Depends on Setup completion - BLOCKS all user stories
- **User Stories**: All depend on Foundational completion.
- Note: Both US1 & US2 encompass the core agent loop loop and often work hand-in-hand, but US1 tests purely text bridging first. US3 and US4 must follow sequentially.

### Parallel Opportunities

- Fast setup (T003, T004) can run in parallel while creating the app structures.
- DB Schemas (T005), App routing (T006), and environment config (T007) parallelizable foundational segments.
- REST Session endpoints (T009) and ConnectionManager (T010) logic parallelized inside US1.
- Computer-Use integration classes (T014) setup parallel to App concurrency execution pools (T015).
- Rest History endpoints (T021) and DB flush mechanisms (T022).

---

## Implementation Strategy

### MVP First (User Story 1 & 2 Together)

1. Complete Setup + Foundational
2. Establish WebSocket loop (US1) streaming thoughts in response to pure text.
3. Hook PyAutoGUI free-threading execution handling (US2).
4. **STOP and VALIDATE**: Confirm the computer-use loop completes effectively with VNC screenshots.

### Incremental Delivery

1. Follow MVP with US3 Isolation locking to guarantee multi-tenancy.
2. Complete data engineering flush and restoration pipeline via US4. 
