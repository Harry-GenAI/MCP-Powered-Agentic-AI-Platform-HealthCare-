import asyncio
import sys
import traceback
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import mcp_tools.mcp_client as client


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")


async def main():
    print(f"Client Python: {sys.executable}")
    print(f"MCP server: {client.SERVER_PATH}")

    try:
        async with asyncio.timeout(120):
            await client.init_mcp()

        async with asyncio.timeout(120):
            tools = await client._session.list_tools()

        print("Tools:")
        for tool in tools.tools:
            print(f"- {tool.name}")

        async with asyncio.timeout(120):
            result = await client.call_tool(
                "text_cleaner",
                {"text": "mcp    is    responding"},
            )

        print(f"text_cleaner result: {result}")

        async with asyncio.timeout(120):
            db_result = await client.call_tool(
                "internal_hospital_knowledge_search",
                {
                    "query": (
                        "hypertension symptoms"
                    )
                },
            )

        print("query_database result:")
        print(db_result)

    except Exception:
        print("MCP check failed:")
        traceback.print_exc()

    finally:
        await client.close_mcp()


if __name__ == "__main__":
    asyncio.run(main())
