from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.rag import RAGRequest, RAGResponse
from app.schemas.knowledge_search import KnowledgeSearchRequest,KnowledgeSearchResponse
from app.core.exceptions import LLMServiceException, RAGServiceException
from app.core.exceptions import KnowledgeSearchException
from app.services.llm import generate_response
from app.services.knowledge_search import search_knowledge
from app.services.rag import generate_rag_response


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
        response = await search_knowledge(query = request.query, limit = request.limit)
    
    except KnowledgeSearchException as exc:
        raise HTTPException (
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "The knowledge service is temporarily unavailable"
        ) from exc
    return response

@router.post("/rag/ask", response_model = RAGResponse)
async def rag_ask(request: RAGRequest) -> RAGResponse:
    try:
        response = await generate_rag_response(question=request.question)
    except RAGServiceException as exc:
        raise HTTPException (
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "The RAG service is temporarily unavailable"
        )from exc
    return response