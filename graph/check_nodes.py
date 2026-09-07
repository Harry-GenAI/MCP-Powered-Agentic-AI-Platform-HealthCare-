
#testing validator_node with rag_results

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()
'''
from graph.nodes.validator_node import validator_node
from rag.rag import retrieve_context
from llm.llm_service import generate_reply
from prompts.prompts import build_prompt
'''
import asyncio



while False:

    try:
        query = input("\n enter query:")
        
        results = retrieve_context(query)
        
        prompt = build_prompt(results["context"], query)
        
        answer = asyncio.run(generate_reply(prompt))
        
        state = {
        "user_query":query,
        "context":results["context"],
        "draft_answer":answer,
        "sources":results["sources"]
        }
        
        result = validator_node(state)
        
        print(f"\n result:\n {result}, \n answer:{answer}")
        
    
    except Exception as e:
        print("error is:", e)

        continue



#checking validator_node with tool results

from graph.nodes.tool_node import tool_node

async def main():

    while True:

        try:
            query = input("\n enter query:")

            state = {
                "user_query": query,
                "route": "web_search",
                "context": "",
                "draft_answer": "",
                "sources": []
            }

            tool_result = await tool_node(state)

            state["context"] = tool_result["tool_result"]

            prompt = build_prompt(
                state["context"],
                state["user_query"]
            )

            answer = await generate_reply(prompt)

            state["draft_answer"] = answer

            result = await asyncio.to_thread(
                validator_node,
                state
            )

            print(
                f"\nresult:\n{tool_result}"
                f"\nresult:\n{result}"
                f"\nanswer:\n{answer}"
            )

        except Exception as e:
            print("error is:", e)
            continue


#asyncio.run(main())



#checking appointment node

# checking appointment node

from graph.nodes.appointment_node import appointment_node


async def appointment_test():

    while True:

        try:
            query = input("\n enter appointment query: ")

            state = {
                "user_query": query
            }

            result = await appointment_node(state)

            print(
                f"\nAppointment Result:\n{result}"
            )

        except Exception as e:
            print("error is:", e)
            continue


asyncio.run(appointment_test())