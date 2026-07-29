from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import generate_response

router = APIRouter(tags=["General"])

@router.get("/")
def read_root():
    return {"message": "Welcome to CloudOps AI"}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
     response = await generate_response(request.prompt)

     return ChatResponse(response=response)