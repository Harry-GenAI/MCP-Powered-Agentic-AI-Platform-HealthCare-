from crewai import Task

def orchestrator_task(agent, query):

    return Task(
        description=f"""
        Analyze the following request.

        User Request:
        {query}

        Decide ONLY ONE route:

        - employee_knowledge_search
        - customer_knowledge_search
        - query_database
        - send_email
        - web_search
        - text_cleaner

        IMPORTANT ROUTING RULE:

        If the user query contains an employee leave code such as
        LV-101, LV-102, LV-103, etc.,
        ALWAYS route to:

        employee_knowledge_search

        These LV-xxx codes refer to employee leave-policy information,
        NOT database queries.

        Examples:
        LV-101 -> employee_knowledge_search
        LV-102 -> employee_knowledge_search
        LV-103 -> employee_knowledge_search

        Return ONLY the route name.

        Do not answer the User.
        Do not explain.
        """,

        expected_output="Only one route name from the allowed routes.",
        agent=agent
    )