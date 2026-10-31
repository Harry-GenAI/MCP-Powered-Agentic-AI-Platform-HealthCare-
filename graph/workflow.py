from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from graph.state import AgentState

from graph.nodes.orchestrator import orchestrator_node
from graph.nodes.rag import rag_node
from graph.nodes.tool import tool_node
from graph.nodes.response import response_node
from graph.nodes.human_review import human_review_node
from graph.nodes.validator import validator_node
from graph.nodes.rejection import rejection_node
from graph.nodes.retry import retry_node
from graph.nodes.retry_exhausted import retry_exhausted_node
from graph.nodes.appointment import appointment_node

from graph.routers import (
    route_after_orchestrator,
    route_after_rag,
    route_after_evidence,
    route_after_review,
    route_after_validation,
)

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# Graph Builder
# ============================================================

builder = StateGraph(AgentState)


# ============================================================
# Nodes
# ============================================================

builder.add_node(
    "orchestrator",
    orchestrator_node
)

builder.add_node(
    "appointment",
    appointment_node
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "tool",
    tool_node
)

builder.add_node(
    "response",
    response_node
)

builder.add_node(
    "human_review",
    human_review_node
)

builder.add_node(
    "rejected",
    rejection_node
)

builder.add_node(
    "retry",
    retry_node
)

builder.add_node(
    "validator",
    validator_node
)

builder.add_node(
    "retry_exhausted",
    retry_exhausted_node
)


# ============================================================
# Entry Point
# ============================================================

builder.add_edge(
    START,
    "orchestrator"
)


# ============================================================
# Orchestrator → RAG / MCP Tool / Appointment
# ============================================================

builder.add_conditional_edges(
    "orchestrator",
    route_after_orchestrator,
    {
        "rag": "rag",
        "tool": "tool",
        "appointment": "appointment",
    },
)


# ============================================================
# RAG → Response / Human Review / Web Search
# ============================================================

builder.add_conditional_edges(
    "rag",
    route_after_rag,
    {
        "response": "response",
        "human_review": "human_review",
        "tool": "tool",
    },
)


# ============================================================
# MCP Tool → Response / Human Review
# ============================================================

builder.add_conditional_edges(
    "tool",
    route_after_evidence,
    {
        "response": "response",
        "human_review": "human_review",
    },
)


# ============================================================
# Response → Validator
# ============================================================

# Response node is only reached for LOW-risk requests.
builder.add_edge(
    "response",
    "validator"
)


# ============================================================
# Human Review → END / Rejected
# ============================================================

builder.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "end": END,
        "rejected": "rejected",
    },
)


# ============================================================
# Validator → END / Retry
# ============================================================

builder.add_conditional_edges(
    "validator",
    route_after_validation,
    {
        "end": END,
        "retry": "retry",
        "retry_exhausted": "retry_exhausted",
    },
)


# ============================================================
# Retry
# ============================================================

builder.add_edge(
    "retry",
    "response"
)


# ============================================================
# Rejection
# ============================================================

builder.add_edge(
    "rejected",
    END
)


# ============================================================
# Retry Exhausted
# ============================================================

builder.add_edge(
    "retry_exhausted",
    END
)


# ============================================================
# Appointment
# ============================================================

builder.add_edge(
    "appointment",
    END
)


# ============================================================
# Export Builder
# ============================================================

# FastAPI compiles this with AsyncSqliteSaver.
graph = builder