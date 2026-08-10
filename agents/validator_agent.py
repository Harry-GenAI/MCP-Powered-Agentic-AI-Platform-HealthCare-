from crewai import Agent


def validator_agent():

    return Agent(
        role="Validator Agent",
        
        goal=""" 
        Validate, Organize and improve the final answer.
        """,
        
        backstory=""" 
        Ensure the Final Response is:

        - Correct
        - Concise
        - Professional
        - Well formatted

        Remove unnecssary information.
        
        Preserver factual correctness.
        """,
        
        verbose=True

    )