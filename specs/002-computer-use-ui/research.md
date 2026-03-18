# Research & Technical Decisions: Computer Use UI

## 1. Web Framework
- **Decision:** React 18+ bundled with Vite.
- **Rationale:** React's component-based ecosystem is ideal for representing discrete layouts. Vite offers immediate hot-reloading perfect for adjusting UI elements and complex socket connections.
- **Alternatives Considered:** Next.js (Overkill for a purely client-side heavy SPA that doesn't need SSR/SEO).

## 2. Styling Solution
- **Decision:** Tailwind CSS.
- **Rationale:** Enables rapid styling without leaving JSX files. Extremely effective for creating a reliable three-pane grid layout using flexbox/grid classes without managing external CSS stylesheets.

## 3. VNC Integration
- **Decision:** `novnc` library (using the `novnc-core` or pure Canvas/Wrapper approaches).
- **Rationale:** noVNC is the industry standard for HTML5 VNC client integration. By passing the WebSocket VNC stream URL directly into the `novnc` client instance, it handles graphic rendering intuitively on an HTML5 canvas element inside the Middle Pane.

## 4. State Management
- **Decision:** Zustand.
- **Rationale:** While React Context is acceptable, Zustand offers cleaner syntax without provider-wrapping hell. It is perfect for storing the global `current_session_id`, holding the historical chats dynamically, and firing events when a session concludes or starts.

## 5. WebSocket Implementations
- **Decision:** Native `window.WebSocket`.
- **Rationale:** The FastAPI backend relies on standard WebSockets (via Starlette). Instead of importing heavy abstraction layers (like socket.io which requires a compatible backend), standard WebSocket event listeners tied to custom React Hooks (`useWebSocket`) will grant full lifecycle control (connect, message, error, close).

## 6. HTTP Client
- **Decision:** Native `fetch` API.
- **Rationale:** Modern fetch is sufficiently powerful for standard GET history API calls. No explicit need for Axios for simple payload retrievals.
