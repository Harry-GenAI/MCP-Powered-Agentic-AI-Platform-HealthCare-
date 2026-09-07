from crewai import Agent

#orchestrator agent
def orchestrator_agent():
    return Agent(
        role="",
        goal="",
        backstory="",
        verbose=True
    )


#h.r agent
def human_review_agent():
    return Agent(
        role="",
        goal=
        """
        Manage the human approval process for the requests that already
        categorized as needed for the human approval.
        """,
        backstory="dont approve yourself",
        verbose=True
    )

#validation agent
def validator_agent():
    return Agent(
        role="",
        goal="",
        backstory="checks: 1)relevance 2)grounding 3)",
        verbose=True
    )

#appointment agent
def appointment_agent():
    return Agent(
        role="",
        goal="extract required info from user's query to book the doc appointment",
        backstory="docname, specialization, date, time"
    )

