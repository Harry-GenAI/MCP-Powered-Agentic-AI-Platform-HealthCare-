from langgraph.types import interrupt

from graph.state import AgentState


async def human_review_node(state: AgentState) -> AgentState:

    review = interrupt({
        "type": "human_review",
        "risk_level": state.get("risk_level", "high"),
        "request_type": state.get("request_type", ""),
        "user_query": state.get("user_query", ""),
        "context": state.get("context", ""),
        "sources": state.get("sources", []),
        "message": (
            "This high-risk request requires review by an "
            "authorized healthcare reviewer before a final "
            "response can be provided."
        ),
        "allowed_decisions": [
            "approve",
            "modify",
            "reject",
        ],
    })

    decision = review.get("decision")

    if decision == "approve":
        return {
            "review_status": "approved",
            "reviewer_feedback": review.get(
                "reviewer_feedback", ""
            ),
            "final_answer": review.get(
                "final_answer", ""
            ),
        }

    if decision == "modify":
        return {
            "review_status": "modified",
            "reviewer_feedback": review.get(
                "reviewer_feedback", ""
            ),
            "final_answer": review.get(
                "final_answer", ""
            ),
        }

    if decision == "reject":
        return {
            "review_status": "rejected",
            "reviewer_feedback": review.get(
                "reviewer_feedback", ""
            ),
            "final_answer": "",
        }

    raise ValueError(
        f"Invalid human review decision: {decision}"
    )