from dotenv import load_dotenv
from openai import AsyncOpenAI
from logger import logger
import time

load_dotenv()

client = AsyncOpenAI()

VAGUE_WORDS = {
    "it", "this", "that", "these", "those",
    "they", "them", "there", "here",
    "above", "below", "same", "previous"
}


async def rewrite_query(query: str, history: str) -> str:

    words = query.lower().split()

    # Skip rewriting for clear standalone questions
    if not (
        len(words) <= 8
        or any(word.strip("?.!,") in VAGUE_WORDS for word in words)
    ):
        return query.strip()

    prompt = f"""
You are a Query Rewrite Assistant.

Your job is to rewrite the User's vague question into a standalone question
optimized for semantic search.

Rules:
- Do not change the meaning.
- Do not explain the rewrite.
- Do not ask follow-up questions.
- Do not answer the question.
- Fix grammatical errors.
- Use chat history below for vague words like "it", "that", "there", "this", "same", or "previous".
- If the query is vague, use the most relevant topic in the chat history and rewrite the query.
- If the user starts a new topic, ignore the previous chat history.
- If chat history is empty, rewrite using only the current query.
- Never ask the user to provide chat history.
- If the query is already a clear standalone question, return it unchanged.
- Return ONLY the rewritten query.

Examples:

Chat History: user asked about HR leave policy
User: what about that?
Rewritten Query: What is the company's HR leave policy?

Chat History: user asked about HR leave policy
User: what is refund time?
Rewritten Query: What is the refund processing time?

Chat History:
{history}

User Query:
{query}

Rewritten Query:
"""

    start = time.time()

    response = await client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    rewritten_query = response.output_text.strip()
    

    return rewritten_query or query.strip()