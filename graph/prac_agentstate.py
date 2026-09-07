from typing import TypedDict

class AgentState(TypedDict):
    
    #user
    user_query:str
    user_role:str
    conversation_history: list
    
    #orchestrator
    request_type:str
    route:str
    risk_level:str
    
    #Appointment
    appointment_doc:str
    specialization:str
    date:str
    time:str
    result:str

    #rag
    context:str
    sources:list
    retrieval_status:str

    #tool
    tool_result:str

    #llm
    draft_answer:str

    #human_review
    review_status:str
    review_feedback:str
    modified_answer:str

    #retry
    retry:int

    #validatation status
    validation:str
    validation_feedback:str

    #final_answer
    final_answer:str