from pathlib import Path

from app.core.logging import get_logger
from app.schemas.knowledge import IngestionResult
from app.services.document_ingestion import ingest_document, ingest_documents
from app.sources.filesystem import load_markdown_directory
from app.sources.upload_file import load_uploaded_markdown
from app.sources.notion import load_notion_page

logger = get_logger(__name__)

def ingest_local_markdown_directory(path: str | Path) -> IngestionResult:
    logger.info(
        "Ingesting local markdown directory %s",
        path
    )
    documents = load_markdown_directory(path)

    return ingest_documents(documents)

def ingest_uploaded_markdown (file_name:str, content: bytes) -> int:
    logger.info(
        "Ingesting uploaded markdown file %s",
        file_name
    )
    document = load_uploaded_markdown(file_name, content)

    return ingest_document(document)

def ingest_notion_page (page_id:str) -> int:
    logger.info(
        "Ingesting notion page %s",
        page_id
    )
    document = load_notion_page(page_id=page_id)

    return ingest_document(document)