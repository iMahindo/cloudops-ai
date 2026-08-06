from langchain_core import messages
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMServiceException

logger = get_logger(__name__)

llm = ChatGroq(
    model=settings.groq_model,
    api_key=settings.groq_api_key,
    temperature=0,
)

async def generate_response(prompt: str) -> str:
    logger.info(
            "Sending LLM request using model %s",
            settings.groq_model,
        )
    
    try:
        message = await llm.ainvoke(
            [
                (
                    "system",
                    (
                        "Eres un Cloud Ops assistant. "
                        "Debes dar respuestas claras, precisas y concisas."
                    ),
                ),
                ("human", prompt),
            ]
        )
    except Exception as exc:
        logger.exception(
            "%s Failed to generate LLM response",
            settings.groq_model,
        )
        
        raise LLMServiceException(
            "The LLM provider failed to generate a response"
        ) from exc

    response = message.content

    if response is None:
        raise LLMServiceException(
            "The LLM provider failed to generate a response"
        )

    if not isinstance(response, str) or not response.strip():
        raise LLMServiceException(
            "The LLM response failed to generate a response"
        )

    logger.info("LLM response generated succesfully")

    return response