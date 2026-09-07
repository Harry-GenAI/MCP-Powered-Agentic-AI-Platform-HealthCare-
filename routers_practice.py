from graph.state import AgentState

#route after orchestrator
def route_after_orch(state:Agentstate)-> AgentState:
    
    route = state["route"]
    if route == "internal_rag":
        retrun "rag"
    
    elif state["route"] in ("enternal_rag", "query_database", "websearch"):
        return "tool"

    else:
        print("invalid request please enter a new request")


#route after response
def route_after_response(state:AgentState)->AgentState:

    if state["risk_level"] == "high":
        return "human_review"
    
    else:
        return "validator"



#route after human review
def route_after_human_review(state:AgentState)-> AgentState:

    if state["rview_status"] == "approval":
        return "validate"

    else:
        return "rejection" 


max_retries = 2



#route after validator
def route_after_validator(state:AgentState)->AgentState:

    if state["validation_status"] == "valid":
        return "end"
    
    if state["retry_count"] > max_retries:
        return "retry_exhausted"
    
    else:
        return "retry"
