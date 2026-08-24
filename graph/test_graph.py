from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from graph.workflow import builder
from graph.checkpointer import create_checkpointer


checkpointer = create_checkpointer()
graph = builder.compile(checkpointer)


config = {
        "configurable": {
            "thread_id": "test-001"
        }
    }


input = input("\n enter query: ")

initial_state = {
        "user_query": input,
        "user_role": "patient",
        "conversation_history": [],
        "route": "",
        "risk_level": "",
        "context": "",
        "sources": [],
        "answer": "",
        "tool_result": "",
        "review_status": "",
        "review_result": "",
        "validation_status": "",
        "validation_result": "",
        "final_response": "",
        "retry_count": 0,
    }

while True:
    
    result = graph.invoke(initial_state, config=config)
    print("\n final restul:\n", result)

 