from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from graph.state import AgentState
from utils.logger import logger


# ============================================================
# Orchestrator Routing
# ============================================================

def route_after_orchestrator(state: AgentState):

    route = state.get("route")

    if route == "internal_rag":
        return "rag"

    if route in {
        "vendor_rag",
        "query_database",
        "web_search",
    }:
        return "tool"

    if route == "appointment":
        return "appointment"

    raise ValueError(
        f"Unknown route: {route}"
    )


# ============================================================
# RAG Routing
# ============================================================

def route_after_rag(state: AgentState):

    # HIGH RISK → ALWAYS HUMAN REVIEW
    if state.get("risk_level") == "high":
        logger.info(
            "High-risk request detected; "
            "triggering human review..."
        )
        return "human_review"

    # LOW RISK + sufficient RAG → response
    if state.get("retrieval_status") == "sufficient":
        return "response"

    # LOW RISK + insufficient RAG → web search
    logger.info(
        "Low-risk retrieval insufficient; "
        "triggering web search fallback..."
    )
    
    state["route"] = "web_search"

    return "tool"


# ============================================================
# Tool Evidence Routing
# ============================================================

def route_after_evidence(state: AgentState):

    # High-risk tool result → Human Review
    if state.get("risk_level") == "high":
        return "human_review"

    # Low-risk tool result → Response generation
    return "response"


# ============================================================
# Response Routing
# ============================================================

def route_after_response(state: AgentState):

    if state.get("risk_level") == "high":
        return "human_review"

    return "validator"


# ============================================================
# Human Review Routing
# ============================================================

def route_after_review(state: AgentState):

    status = state.get("review_status")

    # Human already supplied the final answer.
    # No LLM / validator required.
    if status in {
        "approved",
        "modified",
    }:
        return "end"

    if status == "rejected":
        return "rejected"

    raise ValueError(
        f"Unknown review status: {status}"
    )


# ============================================================
# Validation Routing
# ============================================================

MAX_RETRIES = 2


def route_after_validation(state: AgentState):

    if state.get("validation_status") == "valid":
        return "end"

    retry_count = state.get(
        "retry_count",
        0
    )

    if retry_count >= MAX_RETRIES:
        return "retry_exhausted"

    return "retry"
    