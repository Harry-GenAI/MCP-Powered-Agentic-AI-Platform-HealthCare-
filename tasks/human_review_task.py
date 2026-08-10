from crewai import Task

def human_review_task(agent, query):

    return Task(
        description=f"""
        Review this database request:

        User Request: {query}

        If the request requires sensitive employee information,
        return ONLY: allow

        Otherwise return ONLY: deny

        Do not explain.
        Do not ask for OTP.
        Do not mention OTP.
        """,
        
        expected_output="Either 'allow' or 'deny'.",
        agent=agent
    )
































