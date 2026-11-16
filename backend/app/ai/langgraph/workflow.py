"""Factory for PharmaChain's opt-in, stateful LangGraph workflow."""

from __future__ import annotations

from typing import Any, Mapping

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.ai.langgraph.nodes import (
    approval_decision_node,
    detect_intent_node,
    initialize_node,
    planning_node,
    response_composition_node,
    route_after_planning,
    route_after_tools,
    route_after_validation,
    tool_execution_node,
)
from app.ai.langgraph.state import CopilotState
from app.ai.planner.reasoning_planner import ReasoningPlanner
from app.ai.response import ResponseComposer
from app.ai.tools.tool_registry import ToolRegistry


def build_copilot_workflow(
    *,
    planner: ReasoningPlanner,
    registry: ToolRegistry,
    composer: ResponseComposer,
    checkpointer: BaseCheckpointSaver | None = None,
    tool_context: Mapping[str, Any] | None = None,
):
    """Build a graph without changing the legacy synchronous copilot API.

    Supplying a checkpointer is required to pause and resume an approval
    interrupt. ``MemorySaver`` is appropriate for tests and is not durable.
    """
    graph = StateGraph(CopilotState)
    graph.add_node("initialize", initialize_node)
    graph.add_node("detect_intent", detect_intent_node)
    graph.add_node("planning", lambda state: planning_node(state, planner=planner))
    graph.add_node(
        "tools",
        lambda state: tool_execution_node(
            state,
            registry=registry,
            context=tool_context,
        ),
    )
    graph.add_node("approval", approval_decision_node)
    graph.add_node(
        "response",
        lambda state: response_composition_node(state, composer=composer),
    )

    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "detect_intent")
    graph.add_conditional_edges(
        "detect_intent",
        route_after_validation,
        {"planning": "planning", "response": "response"},
    )
    graph.add_conditional_edges(
        "planning",
        route_after_planning,
        {"tools": "tools", "response": "response"},
    )
    graph.add_conditional_edges(
        "tools",
        route_after_tools,
        {"approval": "approval", "response": "response"},
    )
    graph.add_edge("approval", "response")
    graph.add_edge("response", END)
    return graph.compile(checkpointer=checkpointer)
