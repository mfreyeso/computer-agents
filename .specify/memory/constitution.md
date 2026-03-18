<!--
# Sync Impact Report
Version change: 1.0.0 (initial)
Modified principles:
- I. Async-First I/O
- II. Strict Concurrency & Thread-Safety
- III. Robust Session Isolation & Containerization
- IV. Clean Data Engineering
- V. Quality & Type Safety
Templates requiring updates:
- ✅ .specify/templates/plan-template.md 
- ✅ .specify/templates/spec-template.md 
- ✅ .specify/templates/tasks-template.md 
Follow-up TODOs: None
-->
# energent-code Constitution
<!-- High-performance AI integration API -->

## Core Principles

### I. Async-First I/O

All network operations and I/O tasks MUST be explicitly non-blocking. Synchronous calls that block the main event loop are strictly prohibited. The rationale is to ensure high throughput and low latency for the integration API without tying up resources.

### II. Strict Concurrency & Thread-Safety

We embrace modern Python patterns and prepare for Python 3.13+ free-threading capabilities. Concurrency controls MUST be strict and explicit to prevent race conditions during CPU-bound tasks. Shared state should be minimized, and robust synchronization primitives used where necessary. The rationale is to safely utilize all processing power without data corruption.

### III. Robust Session Isolation & Containerization

All components MUST be containerized. Strong session isolation MUST be enforced to prevent cross-contamination between API requests and to ensure secure, reliable independent execution environments. The rationale is to provide independent execution and scaling.

### IV. Clean Data Engineering

State persistence MUST be reliable and clean, offloaded correctly so as not to bottleneck the main event loop. Data integrity, correct data modeling, and clean engineering practices are mandatory. The rationale is to maintain accurate API state while handling high volumes.

### V. Quality & Type Safety

All code MUST leverage `ty` for comprehensive type checking, `ruff` for strict linting/formatting, and `pytest` for testing, as configured via `uv`. All code must be strongly typed with modern typing constructs.

## Additional Constraints

All components MUST run within isolated containers (e.g., Docker) to guarantee repeatable environments and facilitate scaling. Network configurations and external dependencies MUST support asynchronous integration patterns.

## Development Workflow

- All type checks (`ty`), linter rules (`ruff`), and tests (`pytest`) MUST pass prior to any code integration.
- CPU-bound tasks MUST be isolated or correctly handled with appropriate concurrency mechanisms to avoid delaying async event loops.
- No new features can be merged without clear session isolation mechanisms validated in tests.

## Governance

All changes to this Constitution MUST go through a formal amendment procedure, requiring documentation of the change, approval from maintainers, and a migration plan if necessary.
Versioning Policy follows semantic versioning (MAJOR for breaking governance changes, MINOR for new principles, PATCH for clarifications).
Compliance Review Expectations: All Pull Requests MUST be validated against these strict concurrency, non-blocking rules, and session isolation requirements.

**Version**: 1.0.0 | **Ratified**: 2026-03-18 | **Last Amended**: 2026-03-18
