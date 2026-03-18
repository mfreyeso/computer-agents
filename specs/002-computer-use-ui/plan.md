# Implementation Plan: Computer Use UI

## 1. Summary
A React+Vite frontend for the Anthropic Computer Use Control Plane. It leverages modern web technologies (Tailwind CSS, Zustand for global state, and Native WebSockets) to deliver a high-performance, responsive three-pane interface. It allows users to actively orchestrate the tool API loops while visually watching the virtual desktop inside an iframe/canvas VNC integration using noVNC.

## 2. Technical Context
- **Framework:** React 18+ powered by Vite.
- **Styling:** Tailwind CSS avoiding raw custom CSS footprint.
- **State Management:** Zustand to universally manage Session state cross-components without React Context hierarchies.
- **Live Video:** `novnc` library to bind the VNC output directly to an HTML5 canvas.
- **Networking:** Native `fetch` API for REST history/instantiation. Native `WebSocket` object handling for real-time chat payload parsing and appending.
- **Backend API Contract:** Relies heavily on endpoints `POST /api/v1/sessions`, `GET /api/v1/sessions/{session_id}/history`, and `WS /ws/v1/sessions/{session_id}`.

## 3. Constitution Check
- **Containerization:** The UI will be built as a multi-stage Docker build served by Nginx to join the existing docker-compose network seamlessly.
- **Async & Non-blocking Network:** Handled intrinsically by Javascript's event loop structure. WebSockets are strictly event-driven.
- **State Persistence:** Deferring historical truth to the backend PostgreSQL database, the frontend acts strictly as a dumb hydration layer, pulling history dynamically on navigation changes and dropping active arrays instantly on unmounts. No complex local storage management is required.

## 4. Work Breakdown (Project Structure)
1. Initialize the React/Vite scaffolding with Tailwind and Zustand. Create the top-level three-pane grid structure mappings (`index.css` global rules).
2. Construct the `LeftPanel`: integrate the initial REST fetch calls to list historical completed sessions. Implement the "Start New Agent Task" POST workflow.
3. Construct the `RightPanel`: wire the native WebSocket loop to stream Agent Thoughts, distinct visual block boundaries (User Block vs Tool Result vs Agent Action), and auto-scroll capabilities.
4. Construct the `MiddlePanel`: map the `novnc` canvas onto the currently active session details. Gracefully handle scaling the view inside a locked `div` bounding block and capturing VNC errors cleanly.
5. Create the global Zustand root store to connect the panels (when a user clicks a left panel item, the right and middle panes automatically update to match the session contextual properties).
6. Polish and test. Generate the Nginx Dockerfile.

## 5. Complexity Tracker
**Complexity Score:** 3/5
**Key Risks:**
- **Canvas Scaling:** Raw VNC screens natively are often fixed at 1024x768. Binding them into a fluid grid system safely using standard React resize hooks requires delicate coordinate mappings.
- **Render Thrashing:** If the backend streams 100 WebSocket chunk payloads per second, naive React mapping of chat states could lag the VNC render. The Zustand store must efficiently append states to avoid massive DOM re-renders inside `ChatPanel`.
