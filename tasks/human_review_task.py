from crewai import Task


def human_review_task(agent, user_request):

    return Task(

        description=f"""
        User Request:

        {user_request}

        If sensitive information is requested:
        
        - Require OTP verification.
        - If OTP succeeds, allow execution.
        - Otherwise, deny execution.
        """,

        expected_output="Approval decision.",

        agent=agent
    )
































