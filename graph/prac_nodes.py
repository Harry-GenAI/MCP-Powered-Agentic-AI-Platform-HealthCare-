from state import AgentState
from agents import orchestrator_agent, appointment_agent, human_review, validator_agent
from tasks import orchestrator_task, appointment_task, human_review_task, validator_task

from mcp_tools.mcp_client import call_tool

import json

#orchestrator node
def orchestrator_node(state:AgentState)->AgentState:

    user_query = state["user_query"]
    conversation_history= state["conversation_history"]

    agent = orchestrator_agent()
    task = orchestrator_task(user_query, "", conversation_history, agent)

    result = task.agent.execute_task(task)

    data = json.loads(result)

    return {
        "route":result["route"],
        "risk_level":result["risk_level"]
    }

#appointment node


#rag node

#tool node
async def tool_node(state:AgentState)->AgentState:

    result = await call_tool(state["route"], state["user_query"])

    data = json.loads(result)

    return {
        "tool_result":data["tool_result"]
    }

#response node

#h.r node
def human_review_node(state:AgentState)->AgentState:

    return {
        "review_status":"",
        "feed":"",
        "modified_answer":""

    }


#validation node

#rejection node
def rejection_node(state:AgentState)->AgentState:

    return{
        "final_output":"the doctor reviewd and rejected ur request.."
    }

#retry node
def retry_node(state:AgentState)->AgentState:

    return{
        "retry":state["retry_count"]+1
    }

#



