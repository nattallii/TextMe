import json

from openai import AsyncOpenAI

from src.security.config import settings


client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)


class AIService:

    async def generate_smart_replies(
        self,
        message: str,
    ):
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate 3 short natural "
                        "chat replies. "
                        "Return JSON array only."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=0.7,
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        return json.loads(content)