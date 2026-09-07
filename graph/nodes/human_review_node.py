from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState

from graph.agents import human_review
from graph.tasks import human_review_task



def human_review_node(state: AgentState) -> AgentState:

    task = human_review_task(
        user_query=state["rewritten_query"],
        draft_answer=state["draft_answer"],
        risk_level=state["risk_level"],
        user_role=state.get(
            "user_role",
            "unknown"
        ),
        context=state.get(
            "context",
            ""
        ),
        sources=state.get(
            "sources",
            []
        ),
        agent=human_review()
    )

    result = task.agent.execute_task(task)
    data = json.loads(getattr(result, "raw", result))

    return {
        "review_status": data["review_status"],
        "reviewer_feedback": data["reviewer_feedback"],
        "modified_answer": data.get("modified_answer", ""),
    }
