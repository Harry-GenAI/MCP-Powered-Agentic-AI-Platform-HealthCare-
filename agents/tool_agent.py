from crewai import Agent
from mcp.mcp_server import send_email, web_search, query_database

def tool_agent():

    return Agent(
        
        role="Tool Agent",
        
        goal="""
        Execute external tools whenever required.
        """,
        
        backstory="""
        You are an expert executing actions with corresponding tool.

        Use query_database tool for employee database queries.

        Use send_email tool for sending emails.

        Use web_search tool for any information outside web.

        Always use appropriate tool.
        
        """,
        
        verbose=True
    )
