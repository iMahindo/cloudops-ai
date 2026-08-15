from time import perf_counter
from app.core.logging import get_logger
from app.services.document_splitter import split_documents
from app.services.qdrant import get_vector_store, delete_document_chunks
from app.schemas.knowledge import KnowledgeDocument, IngestionResult, FailedDocument
from app.core.exceptions import DocumentIngestionException
from app.observability.metrics import (
    KNOWLEDGE_INGESTIONS_FAILURES_TOTAL,
    KNOWLEDGE_INGESTIONS_DURATION_SECONDS,
    KNOWLEDGE_INGESTIONS_CHUNKS_TOTAL,
    KNOWLEDGE_INGESTIONS_TOTAL
)

logger = get_logger(__name__)

def ingest_document(document: KnowledgeDocument) -> int:
    
    start_time = perf_counter()
    #get the source_type to incress the metric label
    source_type = document.metadata["source_type"]
    KNOWLEDGE_INGESTIONS_TOTAL.labels(
        source_type=source_type
    ).inc()

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

        #add the number of chunks to label metric
        KNOWLEDGE_INGESTIONS_CHUNKS_TOTAL.labels(
            source_type=source_type
        ).inc(chunk_count)

        return chunk_count
    except Exception as exc:
        logger.exception(
            "Failed to ingest document %s",
            document.document_id
        )

        #incress the total errors for label source_type
        KNOWLEDGE_INGESTIONS_FAILURES_TOTAL.labels(
            source_type=source_type
        ).inc()

        raise DocumentIngestionException(
            "Failed to ingest document"
        ) from exc
    finally:
        #add the duration to metric label
        duration = perf_counter() - start_time
        KNOWLEDGE_INGESTIONS_DURATION_SECONDS.labels(
            source_type=source_type
        ).observe(duration)

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