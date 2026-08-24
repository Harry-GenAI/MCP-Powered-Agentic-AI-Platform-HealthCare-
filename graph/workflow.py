from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from langgraph.graph import StateGraph, START, END

from graph.state import AgentState

from graph.nodes.orchestrator import orchestrator_node
from graph.nodes.rag import rag_node
from graph.nodes.tool import tool_node
from graph.nodes.response import response_node
from graph.nodes.human_review import human_review_node
from graph.nodes.validator import validator_node
from graph.nodes.rejection import rejection_node
from graph.nodes.retry import retry_node

from graph.routers import (
    route_after_orchestrator,
    route_after_response,
    route_after_validation,
    route_after_review
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


# ============================================================
# Entry Point
# ============================================================

builder.add_edge(
    START,
    "orchestrator"
)


# ============================================================
# Orchestrator → RAG / MCP Tool
# ============================================================

builder.add_conditional_edges(
    "orchestrator",
    route_after_orchestrator,
    {
        "rag": "rag",
        "tool": "tool",
    }
)


# ============================================================
# Retrieval / Tool → Response
# ============================================================

builder.add_edge(
    "rag",
    "response"
)

builder.add_edge(
    "tool",
    "response"
)


# ============================================================
# Response → Human Review / Validator
# ============================================================

builder.add_conditional_edges(
    "response",
    route_after_response,
    {
        "human_review": "human_review",
        "validator": "validator",
    }
)


# ============================================================
# Human Review → Validator
# ============================================================

builder.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "validator": "validator",
        "rejected": "rejected",
    }
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
        
    }
)


builder.add_edge(
    "rejected",
    END
)


# ============================================================
# 
# Exporting the BUILDER, not a compiled graph.
#
# FastAPI will compile it with AsyncSqliteSaver.
# ============================================================

graph = builder