from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import generate_response
from app.core.exceptions import LLMServiceException

router = APIRouter(tags=["General"])

@router.get("/")
def read_root():
    return {"message": "Welcome to CloudOps AI"}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        response = await generate_response(request.prompt)
    except LLMServiceException as exc:
        raise HTTPException (
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "The model service is temporarily unavailable"
        )from exc
        
    return ChatResponse(response=response)