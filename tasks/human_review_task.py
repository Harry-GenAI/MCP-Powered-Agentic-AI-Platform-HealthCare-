from crewai import Task


def human_review_task(
    user_query,
    user_role,
    draft_answer,
    risk_level,
    context,
    sources,
    agent
):
    return Task(
        
        description=f"""
        Present high-risk request to the authorized human reviewer.

        User_Request:
        {user_query},

        Draft Answer:
        {draft_answer}
        
        Risk Level:
        {risk_level}
        
        User Role:
        {user_role}
        
        Retrieved Context:
        {context}
        
        Sources:
        {sources}

        Wait for the authorized reviewers decision.
        The reviewer can:
        - approve
        - modify
        - reject

        Return the reviewrs decision and feedback to the workflow
        """
        ,

        expected_output="""A structured human review decision containing:

        - review_status: approved, modified, or rejected
        - reviewer_feedback
        - modified_answer, when the reviewer modifies the answer
        """,

        agent=agent
    )