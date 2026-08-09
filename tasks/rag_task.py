from crewai import Task


def rag_task(agent, user_request, route):

    return Task(

        description=f"""
        
        User Request:
        {user_request}

        selected Route:
        {route}

        If route is internal_rag

        Use employee_knowledge_search

        If route is external_rag

        Use customer_knowledge_search

        Return only retrieved information.
        
        """,

        expected_output="Retrieved company knowledge",
        
        agent=agent
    )