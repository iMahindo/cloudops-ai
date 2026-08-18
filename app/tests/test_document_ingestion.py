from types import SimpleNamespace

import pytest
from langchain_core.documents import Document

from app.core.exceptions import DocumentIngestionException
from app.schemas.knowledge import (
    FailedDocument,
    IngestionResult,
    KnowledgeDocument,
)
from app.services import document_ingestion


def test_ingest_document_splits_and_stores_documents(monkeypatch) -> None:
    stored_documents = []

    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "test",
        },
    )

    def mock_split_documents(texts, metadatas=None):
        return [
            Document(
                page_content="Chunk content",
                metadata=metadatas[0].copy(),
            )
        ]

    mock_vector_store = SimpleNamespace(
        add_documents=lambda documents: stored_documents.extend(
            documents
        )
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: mock_vector_store,
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    chunk_count = document_ingestion.ingest_document(
        document
    )

    assert chunk_count == 1
    assert len(stored_documents) == 1
    assert stored_documents[0].page_content == "Chunk content"


def test_ingest_document_passes_content_and_metadata_to_splitter(monkeypatch) -> None:
    captured = {}

    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "test",
        },
    )

    def mock_split_documents(texts, metadatas=None):
        captured["texts"] = texts
        captured["metadatas"] = metadatas

        return [
            Document(
                page_content="Chunk",
                metadata=metadatas[0].copy(),
            )
        ]

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: None,
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    document_ingestion.ingest_document(
        document
    )

    assert captured["texts"] == [
        "Document content"
    ]

    assert captured["metadatas"] == [
        {
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "test",
        }
    ]


def test_ingest_document_adds_chunk_position_metadata(monkeypatch) -> None:
    stored_documents = []

    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "test",
        },
    )

    def mock_split_documents(texts, metadatas=None):
        return [
            Document(
                page_content="First chunk",
                metadata=metadatas[0].copy(),
            ),
            Document(
                page_content="Second chunk",
                metadata=metadatas[0].copy(),
            ),
            Document(
                page_content="Third chunk",
                metadata=metadatas[0].copy(),
            ),
        ]

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: stored_documents.extend(
                documents
            ),
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    document_ingestion.ingest_document(
        document
    )

    assert stored_documents[0].metadata["chunk_index"] == 0
    assert stored_documents[1].metadata["chunk_index"] == 1
    assert stored_documents[2].metadata["chunk_index"] == 2

    assert all(
        chunk.metadata["chunk_count"] == 3
        for chunk in stored_documents
    )


def test_ingest_document_deletes_existing_chunks(monkeypatch) -> None:
    deleted_document_ids = []

    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "test",
        },
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts, metadatas=None: [
            Document(
                page_content="Chunk",
                metadata=metadatas[0].copy(),
            )
        ],
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: deleted_document_ids.append(
            document_id
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: None,
        ),
    )

    document_ingestion.ingest_document(
        document
    )

    assert deleted_document_ids == [
        "document-123"
    ]


def test_ingest_document_deletes_before_storing(monkeypatch) -> None:
    operations = []

    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "test",
        },
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts, metadatas=None: [
            Document(
                page_content="Chunk",
                metadata=metadatas[0].copy(),
            )
        ],
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: operations.append(
            "delete"
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: operations.append(
                "store"
            ),
        ),
    )

    document_ingestion.ingest_document(
        document
    )

    assert operations == [
        "delete",
        "store",
    ]


def test_ingest_document_raises_document_ingestion_exception_when_storage_fails(monkeypatch) -> None:
    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "test",
        },
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts, metadatas=None: [
            Document(
                page_content="Chunk",
                metadata=metadatas[0].copy(),
            )
        ],
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    def mock_get_vector_store():
        raise RuntimeError(
            "Qdrant unavailable"
        )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        mock_get_vector_store,
    )

    with pytest.raises(DocumentIngestionException):
        document_ingestion.ingest_document(
            document
        )


