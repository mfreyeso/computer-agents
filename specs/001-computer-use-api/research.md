# Phase 0: Research & Technical Approach
**Feature**: Computer Use Control Plane
**Branch**: `001-computer-use-api`

## Outline of Decisions

### 1. Web Framework & Real-Time Communication
- **Decision**: FastAPI with WebSockets for the Agent Loop, REST for session history.
- **Rationale**: FastAPI has first-class `async_io` support required for concurrent, high-throughput streaming. WebSockets enable the lowest latency, bi-directional persistent connection to stream Claude's output (thoughts, tool results) in real-time, while standard REST fits historical retrieval effectively.
- **Alternatives considered**: Server-Sent Events (SSE). We chose WebSockets because they allow for bidirectional continuous polling (i.e. if the user wants to interrupt gracefully before the session locks or send complex continuous payloads).

### 2. Concurrency & Event Loop Protection (CPU-bound Tool Tasks)
- **Decision**: Python 3.13+ free-threading (GIL disabled) utilizing separate thread pools for VNC screenshot encoding and tool executions, maintaining `asyncio` for I/O and networking.
- **Rationale**: Python 3.13 allows threads to run in true parallel when CPU-bound. Since capturing/encoding VNC screens would otherwise block the async event loop, offloading to threads guarantees the `asyncio` loop remains fast and streams without hitching. This meets the Core Principle of strict non-blocking networks.
- **Alternatives considered**: Multiprocessing (ProcessPoolExecutor). Rejected due to higher memory overhead and IPC costs compared to free-threading.

### 3. Session Locking & Isolation
- **Decision**: In-memory `asyncio.Lock()` attached to a global Connection Manager matching session IDs. 
- **Rationale**: Strict and simplistic guarantee to enforce the constitutional requirement preventing race conditions during execution.

### 4. Database & State Flush Pattern
- **Decision**: PostgreSQL for persistent long-term storage, but active Agent Loop history lives in an in-memory session object and is only "flushed" to PostgreSQL when the Agent returns an `end_turn` stop reason.
- **Rationale**: Database writes (I/O) during every single token/thought stream or repetitive tool call would saturate Postgres and bottleneck the event loop. In-memory batching with bulk flushes adheres to the clean data engineering constitutional principle. 

### 5. Deployment Orchestration
- **Decision**: Containerized orchestration using Docker Compose for the FastAPI App, PostgreSQL Database, and the VNC static pool.
- **Rationale**: Matches the containerization and robust isolation requirement. 

### 6. VNC Tool Execution Logic
- **Decision**: Integration of the official `anthropic-quickstarts/computer-use-demo` Python modules.
- **Rationale**: Prevents reinventing the VNC/PyAutoGUI bindings required specifically for Claude's computer use standard.
