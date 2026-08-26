from crewai import Task




#Orchestrator task

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


REQUEST TYPE must be exactly one of:

- clinical
- business
- appointment
- general


ROUTE must be exactly one of:

- internal_rag
- vendor_rag
- query_database
- web_search
- appointment


RISK LEVEL must be exactly one of:

- low
- high


ROUTING REMINDER:

internal_rag = hospital's internal knowledge.

vendor_rag = vendor/supplier knowledge.

query_database = structured hospital staff/database information.

web_search = current public external information.

appointment = appointment booking/scheduling.


IMPORTANT:

Do not confuse vendor_rag with web_search.

vendor_rag is for vendor/supplier information already
available through the vendor knowledge base.

web_search is for current public external information.


Human review is NOT a route.

If risk_level is high, the LangGraph workflow will handle
human review separately.


Do not answer the user's question.

Only classify and route the request.

Return only valid JSON.
Do not wrap the JSON in Markdown.
""",

        expected_output="""
A valid JSON object with exactly these three keys:

{
    "request_type": "clinical | business | appointment | general",
    "route": "internal_rag | vendor_rag | query_database | web_search | appointment",
    "risk_level": "low | high"
}
""",

        agent=agent
    )



#Human Review task

def human_review_task(
    user_query,
    user_role,
    draft_answer,
    risk_level,
    context,
    sources,
    agent
):
    return Task(
        
        description=f"""
        Present high-risk request to the authorized human reviewer.

        User_Request:
        {user_query},

        Draft Answer:
        {draft_answer}
        
        Risk Level:
        {risk_level}
        
        User Role:
        {user_role}
        
        Retrieved Context:
        {context}
        
        Sources:
        {sources}

        Wait for the authorized reviewer's decision.
        The reviewer can:
        - approve
        - modify
        - reject

        Return only valid JSON. Do not wrap it in Markdown.
        """
        ,

        expected_output="""A JSON object with exactly these keys:
        {
          "review_status": "approved, modified, or rejected",
          "reviewer_feedback": "short feedback",
          "modified_answer": "modified answer, or empty string"
        }
        """,

        agent=agent
    )



#validator task

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