def test_ingest_documents_continues_when_one_document_fails(monkeypatch) -> None:
    processed_document_ids = []

    first_document = KnowledgeDocument(
        document_id="first",
        content="First document",
        metadata={
            "document_id": "first",
            "source": "source-first",
            "source_type": "test",
        },
    )

    broken_document = KnowledgeDocument(
        document_id="broken",
        content="Broken document",
        metadata={
            "document_id": "broken",
            "source": "source-broken",
        },
    )

    third_document = KnowledgeDocument(
        document_id="third",
        content="Third document",
        metadata={
            "document_id": "third",
            "source": "source-third",
        },
    )

    def mock_ingest_document(document):
        processed_document_ids.append(
            document.document_id
        )

        if document.document_id == "broken":
            raise DocumentIngestionException(
                "Failed to ingest document"
            )

        if document.document_id == "first":
            return 2

        return 3

    monkeypatch.setattr(
        document_ingestion,
        "ingest_document",
        mock_ingest_document,
    )

    result = document_ingestion.ingest_documents(
        [
            first_document,
            broken_document,
            third_document,
        ]
    )

    assert processed_document_ids == [
        "first",
        "broken",
        "third",
    ]

    assert isinstance(
        result,
        IngestionResult,
    )

    assert result.documents_processed == 2
    assert result.chunks_stored == 5

    assert len(result.failed_documents) == 1

    failed_document = result.failed_documents[0]

    assert isinstance(
        failed_document,
        FailedDocument,
    )

    assert failed_document.document_id == "broken"
    assert failed_document.source == "source-broken"
    assert failed_document.error == "Failed to ingest document"


def test_ingest_documents_returns_empty_result_for_empty_documents(monkeypatch) -> None:
    def mock_ingest_document(document):
        raise AssertionError(
            "ingest_document should not be called"
        )

    monkeypatch.setattr(
        document_ingestion,
        "ingest_document",
        mock_ingest_document,
    )

    result = document_ingestion.ingest_documents(
        []
    )

    assert isinstance(
        result,
        IngestionResult,
    )

    assert result.documents_processed == 0
    assert result.chunks_stored == 0
    assert result.failed_documents == []

def test_ingest_document_updates_metrics_on_success(monkeypatch) -> None:
    calls = SimpleNamespace(
        total=0,
        failures=0,
        duration=0,
        chunks=0,
    )

    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "filesystem",
        },
    )

    chunks = [
        Document(
            page_content="First chunk",
            metadata={},
        ),
        Document(
            page_content="Second chunk",
            metadata={},
        ),
        Document(
            page_content="Third chunk",
            metadata={},
        ),
    ]

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_TOTAL",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                inc=lambda: setattr(
                    calls,
                    "total",
                    calls.total + 1,
                )
            )
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_FAILURES_TOTAL",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                inc=lambda: setattr(
                    calls,
                    "failures",
                    calls.failures + 1,
                )
            )
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_DURATION_SECONDS",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                observe=lambda value: setattr(
                    calls,
                    "duration",
                    calls.duration + 1,
                )
            )
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_CHUNKS_TOTAL",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                inc=lambda value: setattr(
                    calls,
                    "chunks",
                    calls.chunks + value,
                )
            )
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts, metadatas=None: chunks,
    )

    monkeypatch.setattr(
        document_ingestion,
        "delete_document_chunks",
        lambda document_id: None,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        lambda: SimpleNamespace(
            add_documents=lambda documents: None,
        ),
    )

    result = document_ingestion.ingest_document(document)

    assert result == 3
    assert calls.total == 1
    assert calls.failures == 0
    assert calls.duration == 1
    assert calls.chunks == 3

def test_ingest_document_updates_metrics_on_failure(monkeypatch) -> None:
    calls = SimpleNamespace(
        total=0,
        failures=0,
        duration=0,
        chunks=0,
    )

    document = KnowledgeDocument(
        document_id="document-123",
        content="Document content",
        metadata={
            "document_id": "document-123",
            "source": "test-source",
            "source_type": "filesystem",
        },
    )

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_TOTAL",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                inc=lambda: setattr(
                    calls,
                    "total",
                    calls.total + 1,
                )
            )
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_FAILURES_TOTAL",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                inc=lambda: setattr(
                    calls,
                    "failures",
                    calls.failures + 1,
                )
            )
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_DURATION_SECONDS",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                observe=lambda value: setattr(
                    calls,
                    "duration",
                    calls.duration + 1,
                )
            )
        ),
    )

    monkeypatch.setattr(
        document_ingestion,
        "KNOWLEDGE_INGESTIONS_CHUNKS_TOTAL",
        SimpleNamespace(
            labels=lambda **kwargs: SimpleNamespace(
                inc=lambda value: setattr(
                    calls,
                    "chunks",
                    calls.chunks + value,
                )
            )
        ),
    )

    def failing_split_documents(texts, metadatas=None):
        raise RuntimeError("Chunking failed")

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        failing_split_documents,
    )

    with pytest.raises(DocumentIngestionException):
        document_ingestion.ingest_document(document)

    assert calls.total == 1
    assert calls.failures == 1
    assert calls.duration == 1
    assert calls.chunks == 0