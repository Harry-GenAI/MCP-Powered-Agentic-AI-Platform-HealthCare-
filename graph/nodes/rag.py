from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


from graph.state import AgentState
from rag.rag import retrieve_context


def rag_node(state: AgentState) -> AgentState:

    query = state.get(
        "rewritten_query",
        state["user_query"]
    )

    (
        _retrieved_docs,
        _top_docs,
        sources,
        context
    ) = retrieve_context(query)

    return {
        "context": context,
        "sources": sources,
    }





