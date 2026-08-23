from crewai import Task


def validator_task(
    user_query,
    context,
    answer,
    sources,
    agent
):
    return Task(
        description=f"""
Validate the generated response against the available evidence.

User Query:
{user_query}

Retrieved Context:
{context}

Generated Answer:
{answer}

Sources:
{sources}

Check that the answer:
- addresses the user's query
- is supported by the available context
- does not introduce unsupported facts
- is clear and professionally formatted

If the answer is sufficient, approve it.
If important information is missing or the answer is not
adequately grounded, identify the reason for retry.
""",
        expected_output="""
A validation result containing:
- validation status
- reason
""",
        agent=agent
    )