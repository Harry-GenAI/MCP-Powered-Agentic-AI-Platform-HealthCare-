from crewai import Task


#orchestrator task
def orchestrator_task(user_query, conversation_history, agent):
    return Task(
        description="1)request_type, 2)route =>1)internal rag, 2)vend rag, 3)query_database, 4)web_search 5)appointment, 3)risk_level",
        expected_output="A valid json with these 3",
        agent=agent
    )



#human review task
def human_review_task(user_query, draft_answer, sources, context, sources, agent):
    return Task(
        description="",
        expected_output="a valid json, 1) review_status, 2)review_feed 3) modified_answer",
        agent=agent
    )

#validation task


#appointment task
def appointment_task(user_request, agent):
    pass

#validation task

def validation_task(query, context, draft_answer, sources, agent):
