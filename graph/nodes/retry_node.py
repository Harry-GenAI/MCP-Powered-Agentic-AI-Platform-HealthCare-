from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState



def retry_node(state: AgentState) -> AgentState:

    return {
        "retry_count": state.get("retry_count", 0) + 1
    }