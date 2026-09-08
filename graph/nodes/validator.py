from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState

from graph.agents import validator_agent
from graph.tasks import validator_task




async def validator_node(state: AgentState) -> AgentState:

    answer = (
        state.get("modified_answer")
        or state.get("draft_answer", "")
    )

    task = validator_task(
        user_query=state["rewritten_query"],
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

    result = await task.agent.aexecute_task(task)
    data = json.loads(getattr(result, "raw", result))

    return {
        "validation_status": data["validation_status"],
        "validation_reason": data["validation_reason"],
        "final_answer": answer,
    }
