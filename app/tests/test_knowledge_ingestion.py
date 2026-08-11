import pytest

from app.schemas.knowledge import IngestionResult, KnowledgeDocument
from app.services import knowledge_ingestion


def test_ingest_local_markdown_directory_loads_and_ingests_documents(monkeypatch) -> None:
    captured = {}

    documents = [
        KnowledgeDocument(
            document_id="doc-1",
            content="First document",
            metadata={
                "document_id": "doc-1",
                "source": "source-1",
            },
        ),
        KnowledgeDocument(
            document_id="doc-2",
            content="Second document",
            metadata={
                "document_id": "doc-2",
                "source": "source-2",
            },
        ),
    ]

    expected_result = IngestionResult(
        documents_processed=2,
        chunks_stored=5,
        failed_documents=[],
    )

    def mock_load_markdown_directory(path):
        captured["path"] = path
        return documents

    def mock_ingest_documents(received_documents):
        captured["documents"] = received_documents
        return expected_result

    monkeypatch.setattr(
        knowledge_ingestion,
        "load_markdown_directory",
        mock_load_markdown_directory,
    )

    monkeypatch.setattr(
        knowledge_ingestion,
        "ingest_documents",
        mock_ingest_documents,
    )

    result = knowledge_ingestion.ingest_local_markdown_directory(
        "knowledge"
    )

    assert captured["path"] == "knowledge"
    assert captured["documents"] == documents
    assert result == expected_result

def test_ingest_local_markdown_directory_passes_empty_documents_to_ingestion(monkeypatch) -> None:
    captured = {}

    expected_result = IngestionResult(
        documents_processed=0,
        chunks_stored=0,
        failed_documents=[],
    )

    monkeypatch.setattr(
        knowledge_ingestion,
        "load_markdown_directory",
        lambda path: [],
    )

    def mock_ingest_documents(documents):
        captured["documents"] = documents
        return expected_result

    monkeypatch.setattr(
        knowledge_ingestion,
        "ingest_documents",
        mock_ingest_documents,
    )

    result = knowledge_ingestion.ingest_local_markdown_directory(
        "knowledge"
    )

    assert captured["documents"] == []
    assert result == expected_result

def test_ingest_local_markdown_directory_propagates_source_error(monkeypatch) -> None:
    def mock_load_markdown_directory(path):
        raise FileNotFoundError(
            "Directory not found"
        )

    monkeypatch.setattr(
        knowledge_ingestion,
        "load_markdown_directory",
        mock_load_markdown_directory,
    )

    with pytest.raises(FileNotFoundError):
        knowledge_ingestion.ingest_local_markdown_directory(
            "missing"
        )