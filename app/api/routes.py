from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, status, File
from fastapi.responses import FileResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.rag import RAGRequest, RAGResponse
from app.schemas.knowledge_search import KnowledgeSearchRequest,KnowledgeSearchResponse
from app.schemas.knowledge import UploadKnowledgeResponse
from app.core.exceptions import LLMServiceException, RAGServiceException
from app.core.exceptions import KnowledgeSearchException
from app.services.llm import generate_response
from app.services.knowledge_search import search_knowledge
from app.services.rag import generate_rag_response
from app.services.knowledge_ingestion import ingest_uploaded_markdown

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

router = APIRouter(tags=["General"])

@router.get("/")
def read_root():
    #return a html
    return FileResponse(TEMPLATES_DIR / "index.html")

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

@router.post("/knowledge/upload", response_model = UploadKnowledgeResponse)
async def upload_knowledge_document(file: UploadFile = File(...)) -> UploadKnowledgeResponse:
    try:
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