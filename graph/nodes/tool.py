from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from graph.state import AgentState

from mcp_tools.mcp_client import call_tool


async def tool_node(state: AgentState) -> AgentState:

    route = state["route"]
    query = state.get(
        "rewritten_query",
        state["user_query"]
    )

    # Map LangGraph routes to MCP server tool names.
    tool_map = {
        "query_database": "query_database",
        "web_search": "web_search",
        "external_rag": "external_patient_services_search",
    }

    tool_name = tool_map.get(route)

    if not tool_name:
        raise ValueError(
            f"Unsupported MCP route: {route}"
        )

    if tool_name == "query_database":
        arguments = {
            "sql": query
        }
    else:
        arguments = {
            "query": query
        }

    result = await call_tool(
        tool_name,
        arguments
    )

    return {
        "tool_result": result
    }