from pathlib import Path

from app.core.logging import get_logger
from app.schemas.knowledge import IngestionResult
from app.services.document_ingestion import ingest_documents
from app.sources.local_markdown import load_markdown_directory

logger = get_logger(__name__)

def ingest_local_markdown_directory(path: str | Path) -> IngestionResult:
    documents = load_markdown_directory(path)

    return ingest_documents(documents)
