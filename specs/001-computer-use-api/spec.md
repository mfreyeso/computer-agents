# Feature Specification: Computer Use Agent Control Plane

**Feature Branch**: `001-computer-use-api`  
**Created**: 2026-03-18  
**Status**: Draft  
**Input**: User description: "Build a backend API that acts as the control plane for Anthropic's Computer Use agent. It must sit between a frontend application, the Anthropic Claude API, and a target VNC environment. The primary feature is an interactive \"Agent Loop\" that supports multiple concurrent user sessions. When a user sends a prompt, the system must stream Claude's intermediate steps (thoughts, tool requests) in real-time back to the frontend. If Claude requests a computer tool (like a mouse click or screenshot), the system must execute it in the VNC environment, capture the result, and transparently continue the loop. It must maintain strict isolation between user sessions to avoid race conditions (e.g., preventing users from interrupting the agent mid-task) and securely persist the conversation history of each session so users can resume past interactions."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-time Agent Stream (Priority: P1)

A user connects to the control plane via the frontend and sends a prompt asking the agent to perform a task. As the agent formulates its response, the user can see the agent's "thoughts" and "tool requests" streaming in real-time before the task is fully completed.

**Why this priority**: Real-time feedback is critical for the perceived responsiveness of long-running agent tasks and forms the core of the desired UX.

**Independent Test**: Can be tested by sending a prompt and validating that intermediate JSON/text tokens are streamed continuously to the UI before the definitive final response.

**Acceptance Scenarios**:

1. **Given** an active session, **When** the user sends a complex prompt, **Then** the UI receives intermediate thought tokens from the backend within 500ms.
2. **Given** an active session, **When** the agent decides to use a tool, **Then** the UI receives the tool execution request payload in real-time.

---

### User Story 2 - Transparent Tool Loop Execution (Priority: P1)

When the agent decides it needs to interact with the computer (e.g., clicking a button, taking a screenshot), the control plane automatically intercepts the tool request, executes the VNC operation, captures the UI state (e.g., a screenshot), and feeds it back to the agent without user intervention, continuing the loop until the goal is achieved.

**Why this priority**: The automatic execution of VNC tools is the core technical requirement for the "Computer Use" agent loop.

**Independent Test**: Can be fully tested by mocking an agent tool call, having the backend perform the VNC action, and verifying the result is returned to the agent loop orchestrator.

**Acceptance Scenarios**:

1. **Given** an agent loop, **When** the agent emits a "mouse_click" tool call, **Then** the backend executes the corresponding VNC click and returns the updated state to the agent.
2. **Given** an agent loop waiting on a computer interaction, **When** the VNC action fails, **Then** the failure error is passed elegantly back to the agent to try again.

---

### User Story 3 - Strict Session Isolation and Lock (Priority: P2)

Two users start sessions simultaneously. When User A's agent begins executing a long-running VNC task, User A tries to send another prompt mid-task. The system rejects the interruption, locking the session state to prevent race conditions. Meanwhile, User B's session runs smoothly without cross-contamination.

**Why this priority**: Prevents critical race conditions and dangerous VNC state mismatches, ensuring stability for concurrent users.

**Independent Test**: Can be tested by simulating multiple concurrent web requests and attempting to post new messages to a session that is currently marked as "executing".

**Acceptance Scenarios**:

1. **Given** an executing agent loop for Session A, **When** the user attempts to send another prompt to Session A, **Then** the system rejects the input with a "Task in progress" error.
2. **Given** 50 concurrent active sessions, **When** they all execute VNC macros, **Then** no session accesses or modifies another session's VNC target or conversation array.

---

### User Story 4 - Conversation History Resumption (Priority: P3)

A user finishes working with the agent, closes the application, and returns the next day. They can pull up their past session, view the historical interaction (including past VNC screenshots), and ask the agent a follow-up question seamlessly.

**Why this priority**: Enhances long-term user value and prevents task data loss.

**Independent Test**: Can be tested by terminating a session, fetching its ID from the persistent store, and successfully sending a new prompt that leverages context from the old messages.

**Acceptance Scenarios**:

1. **Given** a new connection, **When** the user requests a past session ID, **Then** the system returns the full ordered history of thoughts, tool calls, and text.
2. **Given** a resumed session, **When** the user sends a new prompt, **Then** the agent accurately references the prior context.

---

### Edge Cases

- What happens when the underlying VNC connection drops mid-execution?
- How does the system handle Anthropic API rate limiting or timeouts during an active loop?
- What occurs if a user's browser disconnects while the agent loop is still executing?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an asynchronous API for frontend clients to initiate text prompts.
- **FR-002**: System MUST stream Claude API intermediate outputs (thoughts, text, and tool requests) to the frontend continuously over a persistent connection (e.g., Server-Sent Events or WebSockets).
- **FR-003**: System MUST execute Claude's requested computer use tools (e.g., keyboard input, mouse input, screenshot) directly against the designated VNC environment.
- **FR-004**: System MUST capture the result of the VNC execution and feed it back into the Anthropic API to continue the execution loop.
- **FR-005**: System MUST enforce session locks while the "Agent Loop" is active, strictly rejecting new user prompts until the loop completes or fails.
- **FR-006**: System MUST securely persist all conversation history (including text, thoughts, tool inputs, and tool outputs/screenshots) to a datastore.
- **FR-007**: System MUST allow users to retrieve historical sessions and append new messages to them.
- **FR-008**: System MUST isolate concurrent sessions in memory and persistence layers to guarantee zero cross-contamination of context or VNC targets.
- **FR-009**: System MUST automatically provision a dedicated, isolated VNC environment dynamically for each new user session using container orchestration, and tear it down when the session concludes.

### Key Entities *(include if feature involves data)*

- **Session**: A continuous tracking context for an agent loop. Attributes: ID, UserID, VncEnvironmentId, State (`Idle`, `Executing`), CreatedAt, UpdatedAt.
- **Event/Message**: An entry in the session timeline. Attributes: SessionID, Role (user, assistant, tool), Type (text, thought, tool_call, tool_result), Content (text or JSON payload).
- **VncEnvironment**: The target environment configuration. Attributes: EnvironmentID, Host, Port, Status (Available, In-Use).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System streams initial LLM tokens to the frontend connection within 500ms of the API yielding them.
- **SC-002**: VNC tool execution and response payload formatting (e.g., generating and encoding a screenshot) completes in under 2 seconds on average.
- **SC-003**: System handles 100 concurrent independent sessions executing agent loops with zero instances of cross-session data contamination.
- **SC-004**: Users are prevented 100% of the time from interrupting via race-condition inputs while a session state is structurally locked.
- **SC-005**: Resumed session context accuracy is 100% (no missing messages from historical logs during a resumption).
