import pytest
from types import SimpleNamespace

from langchain_core.documents import Document

from app.services import document_ingestion
from app.core.exceptions import DocumentIngestionException

def test_ingest_markdown_file_loads_splits_and_stores_documents(monkeypatch) -> None:
    stored_documents = []

    def mock_load_markdown_file(path):
        return "Markdown content"

    def mock_split_documents(texts):
        return [
            Document(
                page_content="Chunk content"
            )
        ]

    mock_vector_store = SimpleNamespace(
        add_documents=lambda documents: stored_documents.extend(documents)
    )

    def mock_get_vector_store():
        return mock_vector_store

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        mock_load_markdown_file,
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        mock_split_documents,
    )

    monkeypatch.setattr(
        document_ingestion,
        "get_vector_store",
        mock_get_vector_store,
    )

    document_ingestion.ingest_markdown_file(
        "guide.md"
    )

    assert len(stored_documents) == 1
    assert stored_documents[0].page_content == "Chunk content"

def test_ingest_markdown_file_passes_loaded_content_to_splitter(monkeypatch) -> None:
    captured_texts = []

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Markdown content",
    )

    def mock_split_documents(texts):
        captured_texts.extend(texts)

        return [
            Document(
                page_content="Chunk"
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
            add_documents=lambda documents: None
        ),
    )

    document_ingestion.ingest_markdown_file(
        "guide.md"
    )

    assert captured_texts == [
        "Markdown content"
    ]

def test_ingest_markdown_file_raises_document_ingestion_exception_when_storage_fails(monkeypatch) -> None:

    monkeypatch.setattr(
        document_ingestion,
        "load_markdown_file",
        lambda path: "Markdown content",
    )

    monkeypatch.setattr(
        document_ingestion,
        "split_documents",
        lambda texts: [
            Document(
                page_content="Chunk"
            )
        ],
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
        document_ingestion.ingest_markdown_file(
            "guide.md"
        )