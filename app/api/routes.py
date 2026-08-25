from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import (
    KnowledgeSearchException,
    LLMServiceException,
    RAGServiceException,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.knowledge import (
    NotionIngestionRequest,
    NotionIngestionResponse,
    UploadKnowledgeResponse,
)
from app.schemas.knowledge_search import KnowledgeSearchRequest, KnowledgeSearchResponse
from app.schemas.rag import RAGRequest, RAGResponse
from app.services.knowledge_ingestion import (
    ingest_notion_page,
    ingest_uploaded_markdown,
)
from app.services.knowledge_search import search_knowledge
from app.services.llm import generate_response
from app.services.rag import generate_rag_response

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

router = APIRouter(tags=["General"])

@router.get("/")
def read_root():
    #return a html
    return FileResponse(TEMPLATES_DIR / "index.html")

@router.get("/test-error")
def test_error():
    raise RuntimeError("Test error")

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

@router.post("/knowledge/upload", response_model = UploadKnowledgeResponse, include_in_schema=settings.ingestion_enabled)
async def upload_knowledge_document(file: UploadFile = File(...)) -> UploadKnowledgeResponse:
    try:
        if not settings.ingestion_enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must have a filename",
            )

        content = await file.read()

        chunks_stored = ingest_uploaded_markdown(file_name=file.filename, content = content)

        return UploadKnowledgeResponse(
            file_name= file.filename,
            chunks_stored= chunks_stored
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException (
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(exc)
    )from exc 
    except Exception as exc:
        raise HTTPException (
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "The upload service is temporarily unavailable"
    )from exc

@router.post("/knowledge/notion", response_model = NotionIngestionResponse, include_in_schema=settings.ingestion_enabled)
def insert_notion_page(request: NotionIngestionRequest) -> NotionIngestionResponse:
    try:
        if not settings.ingestion_enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        if not request.page_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notion page ID must not be empty",
            )
        
        chunks_stored = ingest_notion_page(page_id=request.page_id)

        return NotionIngestionResponse(
            page_id=request.page_id,
            chunks_stored = chunks_stored 
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException (
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "The notion ingestion service is temporarily unavailable"
    )from exc 

@router.get("/config")
def get_public_config() -> dict[str, bool]:
    return {
        "ingestion_enabled": settings.ingestion_enabled,
    }