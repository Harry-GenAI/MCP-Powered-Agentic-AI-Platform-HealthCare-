from pathlib import Path
import sys
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PATH = Path(__file__).with_name("mcp_server.py")

_stack = None
_session = None

#----explanation 3----

async def init_mcp():
    global _stack, _session

    if _session is not None:
        return

    _stack = AsyncExitStack()
    await _stack.__aenter__()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)]
    )

    read_stream, write_stream = await _stack.enter_async_context(
        stdio_client(server_params)
    )

    _session = await _stack.enter_async_context(
        ClientSession(read_stream, write_stream)
    )

    await _session.initialize()


async def call_tool(tool_name: str, arguments: dict) -> str:
    await init_mcp()

    result = await _session.call_tool(
        tool_name,
        arguments
    )

    parts = []

    for item in result.content:
        text = getattr(item, "text", None)
        if text:
            parts.append(text)
        else:
            parts.append(str(item))

    return "\n".join(parts)


async def close_mcp():
    global _stack, _session

    if _stack:
        await _stack.aclose()

    _stack = None
    _session = None