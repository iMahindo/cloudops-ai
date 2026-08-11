from app.core.logging import get_logger
from app.services.document_splitter import split_documents
from app.services.qdrant import get_vector_store, delete_document_chunks
from app.schemas.knowledge import KnowledgeDocument, IngestionResult, FailedDocument
from app.core.exceptions import DocumentIngestionException

logger = get_logger(__name__)

def ingest_document(document: KnowledgeDocument) -> int:
    try:
        #create the chunks
        documents = split_documents([document.content], metadatas=[document.metadata])

        #add the index metadata
        chunk_count = len(documents)

        for chunk_index, chunk in enumerate(documents):
            chunk.metadata["chunk_index"] = chunk_index
            chunk.metadata["chunk_count"] = chunk_count

        #delete the older document if exist
        delete_document_chunks(document.document_id)

        #add the documents to the vector store
        vector_store = get_vector_store()
        vector_store.add_documents(documents)

        logger.info(
            "Document ingestion completed successfully",
        )

        return len(documents)
    except Exception as exc:
        logger.exception(
            "Failed to ingest document %s",
            document.document_id
        )
        raise DocumentIngestionException(
            "Failed to ingest document"
        ) from exc

def ingest_documents(documents: list[KnowledgeDocument]) -> IngestionResult:
    documents_processed = 0
    chunks_stored = 0
    failed_documents =[]
    
    for document in documents:
        try:
            chunks_stored += ingest_document(document)
            documents_processed +=1 
        except DocumentIngestionException as exc:
            logger.exception("Failed to ingest document %s",document.document_id)
            failed_document = FailedDocument(
                document_id = document.document_id,
                source=document.metadata["source"],
                error= str(exc)
            )
            failed_documents.append(failed_document)

    return IngestionResult(
        documents_processed=documents_processed,
        chunks_stored=chunks_stored,
        failed_documents=failed_documents)