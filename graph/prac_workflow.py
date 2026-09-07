from langgraph.graph import StateGraph, START,END

from nodes import orchestrator_node, appointment_node, rag_node, tool_node, human_review_node, response_node, validator_node, retry_exhausted_node
from graph.routers import route_after_orchestrator, route_after_rag, route_after_response, route_after_review, route_after_validation
from routers import route_after_orchestrator, route_after_rag, route_after_response, route_after_review, route_after_validation

from state import AgentState

#initiate the graph
builder = StateGraph(AgentState)

#add nodes
builder.add_node("orhcestrator", orchestrator_node)

builder.add_node("appointment", appointment_node)

builder.add_node("rag", rag_node)

#entry point
builder.set_entry_point("orchestrator")


#add conditional edges
builder.add_conditional_edges(
    "orchestrator", 
    route_after_orchestrator, 
    {
        "rag":"rag",
        "appointment":"appointment",
        "tool":"tool"

})

builder.add_conditional_edges(
    "rag",
    route_after_rag,
    {
        "response":"response",
        "tool":"tool"
    }
)

builder.add_edge("appointment", END)

builder.add_conditional_edges("tool", "response")

builder.add_conditional_edges(
    "response", 
    route_after_response, 
    {
        "human_review":"human_review",
        "validator":"validator"

})

builder.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "validator":"validator",
        "rejected":"rejected"
    }
)

builder.add_conditional_edges(
    {
        "end":END,
        "retry":"retry",
        "retry_exhausted":"retry_exhausted"


    }
)

builder.add_edge("rejected", END)

builder.add_edge("retry", "response")

graph = builder