# PharmaChain LangGraph workflow

`build_copilot_workflow` is an opt-in stateful workflow alongside the existing
deterministic `CopilotOrchestratorService` path. It does not replace that API.

```
initialize -> intent detection -> planning -> tools -> approval -> response
                         |              |          |
                         +--- error ----+----------+----> response
```

The workflow uses the existing `IntentEngine`, `ReasoningPlanner`,
`ToolRegistry`, and `ResponseComposer`. Tool execution preserves the planner's
ordering. Runtime dependencies are injected through the workflow factory's
`tool_context` (for example, `{ "db": session }`) rather than checkpointed
workflow state.

For `PROCUREMENT` intent, the approval node invokes LangGraph's `interrupt`.
Resume it with `Command(resume={"approved": True})` or `False`. This is a
simulated decision only: it annotates the final response and never creates,
approves, or changes a procurement request.

An interrupt must be compiled with a checkpointer and a stable `thread_id`:

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

workflow = build_copilot_workflow(
    planner=planner, registry=registry, composer=composer,
    checkpointer=MemorySaver(), tool_context={"db": db},
)
config = {"configurable": {"thread_id": "request-123"}}
paused = workflow.invoke({"question": "Should I reorder vaccine?"}, config=config)
completed = workflow.invoke(Command(resume={"approved": True}), config=config)
```

`MemorySaver` is intended for tests or process-local demonstrations; it does
not provide durable persistence. Configure a persistent LangGraph checkpointer
before relying on pause/resume across process restarts.

Run the focused tests from `backend`:

```powershell
python -m pytest tests/test_langgraph_workflow.py -q
```
