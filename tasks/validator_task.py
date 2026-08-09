from crewai import Task


def validator_task(agent, context):

    return Task(

        description=f"""
        Validate the following response.

        {context}

        Improve formatting.

        Remove duplicate information.

        Preserve factual correctness.

        Return final response.
        """,

        expected_output="Clean final answer.",

        agent=agent
    )