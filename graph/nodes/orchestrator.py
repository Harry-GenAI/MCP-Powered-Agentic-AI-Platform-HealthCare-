from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState
from agents.orchestrator import orchestrator_agent
from tasks.orchestrator_task import orchestrator_task


def orchestrator_node(state:AgentState)-> AgentState:

    task = orchestrator_task(
        user_request=state["user_query"],
        user_role=state["user_role"],
        conversation_history=state["conversation_history"],
        agent=orchestrator_agent()

    )

    result = task.agent.execute_task(task)
    data = json.loads(getattr(result, "raw", result))

    return {
        "route":data["route"],
        "risk_level":data["risk_level"]
    }
