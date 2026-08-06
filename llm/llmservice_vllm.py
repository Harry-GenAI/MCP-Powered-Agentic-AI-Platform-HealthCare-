from openai import OpenAI

client = OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)


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