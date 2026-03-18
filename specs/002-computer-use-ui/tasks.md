# Task Breakdown: Computer Use UI

## Phase 1: Setup & Scaffolding
- [ ] T001 Bootstrapping frontend boilerplate using `npm create vite@latest src/ui -- --template react` in `src/ui`.
- [ ] T002 Install core dependencies (`tailwindcss`, `zustand`, `@novnc/novnc`, `lucide-react`, `date-fns`).
- [ ] T003 Setup `tailwind.config.js` and clear default CSS bloat in `index.css`.
- [ ] T004 Build generic three-pane skeleton layout utilizing Tailwind grid/flex inside `src/ui/src/App.jsx`.

## Phase 2: Global State Management
- [ ] T005 Construct Zustand global state mapping inside `src/ui/src/store/sessionStore.js` (including `currentSessionId`, `history`, and `status`).
- [ ] T006 Implement API networking abstractions via standard Fetch for POSTing new sessions or retrieving historical session lists in `src/ui/src/api/client.js`.

## Phase 3: User Story 1 - Left Sidebar Navigation
- [ ] T007 Implement the `SidebarList.jsx` component resolving global sessions by calling the endpoints and mapping states.
- [ ] T008 Add the bold `Start a New Agent Task` button triggering the `POST` request natively and mutating the global `currentSessionId`.

## Phase 4: User Story 2 - VNC Observation
- [ ] T009 Construct the `VncViewer.jsx` embedding an empty unmanaged Canvas node.
- [ ] T010 Hook up the `@novnc/novnc` JS bindings dynamically reading the `currentSessionId` properties and proxying graphical packets locally onto the unmanaged target Canvas.
- [ ] T011 Handle viewport `ResizeObserver` rules maintaining an accurate desktop grid without crashing React.

## Phase 5: User Story 3 - Interactive Real-time Chat
- [ ] T012 Implement `ChatPanel.jsx` rendering the core input forms and iterating over the arrays bounded heavily by auto-scrolling rules.
- [ ] T013 Construct UI component variants mapping to internal loops (`UserMessageBubble.jsx`, `AgentThoughtBubble.jsx`, `ToolResultBubble.jsx`).
- [ ] T014 Develop `useAgentSocket.js` hook managing native HTML5 WebSocket bindings matching the `currentSessionId`, pushing the incremental payloads sequentially into the Zustand reducer logic.

## Phase 6: Polish & Containerization
- [ ] T015 Inject generic connection resilient loaders rendering overlay states if the UI hits errors polling standard REST servers.
- [ ] T016 Setup UI Dockerfile wrapping production bundles gracefully via `nginx` alongside the primary composition tree.
