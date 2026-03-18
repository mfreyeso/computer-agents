# Energent Code: Computer Use Demo

Author: **Mario Reyes Ojeda**

A specialized AI Agent architecture that performs actions on a virtual desktop environment using Anthropic's Claude 3.5/3.7 Sonnet Computer Use capabilities.

The project manages isolated VNC sandbox environments locally, orchestrating them alongside a modernized React tracking UI and a FastAPI control plane.

## Technical Specifications & Component Integration

The application is structured into four main isolated components, leveraging Docker Compose:

1. **Frontend UI (`ui`)**: A React/Vite web application using Zustand and tailwindcss. Served statically via Nginx in production, it offers a 3-pane dashboard: Tasks Sidebar, live VNC Viewer, and an Execution Loop agent chat.
2. **Backend App (`app`)**: A Python-based FastAPI web server. It manages PostgreSQL connections using SQLAlchemy, exposes REST endpoints for Session managing, and WebSocket streams for real-time agent/user interactions.
3. **Database (`db`)**: A PostgreSQL 15 relational database storing session histories, chat sequences, and agent tool execution tokens.
4. **VNC Target (`vnc_target`)**: Built on top of `ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest`, extending it with a custom `tool_server.py`. It runs an Xvfb virtual display, a Tint2 panel, a noVNC server, and accepts HTTP requests from the `app` container to perform screen grabs and dispatch PyAutoGUI input events.

### Session Manager & Request Loop Sequence

The following sequence details how the system creates sessions, requests thoughts from Claude, and safely proxies tool executions to the isolated VNC target.

```mermaid
sequenceDiagram
    actor User as User
    participant UI as React UI
    participant API as FastAPI App
    participant DB as PostgreSQL
    participant AI as Anthropic API
    participant VNC as VNC Target (Tool Server)

    User->>UI: Create Session
    UI->>API: POST /api/sessions/
    API->>DB: Insert Session (IDLE)
    API-->>UI: Return Session ID
    
    User->>UI: Input Prompt Task
    UI->>API: WebSocket Connection (Send prompt)
    API->>DB: Save User Message
    
    loop Agent Execution Loop
        API->>AI: Stream messages.create(betas=["computer-use-2025-01-24"])
        AI-->>API: Stream tokens (Thoughts)
        API-->>UI: WS push (text chunks)
        
        opt Tool Execution Requested
            AI-->>API: tool_use (e.g. computer action)
            API-->>UI: WS push (tool_execution_start)
            API->>VNC: HTTP POST /execute (Tool Input)
            Note over VNC: Agent executes PyAutoGUI / Bash inside Xvfb
            VNC-->>API: Returns Base64 Screenshot + status
            API->>DB: Save Tool Execution Result
            API-->>UI: WS push (vnc_screenshot_result)
        end
    end
    API->>DB: Mark turn complete
```

### Deployment Pattern Architecture

Below is the Docker service mapping and network integration pattern:

```mermaid
graph TD
    subgraph Docker Network [energent_code_default]
        UI[UI Container<br/>React + Nginx]
        APP[App Container<br/>FastAPI + Uvicorn]
        DB[(DB Container<br/>PostgreSQL 15)]
        VNC[VNC Target Container<br/>Xvfb + noVNC + Tool Server]
    end

    User(Browser) -->|Port 5173| UI
    User(Browser) -->|Port 8000| APP
    User(Browser) -->|Port 8080| VNC
    User(Browser) -.->|Port 5900| VNC
    
    UI -->|WS / REST| APP
    APP -->|SQLAlchemy| DB
    APP -->|HTTP:8888| VNC
    
    APP <-->|External API| Anthropic(Anthropic API)
```

## Setup & Deployment Instructions

You will need Docker and Docker Compose installed on your host system.

### 1. Environment Variables

Create a `.env` file from the provided baseline:

```bash
cp .env.example .env
```

Edit `.env` and configure your keys (specifically `ANTHROPIC_API_KEY`).

### 2. Standard Deployment

To build and start all integrated Docker services locally, use the provided `Makefile`:

```bash
# Starts all containers in detached mode, provisioning the images
make up
```

Once running, the components are accessible at:

- **Main React Dashboard**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend (Swagger Docs)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Raw noVNC Stream**: [http://localhost:8080](http://localhost:8080)

### 3. Log Observation

To stream and parse the aggregate logs from all active microservices:

```bash
make logs
```

### 4. Teardown

To cleanly stop and remove the Docker containers, networks, and environment links:

```bash
make down
```

## Local Development Requirements (Optional)

If you wish to make changes to the backend or the frontend locally (outside of Docker), you can run the dependencies natively:

**For the Python Backend:**

```bash
uv sync            # Installs backend dependencies
make check         # Run ty type checker
make lint          # Run ruff linter
make format        # Format code with ruff
make test          # Run pytest
make all           # Lint + Check + Test sequentially
```

**For the React Frontend:**

```bash
make ui-install    # Installs JS dependencies in src/ui
make ui            # Starts local Vite development server
```
