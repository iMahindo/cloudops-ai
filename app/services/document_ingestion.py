from pydantic import BaseModel

from pathlib import Path
from hashlib import sha256

from app.core.exceptions import DocumentIngestionException
from app.core.logging import get_logger
from app.services.document_loader import load_markdown_file
from app.services.document_splitter import split_documents
from app.services.qdrant import get_vector_store, delete_document_chunks

logger = get_logger(__name__)

class FailedDocument(BaseModel):
    path: str
    error: str

class IngestionResult(BaseModel):
    documents_processed: int
    chunks_stored: int
    failed_documents: list[FailedDocument]

def ingest_markdown_file(path: str | Path) -> int:
    try:
        logger.info(
            "Starting ingestion for document %s",
            path,
        )

        file_path = Path(path)

        #encode the path and create document id
        normalized_path = str(file_path.resolve())
        
        #document_id is a hash to create a better id
        document_id = sha256(
            normalized_path.encode("utf-8")
        ).hexdigest()

        #get the document content
        content = load_markdown_file(file_path)

        #create the metadata
        metadata = {
            "document_id": document_id,
            "source": normalized_path,
            "file_name": file_path.name,
            "source_type": "markdown"
        }

        #create the chunks
        documents = split_documents([content], metadatas=[metadata])

        #add the index metadata
        chunk_count = len(documents)

        for chunk_index, document in enumerate(documents):
            document.metadata["chunk_index"] = chunk_index
            document.metadata["chunk_count"] = chunk_count

        #delete the older document if exist
        delete_document_chunks(document_id)

        #add the documents to the vector store
        vector_store = get_vector_store()
        vector_store.add_documents(documents)

        logger.info(
            "Document ingestion completed successfully",
        )

        return len(documents)

    except Exception as exc:
        logger.exception(
            "Failed to ingest document",
        )
        raise DocumentIngestionException(
            "Failed to ingest document"
        ) from exc

def ingest_markdown_files(paths: list[str | Path]) -> IngestionResult:
    #initialize validation atributes
    documents_processed = 0
    chunks_stored = 0
    failed_documents =[]

    for path in paths:
        try:
            chunks_stored += ingest_markdown_file(path)
            documents_processed +=1
        except DocumentIngestionException as exc:
            logger.exception("Failed to ingest document %s",path)
            failed_document = FailedDocument(
                path = str(path),
                error= str(exc)
            )
            failed_documents.append(failed_document)

    return IngestionResult(
        documents_processed=documents_processed,
        chunks_stored=chunks_stored,
        failed_documents=failed_documents)

def ingest_markdown_directory(path: str | Path) -> IngestionResult:
    directory_path = Path(path)

    if not directory_path.exists():
        raise DocumentIngestionException(
            f"Directory not found: {directory_path}"
        )
    
    if not directory_path.is_dir():
        raise DocumentIngestionException(
            f"Path is not a directory: {directory_path}"
        )
    
    markdown_paths = list(directory_path.rglob("*.md"))

    return ingest_markdown_files(markdown_paths)