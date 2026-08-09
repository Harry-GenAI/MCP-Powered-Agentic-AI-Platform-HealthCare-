from crewai import Agent


def rag_agent():

    return Agent(
        role="RAG Agent",
        
        goal="""
        Retrieve accurate information from the correct
        company knowledge base.
         """,
        backstory= """ 
        You specialize in retrieving company knowledge.
        Identify whether the request is about:
        
        - Internal employee knowledge
        - Customer-facing knowledge
        
        Return accurate information.
        """,
        
        verbose=True
    )