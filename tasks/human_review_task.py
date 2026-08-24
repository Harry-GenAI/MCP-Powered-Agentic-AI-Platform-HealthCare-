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

        Wait for the authorized reviewer's decision.
        The reviewer can:
        - approve
        - modify
        - reject

        Return only valid JSON. Do not wrap it in Markdown.
        """
        ,

        expected_output="""A JSON object with exactly these keys:
        {
          "review_status": "approved, modified, or rejected",
          "reviewer_feedback": "short feedback",
          "modified_answer": "modified answer, or empty string"
        }
        """,

        agent=agent
    )
