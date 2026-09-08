from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState

from prompts.prompts import build_prompt
from llm.llm_service import generate_reply



async def response_node(state: AgentState) -> AgentState:

    context = state.get("context", "")

    tool_result = state.get(
        "tool_result",
        ""
    )

    if tool_result:
        context = tool_result

    query = state.get(
        "rewritten_query",
        state["user_query"]
    )

    prompt = build_prompt(
        context=context,
        question=query
    )

    draft_answer = await generate_reply(
        prompt
    )

    return {
        "draft_answer": draft_answer
    }