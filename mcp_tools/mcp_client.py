from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# MCP Server Path
SERVER_PATH = Path(__file__).with_name("mcp_server.py")


def format_result(result) -> str:
    """
    Convert MCP response into plain text.
    """
    parts = []

    for item in result.content:
        text = getattr(item, "text", None)

        if text:
            parts.append(text)
        else:
            parts.append(str(item))

    return "\n".join(parts)


async def call_tool(tool_name: str, arguments: dict) -> str:
    """
    Generic MCP Tool Caller.

    Args:
        tool_name: Name of the MCP tool.
        arguments: Dictionary containing tool inputs.

    Returns:
        Tool response as string.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)]
    )
    
    #launch the mcp server, create connection, initializes the connection/session
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments
            )

            return format_result(result)


async def list_available_tools():
    """
    Returns all available MCP tool names.
    """

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)]
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            tools = await session.list_tools()

            return [tool.name for tool in tools.tools]