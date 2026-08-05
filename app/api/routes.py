from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import generate_response
from app.core.exceptions import LLMServiceException
from app.schemas.knowledge_search import KnowledgeSearchRequest,KnowledgeSearchResponse
from app.services.knowledge_search import search_knowledge
from app.core.exceptions import KnowledgeSearchException

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

@router.post("/knowledge/search", response_model = KnowledgeSearchResponse)
async def search_knowledge_endpoint(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    try:
        response = search_knowledge(query = request.query, limit = request.limit)
    
    except KnowledgeSearchException as exc:
        raise HTTPException (
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "The knowledge service is temporarily unavailable"
        ) from exc
    return response
