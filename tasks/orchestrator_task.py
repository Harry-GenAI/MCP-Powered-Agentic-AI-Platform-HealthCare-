
from crewai import Task



def orchestrator_task(
    user_request,
    user_role,
    conversation_history,
    agent
):
    return Task(
        description=f"""
Analyze the user's request and determine:

1. request_type
2. route
3. risk_level

User Query:
{user_request}

User Role:
{user_role}

Conversation History:
{conversation_history}

Return a structured routing decision.

request_type must be one of:
- clinical
- business
- appointment
- general

route must be one of:
- internal_rag
- external_rag
- query_database
- web_search
- appointment

risk_level must be one of:
- low
- high

Do not answer the user's question.
Only classify and route the request.

Return only valid JSON. Do not wrap it in Markdown.
""",

        expected_output="""
A JSON object with exactly these keys:
{
  "request_type": "clinical, business, appointment, or general",
  "route": "internal_rag, external_rag, query_database, web_search, or appointment",
  "risk_level": "low or high"
}
""",

        agent=agent
    )
