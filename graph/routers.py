from graph.state import AgentState


def route_after_orchestrator(state: AgentState):

    route = state.get("route")

    if route == "internal_rag":
        return "rag"

    if route in {
        "external_rag",
        "query_database",
        "web_search",
    }:
        return "tool"

    raise ValueError(
        f"Unknown route: {route}"
    )


def route_after_response(state: AgentState):

    if state.get("risk_level") == "high":
        return "human_review"

    return "validator"


def route_after_review(state: AgentState):

    status = state.get("review_status")

    if status == "approved":
        return "validator"

    if status == "modified":
        return "validator"

    if status == "rejected":
        return "rejected"

    raise ValueError(
        f"Unknown review status: {status}"
    )



MAX_RETRIES = 2


def route_after_validation(state: AgentState):

    if state.get("validation_status") == "valid":
        return "end"

    retry_count = state.get("retry_count", 0)

    if retry_count >= MAX_RETRIES:
        return "max_retry"

    return "retry"