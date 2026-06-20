import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def rewrite_query(query:str, history:str)->str:

    prompt = f"""
    You are a Query Rewrite Assistant.

    Your job is to rewrite the User's Vague question to standalone question which
    is comprimised for semnatic search in knowledge database.

    Rules:
    -Do not answer the query
    -Do not ask follow-up questions
    -Do not change the meaning of the query
    -check for grammitical errors
    -Use chat history below to If user's question consists of these words "It", "that", "this" or "there"
    -If question is vague then choose best topic from chathistory to make the better question
    -If user asked a new topic from previous chat history, then don't include old chat history topics in rewritten query.

    examples:
    Chat History: User asked about HR's leave policy.
    user : what about that?
    Rewritten Query: what about company's HR's leave policy?

    Chat History: User asked about HR's leave policy.
    user: what is refund time?
    Rewritten query: what is the refund processing time?

    Chat History:
    {history}

    User Query:
    {query}
    
    Rewritten Query:
    """
    response = client.responses.create(
        input=prompt,
        model="gpt-5-nano",
        max_output_tokens=300,
        reasoning={"effort": "minimal"},#query rewriting doesn't need deep reasoning, which will save tokens..
        
    )

    rewritten_query = response.output_text.strip()
    return rewritten_query or query.strip()
