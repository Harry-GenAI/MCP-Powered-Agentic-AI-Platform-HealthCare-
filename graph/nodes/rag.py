from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


from graph.state import AgentState
from rag.rag import retrieve_context



def rag_node(state:AgentState)->AgentState:

    query = state.get(
        "rewritten_query",
        state["user_query"]
    )

    result = retrieve_context(query)

    return {
        "context": result["context"],
        "sources": result["sources"],
        "retrieval_status":result["retrieval_status"]
    }





