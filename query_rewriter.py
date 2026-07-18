from dotenv import load_dotenv
from openai import AsyncOpenAI
from logger import logger
import time

load_dotenv()

# Local vLLM server
client = AsyncOpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)

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
- Do not answer the question.
- Do not ask follow-up questions.
- Do not change the meaning.
- Fix grammar if needed.
- Use chat history only when necessary.
- If the question is already standalone, return it unchanged.
- If the user starts a new topic, ignore previous chat history.

Chat History:
{history}

User Query:
{query}

Rewritten Query:
"""

    start = time.time()

    response = await client.chat.completions.create(
        model="private-llm",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.0,
        max_tokens=128
    )

    rewritten_query = response.choices[0].message.content.strip()

    logger.debug(
        f"Rewritten query took {(time.time() - start):.3f} secs"
    )

    return rewritten_query or query.strip()