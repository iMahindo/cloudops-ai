from pathlib import Path

from app.core.exceptions import DocumentIngestionException
from app.core.logging import get_logger
from app.services.document_loader import load_markdown_file
from app.services.document_splitter import split_documents
from app.services.qdrant import get_vector_store

logger = get_logger(__name__)

def ingest_markdown_file(path: str | Path) -> None:
    try:
        logger.info(
            "Starting ingestion for document %s",
            path,
        )

        #get the document content
        content = load_markdown_file(path)

        #create the chunks
        documents = split_documents([content])

        #gadd the documents to the vector store
        vector_store = get_vector_store()
        vector_store.add_documents(documents)

        logger.info(
            "Document ingestion completed successfully",
        )

    except Exception as exc:
        logger.exception(
            "Failed to ingest document",
        )
        raise DocumentIngestionException(
            "Failed to ingest document"
        ) from exc