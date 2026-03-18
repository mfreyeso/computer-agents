# Feature Specification: Computer Use UI

**Feature Name:** Computer Use UI
**Short Name:** `computer-use-ui`
**Date:** 2026-03-18
**Status:** DRAFT

## 1. Feature Definition

**What is being built?**
A frontend web application that serves as the user interface for our Anthropic Computer Use FastAPI backend.

**What problem does it solve?**
It provides an intuitive, high-visibility control mechanism allowing operators to watch precisely what an autonomous computer-use agent is doing (via VNC) while simultaneously parsing its internal programmatic thoughts (via realtime chat) and reviewing past sessions.

**Who is it for?**
System operators, researchers, and users monitoring autonomous agents interacting with virtual environments.

## 2. User Stories & Acceptance Criteria

### User Story 1: Left Sidebar Navigation and Instantiation
**Priority:** P1
**Focus:** Navigability and Session Management

**As an** operator
**I want to** view past agent tasks and easily start new ones via a persistent sidebar
**So that** I can seamlessly manage the lifecycle of different agent executions.

**Acceptance Criteria:**
- The left sidebar displays a scrollable or paginated list of historical "Task" sessions retrieved from the backend.
- A prominent "Start a New Agent Task" button remains visible at the top of the sidebar.
- Selecting an existing task immediately requests and displays the historical context without forcing a full page browser reload.
- The active session is clearly highlighted in the list.

### User Story 2: Live Observation VNC Middle Panel
**Priority:** P1
**Focus:** Visual Verification

**As an** observer
**I want to** watch the live graphical desktop of the target virtual machine
**So that** I can visually verify the agent's cursor actions, typing, and window manipulations in real-time.

**Acceptance Criteria:**
- The center panel embeds a live graphical VNC stream of the virtual machine environment.
- The viewer maintains a stable, low-latency display connection that automatically scales or fits within the bounded middle pane boundaries.
- Connecting to a new active session dynamically targets the corresponding VNC port mapped by the backend without manual configuration.

### User Story 3: Real-Time Interaction feed
**Priority:** P1
**Focus:** Execution loop transparency and control

**As an** operator
**I want to** see a chronological stream of user queries, agent thoughts, and tool execution traces
**So that** I can read the internal rationale as the loop progresses.

**Acceptance Criteria:**
- The right panel displays a conversation feed resembling a chat interface.
- Data streams into the panel in strict real-time via WebSockets.
- Distinct visual block formatting exists separating User Queries, Agent Thoughts, Requested Function Calls, and Execution Results.
- A text input area locked to the bottom allows typing user directives into the active stream.

## 3. Functional Requirements

### 3.1 Layout Architecture
- The application must strictly adhere to a three-pane side-by-side design on desktop resolutions.
- Panes must be distinctly separated with clearly identifiable boundaries.

### 3.2 Connectivity
- The frontend must establish and continuously poll REST endpoints to aggregate the paginated Task History.
- The frontend must establish persistent, robust WebSocket connections when joining an active session to map stream events explicitly to the chat feed UI.

### 3.3 Error Resiliency
- In the event of an orphaned WebSocket or disconnected VNC frame, the UI must gracefully present a "Reconnecting" or "Error" visual indicator without crashing the application.
- The UI must block secondary User Prompts if the backend streams a "Task is in progress" execution lock warning.

## 4. Testing Scenarios

**Scenario 1: End-to-End Loop Observation**
- **Given** an operator starts a new session
- **When** the operator types "Open the calculator app"
- **Then** the chat feed streams the agent's thoughts within milliseconds, the VNC center pane visibly reflects a mouse movement and click, and the result is appended synchronously to the chat list.

**Scenario 2: History Resumption**
- **Given** several past executions exist
- **When** the operator clicks an older session ID in the Left Sidebar
- **Then** the VNC viewer re-establishes connectivity with that environment and the right Chat Panel hydrates instantly with the historical chronological message thread.

## 5. Key Entities

- **Session History List:** Array mappings containing session IDs, dates, and snippet names.
- **Chat Feed Block:** A contextual wrapper dictating whether a rendered message is a User Text, an Agent internal thought stream, a Tool Request, or a completed System Tool string.

## 6. Success Criteria

- **Interface Stability:** The three panes maintain proportional, responsive positioning across standard widescreen viewports (1080p+) with zero layout crashing during active streams.
- **Latency Performance:** Incoming WebSocket payloads reflect visually on the right-panel DOM within 500ms of local backend emission.
- **Completeness:** The layout captures the entirety of an Anthropic Computer iteration loop visibly in one holistic interface.

## 7. Dependencies & Assumptions

- **Desktop Form Factor:** Due to the spatial limitations of a three-pane (Sidebar + VNC Desktop + Chat) view, it is assumed the interface is rigorously designed for widescreen desktops rather than mobile smartphones.
- **Backend Availability:** It relies on the endpoints defined in the previously deployed FastAPI `001-computer-use-api` application schema.
