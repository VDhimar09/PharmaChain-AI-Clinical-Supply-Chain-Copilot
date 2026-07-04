# PharmaChain AI Architecture

## Overview

PharmaChain AI Clinical Supply Chain Copilot is organized as a layered reasoning pipeline. Each layer has a clear responsibility so planning, execution, and response generation can evolve independently without forcing changes across the rest of the system.

High-level flow:

`Client -> FastAPI Chat API -> AIChatService -> CopilotTool -> ReasoningEngine -> ReasoningPlanner -> PlanningStrategy -> RuleBasedPlanner -> ExecutionPlan -> ToolRegistry -> Tools -> ResponseComposer`

## Reasoning Pipeline

The reasoning pipeline is intentionally split into deterministic stages:

1. `CopilotTool` receives the user message and routes the request.
2. `ReasoningPlanner` detects intent, creates a `PlannerContext`, and delegates plan construction to the configured `PlanningStrategy`.
3. `RuleBasedPlanner` produces an `ExecutionPlan` with an ordered list of tools and explicit planner reasoning.
4. `ReasoningEngine` executes the plan by retrieving tools from `ToolRegistry` and collecting structured evidence.
5. `ResponseComposer` converts structured evidence into a professional natural-language response for the client.

This flow keeps decision making explainable because every step produces explicit intermediate artifacts: intent, plan, tool results, and formatted reasoning.

## Planning Layer

The planning layer consists of:

- `PlannerContext`: Immutable planning inputs including user message, detected intent, available tools, and metadata.
- `PlanningStrategy`: The abstract contract for all planner implementations.
- `RuleBasedPlanner`: The current deterministic implementation that preserves the existing planning behavior.
- `ReasoningPlanner`: The orchestration layer that assembles context and delegates planning to a strategy.

This design uses the Strategy Pattern. New planners such as `LLMPlanner`, `HybridPlanner`, or `PolicyPlanner` can be added by implementing `PlanningStrategy` and injecting the new strategy into `ReasoningPlanner`.

## Execution Layer

The execution layer is built around:

- `ReasoningEngine`: Executes tools in the exact order defined by the execution plan.
- `ToolRegistry`: The single source of truth for tool discovery and retrieval.
- AI tools such as `InventoryTool`, `WarehouseTool`, `ShipmentTool`, and `ProcurementTool`.

`ReasoningEngine` does not need to know tool internals. It only depends on the registry contract and the execution plan. This keeps tool execution deterministic and easy to test without any database dependency in unit tests.

## Response Composition

`ResponseComposer` is a pure Python presentation component. It accepts structured evidence and returns a readable AI response with recommendation, confidence, summary, and reasoning sections.

This layer does not execute tools, access the database, or depend on FastAPI. That separation keeps response formatting reusable across chat surfaces, APIs, or future background workflows.

## Tool Registry

`ToolRegistry` centralizes tool registration, lookup, and duplicate prevention. The registry protects the execution layer from direct coupling to concrete tool classes and enables dynamic tool composition.

## Logging and Error Handling

The shared logging module at `app/core/logging.py` standardizes log format across AI components with timestamp, level, module, and message fields. The AI-specific exceptions in `app/ai/exceptions.py` give enterprise-friendly failure boundaries:

- `PlanningException` for planning failures
- `ToolExecutionException` for tool execution failures
- `ResponseCompositionException` for response formatting failures

These boundaries improve observability, operational debugging, and incident triage without changing business behavior on successful requests.

## Why This Follows Clean Architecture

The architecture follows Clean Architecture because responsibilities are separated by role:

- Planning decides which tools should run.
- Execution runs those tools.
- Response composition formats outputs for users.
- Tool registration manages available capabilities.

Each layer depends on abstractions or stable contracts instead of hard-coded orchestration logic.

## Why This Follows SOLID

- Single Responsibility Principle: planner, engine, registry, and composer each have one focused job.
- Open/Closed Principle: new planning strategies and tools can be added without rewriting the engine.
- Liskov Substitution Principle: any planner implementing `PlanningStrategy` can replace the current strategy.
- Interface Segregation Principle: small focused contracts keep modules from depending on unrelated behavior.
- Dependency Inversion Principle: `ReasoningPlanner` depends on `PlanningStrategy`, not a concrete planner implementation.

## Why This Supports Explainable AI

The system is explainable because it preserves structured intermediate reasoning:

- detected intent
- execution plan
- tool outputs
- procurement decision
- final composed explanation

That makes the AI assistant easier to audit, test, and improve in enterprise settings where traceability matters.
