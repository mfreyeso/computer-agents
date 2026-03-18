# Quickstart: Computer Use Control Plane
**Branch**: `001-computer-use-api`

This module provides an interactive backend control plane mediating between the Claude API and an isolated target VNC environment. It streams agent iterations to the user via WebSockets in real-time, executing tools parallelly in Python 3.13 free-threads to prevent Event Loop blocking.

## Prerequisites

- [Docker Desktop / Docker Compose](https://docs.docker.com/engine/install/) running on your system.
- Anthropic API Key
- `uv` installed in the Python environment
- PostgreSQL database provisioned via Docker

## Setup Dependencies

1. Initialize `uv`
   ```bash
   uv sync
   uv pip install fastapi uvicorn websockets psycopg2-binary anthropic pyautogui ...
   ```
2. Export your API Key:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-XXXXXXXXXXXXX"
   ```

## Starting the Application

The application stack connects PostgreSQL, a VNC base server, and the FastAPI orchestrator. Start it entirely through docker compose:

```bash
docker-compose up -d
```
(Alternatively, to run the FastAPI app manually on the host while pointing to the db):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running the API

1. **Initialize a session**
   ```bash
   curl -X POST http://localhost:8000/api/v1/sessions \
        -H "Content-Type: application/json" \
        -d '{"user_id": "demo-user-1"}'
   ```
2. **Connect via WebSocket**
   Open a WebSocket to `ws://localhost:8000/ws/v1/sessions/{session_id}`.

3. **Send a prompt**
   Push `{ "type": "user_prompt", "text": "Open the calculator and do 2+2" }` over the socket and listen for streaming replies and base64 VNC screenshots in real-time.
