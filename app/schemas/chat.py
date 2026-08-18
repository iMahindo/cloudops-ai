from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field (
        min_length = 1,
        description = "Pregunta o instrucción enviada al LLM",
    )

class ChatResponse(BaseModel):
    response: str