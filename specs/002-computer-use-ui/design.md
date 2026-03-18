# Architecture Design: Computer Use UI

## 1. System Context

The frontend UI operates as the client in a Client-Server topology. It consumes the FastAPI `002-computer-use-api` endpoints exclusively for task management, VNC port acquisition, and history parsing, while simultaneously maintaining dual real-time websocket flows (one to the FastAPI stream processor natively, and another to the target virtual machine's embedded VNC proxy).

## 2. Component Hierarchy

- `App` (Root Layout containing the grid split)
    - `SidebarList` (Left pane)
       - `NewTaskButton`
       - `TaskItem` (Mapping through historical responses)
    - `VncViewer` (Middle pane)
       - The Canvas injected by `<novnc>`
    - `ChatPanel` (Right pane)
       - `ChatList` (Chronological feed)
          - `UserMessageBubble`
          - `AgentThoughtBubble`
          - `ToolExecutionBubble`
       - `ChatInputForm` (Locked strictly to the bottom)

## 3. State Management (Zustand Store)

```javascript
type SessionStore = {
  currentSessionId: string | null;
  sessionState: 'idle' | 'running' | 'completed' | 'error';
  chatHistory: ChatMessage[];
  
  // Actions
  setSession: (id: string) => void;
  appendMessage: (msg: ChatMessage) => void;
  clearSession: () => void;
  fetchHistoricalMessages: (id: string) => Promise<void>;
  updateSessionState: (state: string) => void;
}
```

## 4. Native WebSocket Integration Model

The Chat panel utilizes a customized React Hook `useAgentSocket(sessionId)`:
1. When `sessionId` changes and the state is actively `running`, it mounts the native `WebSocket` object pointing to `ws://localhost:8000/ws/v1/sessions/{sessionId}`.
2. The `onmessage` handler intercepts Anthropic chunk payloads, transforming them instantly via the `appendMessage` method on the global Zustand store to force instantaneous React renders.
3. Unmounting closes the socket gracefully.

## 5. VNC Integration Model

The VNC Panel parses the currently active session object. If a valid `vnc_environment` configuration exists containing an active port, the component initializes an `@novnc/novnc` `RFB` constructor pointed directly to the Vnc container, piping graphical pixels onto an unmanaged `<canvas>` ref inside the VncViewer node.
