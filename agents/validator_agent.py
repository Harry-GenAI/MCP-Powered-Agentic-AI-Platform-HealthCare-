from crewai import Agent
from mcp.mcp_server import text_cleaner

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