from crewai import Task

def orchestrator_task(agent, user_request):

    return Task(
        
        description=f"""
        Analyze the following request.

        User Request:
        {user_request}

        Decide Only One route:

        - employee_knowledge_search
        - customer_knowledge_search
        - query_database
        - send_email
        - web_search
        - text_cleaner

        Return Only the route name.

        Do not answer the User.

        Do not explain
        
        """,

        expected_output="One routing label",

        agent = agent

    )