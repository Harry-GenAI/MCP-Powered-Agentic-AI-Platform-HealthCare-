from pathlib import path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))



def retry_node(state: AgentState) -> AgentState:

    return {
        "retry_count": state.get("retry_count", 0) + 1
    }