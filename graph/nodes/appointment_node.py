from pathlib import Path
import sys
import json

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from graph.state import AgentState
from graph.agents import appointment_agent
from graph.tasks import appointment_task
from mcp_tools.mcp_client import call_tool


async def appointment_node(
    state: AgentState
) -> AgentState:

    # --------------------------------------------------------
    # Extract appointment information
    # --------------------------------------------------------

    task = appointment_task(
        user_request=state["rewritten_query"],
        agent=appointment_agent()
    )

    result = task.agent.execute_task(task)

    data = json.loads(
        getattr(result, "raw", result)
    )

    doctor = data["doctor"]
    specialization = data["specialization"]
    appointment_date = data["appointment_date"]
    appointment_time = data["appointment_time"]

    # --------------------------------------------------------
    # Call MCP appointment tool
    # --------------------------------------------------------

    appointment_result = await call_tool(
        "book_appointment",
        {
            "doctor": doctor,
            "specialization": specialization,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time
        }
    )

    return {
        "appointment_doctor": doctor,
        "appointment_specialization": specialization,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "appointment_result": appointment_result,
        "final_answer": appointment_result
    }