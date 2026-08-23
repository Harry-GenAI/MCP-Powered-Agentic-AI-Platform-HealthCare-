from graph.state import AgentState

from agents.validator_agent import validator_agent
from tasks.validator_task import validator_task


def validator_node(state: AgentState) -> AgentState:

    answer = (
        state.get("modified_answer")
        or state.get("draft_answer", "")
    )

    task = validator_task(
        user_query=state["user_query"],
        context=state.get(
            "context",
            ""
        ),
        answer=answer,
        sources=state.get(
            "sources",
            []
        ),
        agent=validator_agent()
    )

    result = task.agent.execute_task(task)

    return {
        "validation_status": result.validation_status,
        "validation_reason": result.validation_reason,
        "final_answer": answer,
    }