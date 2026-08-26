from pathlib import Path
import sys
import asyncio

sys.path.append(str(Path(__file__).resolve().parent.parent))

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from graph.workflow import builder
from mcp_tools.mcp_client import close_mcp

async def main():
    config = {
        "configurable": {
            "thread_id": "test-001"
        }
    }


    user_input = input("\n enter query: ")

    initial_state = {
        "user_query": user_input,
        "user_role": "patient",
        "conversation_history": [],
        "route": "",
        "risk_level": "",
        "context": "",
        "sources": [],
        "draft_answer": "",
        "tool_result": "",
        "review_status": "",
        "reviewer_feedback": "",
        "modified_answer": "",
        "validation_status": "",
        "validation_reason": "",
        "final_answer": "",
        "retry_count": 0,
    }

    async with AsyncSqliteSaver.from_conn_string("memory/langgraph_checkpoints.db") as checkpointer:
        graph = builder.compile(checkpointer)

        try:
            result = await graph.ainvoke(initial_state, config=config)
            print("\n final result:\n", result)
        finally:
            await close_mcp()

asyncio.run(main())
