# API Contracts: Computer Use Control Plane
**Branch**: `001-computer-use-api`

## REST Endpoints

### 1. `POST /api/v1/sessions`
Initializes a new session and provisions a VNC target constraint.
- **Request Body**:
  ```json
  {
      "user_id": "string"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
      "session_id": "uuid",
      "vnc_host": "string",
      "status": "idle"
  }
  ```

### 2. `GET /api/v1/sessions/{session_id}/history`
Fetches a chronological log of events that occurred in the session, persisted in PostgreSQL.
- **Response**: `200 OK`
  ```json
  {
      "messages": [
          {
              "type": "text",
              "role": "user",
              "content": "Click the start button.",
              "created_at": "timestamp"
          },
          {
              "type": "tool_call",
              "role": "assistant",
              "content": "{\"tool\": \"mouse\", \"action\": \"click\", \"x\": 100, \"y\": 100}",
              "created_at": "timestamp"
          }
      ]
  }
  ```

## WebSocket Connection

### 1. `WS /ws/v1/sessions/{session_id}?token={auth_token}`
Maintains the real-time agent loop streaming. The connection is held open, tracked by a global ConnectionManager mapped by `session_id`.

**Client → Server (Input)**
Client explicitly sends new prompts when the agent states are IDLE. If the loop is actively EXECUTING, new prompts are dropped or returned with an error over the socket.
```json
{
    "type": "user_prompt",
    "text": "Navigate to Google and search for Anthropic."
}
```

**Server → Client (Streamed Output)**
Server continuously streams text thoughts and tool actions as they happen without database I/O bottlenecks.
```json
// Example: Thought stream
{
    "type": "agent_thought_chunk",
    "text": "First, I'll need to move the mouse..."
}

// Example: Tool usage update
{
    "type": "tool_execution_start",
    "tool": "mouse",
    "action": "move_to"
}

// Example: VNC state update (Screenshot payload)
{
    "type": "vnc_screenshot_result",
    "base64_data": "data:image/png;base64,..."
}

// Example: Turn Ended
{
    "type": "agent_turn_complete"
}
```
