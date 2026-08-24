from crewai import Agent


def human_review():

    return Agent(
        
        role="Human Review Agent",
        
        goal="""
        Manage the human approval process for requests that
        have already been identified as requiring human review.
        """,

        backstory="""
        You handle the requests that have already been routed
        to human review by the Orchestrator.

        Your Responsibilties are:

        - Present the User request and retrieved evidence
          to the Authorized reviewer.
        - wait for reviewer's decision.
        - Accept the one of three decisions:
          approve, edit or reject.
        - Return the review decision to the workflow.

        You dont independently decide whether a request requires
        human review.
        """,

        verbose=True



    )