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

If the answer is sufficient, set validation_status to valid.
If important information is missing or the answer is not
adequately grounded, set validation_status to invalid and identify the
reason for retry.

Return only valid JSON. Do not wrap it in Markdown.
""",
        expected_output="""
A JSON object with exactly these keys:
{
  "validation_status": "valid or invalid",
  "validation_reason": "short explanation"
}
""",
        agent=agent
    )
