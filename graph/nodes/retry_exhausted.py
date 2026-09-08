from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState



def retry_exhausted_node(state:AgentState)->AgentState:

    return {
        "final_answer":"I couldn't generate a sufficiently validated response. "
        "Please try rephrasing your question or contact an authorized healthcare professional."
    }