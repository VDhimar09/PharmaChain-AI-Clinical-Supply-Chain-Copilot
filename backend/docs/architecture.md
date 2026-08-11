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

## Grounded Copilot: RAG Integration (Phase 3)

The reasoning pipeline above (Executive Copilot) and the RAG document pipeline (`RetrieverService` → `ContextBuilder` → `RagGenerationService`, see `POST /api/rag/query`) were built and shipped as two independent systems. **RAG was not part of the Copilot before this phase.** Phase 3 integrates them at a single, explicit boundary - `GroundedCopilotService` (`app/services/grounded_copilot_service.py`) - without rewriting either system and without turning RAG into "just another Copilot tool". Operational evidence (live database facts) and document evidence (retrieved PDF chunks) keep different trust semantics all the way through.

### Where it connects

```
POST /api/ai/copilot/chat
        |
        v
GroundedCopilotService.chat(message)
        |
        v
EvidenceRequirementDetector.detect(message)
        |
   -------------------------------------------------
   |                    |                          |
OPERATIONAL          DOCUMENT          OPERATIONAL_AND_DOCUMENT
   |                    |                          |
   v                    v                          v
CopilotOrchestratorService   RagGenerationService   both gathered independently,
(unchanged)                  (unchanged)            then combined via one grounded
   |                    |                          LLM synthesis call
   v                    v                          |
CopilotChatResponse   CopilotChatResponse           v
                                              CopilotChatResponse
                                              (response cites document
                                               evidence via SOURCE_N,
                                               validated server-side)
```

### Evidence requirement detection

`EvidenceRequirementDetector` (`app/ai/evidence_requirement.py`) classifies a question into `OPERATIONAL`, `DOCUMENT`, or `OPERATIONAL_AND_DOCUMENT` using a deterministic keyword check, not an LLM call. It is intentionally separate from `IntentEngine`, which classifies *which operational tools* a question needs - `IntentEngine` is reused read-only as a signal ("does this also look operational?"), never modified or replaced.

### The shared evidence contract

`app/schemas/grounded_copilot.py` defines a typed contract used internally by `GroundedCopilotService`:

```
GroundedEvidence
|-- operational_evidence: list[OperationalEvidenceItem]   (tool, tool_key, status, data)
`-- document_evidence:    list[DocumentEvidenceItem]      (source_id, document_id, chunk_id,
                                                             filename, page_number, content,
                                                             similarity)
```

`OperationalEvidenceItem` reshapes the existing `CopilotEvidenceBundle` (no new tool execution, no recomputation). `DocumentEvidenceItem` mirrors `ContextItem`/`Citation` from the RAG pipeline - it does not introduce a second citation system. Citation trust stays entirely inside `app/services/citation_resolver.py` (extracted from `RagGenerationService` in this phase so both `RagGenerationService` and `GroundedCopilotService` resolve `SOURCE_N` references through the exact same, single validation path - an LLM-invented source id is always dropped, never surfaced).

### Routing behavior

- **`OPERATIONAL`** - calls `CopilotOrchestratorService.chat()` directly, unchanged. No LLM call. Identical behavior/response shape to before Phase 3 for every operational-only question (e.g. *"Show me delayed shipments."*).
- **`DOCUMENT`** - calls `RagGenerationService.query()` directly, unchanged, including its own no-evidence fallback (no LLM call at all when nothing relevant was retrieved) and server-side citation validation.
- **`OPERATIONAL_AND_DOCUMENT`** - both are gathered independently (`CopilotOrchestratorService.chat()` and `RetrieverService.search()` + `ContextBuilder.build()`), assembled into a `GroundedEvidence`, and passed to one LLM synthesis call whose system prompt requires it to: use only the supplied evidence, distinguish live operational state from documented procedure, and cite document evidence with a real `SOURCE_N` id (never an operational fact). The answer is only trusted if `citation_resolver.resolve_citations()` finds at least one real, retrieved source; otherwise the deterministic operational answer is returned instead of an unverified synthesis.

### Failure handling

- An operational tool failure (`AIException`) never fabricates operational evidence - the combined path degrades to a document-only answer via the unchanged RAG pipeline.
- A document retrieval failure never fabricates document evidence - the combined path degrades to the operational answer alone.
- If both sources are unavailable, or LLM synthesis itself fails, `GroundedCopilotError` is raised and mapped to `HTTP 503` at the API layer (mirrors `RagGenerationError`).

### RBAC

`copilot.use` and `rag.query` are independent permissions. `GroundedCopilotService` checks `rag.query` itself before ever calling `RetrieverService` - a caller with only `copilot.use`:

- gets a normal operational answer for an operational-only or combined question (document evidence is simply never fetched on their behalf for a combined question), and
- gets `HTTP 403` for a document-only question, rather than a silently empty/fabricated answer.

This reuses the same permission-checking logic `require_permission` is built on (`app.dependencies.auth.user_has_permission`), so there is exactly one RBAC source of truth.

### API compatibility

`CopilotChatResponse` gained four additive, defaulted fields - `evidence_requirement`, `grounded`, `document_evidence`, `citations`. Every pre-Phase-3 field is unchanged, so existing clients/tests that only read `response`, `evidence`, `tools_used`, etc. continue to work without modification.

## Why This Supports Explainable AI

The system is explainable because it preserves structured intermediate reasoning:

- detected intent
- execution plan
- tool outputs
- procurement decision
- final composed explanation

That makes the AI assistant easier to audit, test, and improve in enterprise settings where traceability matters.
