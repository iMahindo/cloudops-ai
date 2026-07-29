from groq import AsyncGroq

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

client = AsyncGroq(api_key=settings.groq_api_key)

async def generate_response(prompt: str) -> str:
    logger.info(
            "Sending LLM request using model %s",
            settings.groq_model,
        )
    
    #Async request
    chat_completion = await client.chat.completions.create(
        model = settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un Cloud Ops assistant. "
                    "Debes dar respuestas claras, precisas y concisas."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    response = chat_completion.choices[0].message.content

    if response is None:
        raise ValueError("Groq has return an empty response")

    logger.info("LLM response generated succesfully")

    return response