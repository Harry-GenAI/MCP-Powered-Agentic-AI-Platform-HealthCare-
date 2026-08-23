from pathlib import path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState


def rejection_node(state: AgentState) -> AgentState:

    return {
        "final_response": (
            "Your request was not approved by the "
            "authorized healthcare reviewer. "
            "Please contact the appropriate healthcare "
            "professional for further assistance."
        )
    }