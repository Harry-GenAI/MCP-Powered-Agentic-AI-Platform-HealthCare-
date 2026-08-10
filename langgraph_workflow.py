from typing import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from dotenv import load_dotenv
import asyncio

#Agents
from agents.orchestrator import orchestrator_agent
from agents.rag_agent import rag_agent
from agents.tool_agent import tool_agent
from agents.validator_agent import validator_agent
from agents.human_review import human_review_agent

#Tasks
from tasks.orchestrator_task import orchestrator_task
from tasks.rag_task import rag_task
from tasks.tool_task import tool_task
from tasks.validator_task import validator_task
from tasks.human_review_task import human_review_task

#MCP Client
from mcp_tools.mcp_client import call_tool


load_dotenv()



#Shared State
class AgentState(TypedDict):
    user_query : str
    rewritten_query : str
    route : str
    response : str
    approval : str


#Nodes
def orchestrator_node(state:AgentState):
    agent = orchestrator_agent()
    task = orchestrator_task(agent, state["rewritten_query"])
    result = agent.execute_task(task)
    state["route"] = result.strip().lower()

    return state

async def rag_node(state:AgentState):

    result = await call_tool(
        state["route"], {
            "query":state["rewritten_query"]
            }
    )

    state["response"] = result

    return state

async def tool_node(state:AgentState):

    result = await call_tool(
        state["route"], {
            "query":state["rewritten_query"]
            }
    )

    state["response"] = result

    return state

async def human_review_node(state:AgentState):

    agent = human_review_agent()

    task = human_review_task(agent, state["rewritten_query"])

    result = agent.execute_task(task)

    state["approval"] = result

    return state

async def sql_node(state:AgentState):

    result = await call_tool(
        "query_database", {
            "query":state["rewritten_query"]
        } 
    )

    state["response"] = result

    return state

async def validator_node(state: AgentState):

    result = await call_tool(
        "text_cleaner",
        {
            "text": state["response"]
        }
    )

    state["response"] = result

    return state


#Main Routing function
def route_request(state:AgentState):

    route = state["route"]

    if route in ("employee_knowledge_search", "customer_knowledge_search"):
        return "rag"
    
    elif route == "query_database":
        return "human_review"
    
    else:
        return "tool"

#Human Approval Routing
def approval_route(state:AgentState):

    if state["approval"] == "allow":
        return "sql"
    
    return END


# LangGraph
graph = StateGraph(AgentState)


#add nodes
graph.add_node("orchestrator", orchestrator_node)
graph.add_node("rag", rag_node)
graph.add_node("tool", tool_node)
graph.add_node("human_review", human_review_node)
graph.add_node("sql", sql_node)
graph.add_node("validator", validator_node)


#Entry point
graph.set_entry_point("orchestrator")


#Conditional Routing
graph.add_conditional_edges(
    "orchestrator", route_request, {
        "rag" : "rag",
        "human_review" : "human_review",
        "tool" : "tool"
    }
)

#RAG/Tool -> Validator
graph.add_edge("rag", "validator")
graph.add_edge("tool", "validator")


#Human Review -> SQL or END
graph.add_conditional_edges(
    "human_review", approval_route, {
        "allow" : "sql",
        END : END
    }
)

# SQL -> validator
graph.add_edge("sql", "validator")

#Final Node
graph.add_edge("validator", END)


#check-point memory + compile + invoke

#prototype invocation
if __name__ == "__main__":

    async def main():
        
        async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as memory:
            
            app = graph.compile(checkpointer=memory)
            
            config = {
            "configurable": {
                "thread_id": "demo-user-1"
            }
            }
            
            initial_state = {
            "user_query": "What is the annual leave policy?",
            "rewritten_query": "What is the annual leave policy?",
            "route": "",
            "response": "",
            "approval": ""
            }
            
            result = await app.ainvoke(
            initial_state,
            config=config
            )
            
            print("\nFinal response:\n")
            print(result["response"])

    
    asyncio.run(main())



