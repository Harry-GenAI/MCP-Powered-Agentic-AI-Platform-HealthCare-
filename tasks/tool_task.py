from crewai import Task


def tool_task(agent, user_request, route):

    return Task(

        description=f"""
        User Request:

        {user_request}

        Selected Route:

        {route}

        Execute ONLY the required MCP tool.

        sql

        email

        web_search

        clean_text

        Do not use unnecessary tools.

        Return tool output.
        """,

        expected_output="Tool execution result.",

        agent=agent
    )