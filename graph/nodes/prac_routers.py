from state import AgentState

#route after orchestrator
def route_after_orchestrator(state:AgentState):

    if state["route"] == "internal_rag":
        return "rag"
    
    if state["route"] in ("websearch", "query_database"):
        return "tool"
    
    if state["route"] == "appointment":
        return "appointment"

#route after rag
def route_after_rag(state:AgentState):

    if state["retrieval_status"] == "sufficient":
        return "response"
    
    else:
        return "tool"


#route after human review
def route_after_human_review(state:AgentState):

    pass

    #if reviewstatus is approve validator

    #if review status is reject , "rejection"


max_retries = 2

# route after validator
def route_after_validator(state:AgentState):

    if state["validation_status"] == "approved":
        return "end"
    
    if state["retry_count"] > max_retries:

        return "retry_exhausted"
    
    return "retry"


