from openai import OpenAI
from middleware.retry import retry
from middleware.timeout import timeout
from middleware.rate_limit import rate_limit

client = OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)


@retry
@timeout(60)
@rate_limit(1,1)
async def generate_reply(prompt: str) -> str:

    response = client.chat.completions.create(
        model="private-llm",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=150
    )
    
    return response.choices[0].message.content.strip()