from hashlib import sha256

import pytest

from app.schemas.knowledge import KnowledgeDocument
from app.sources import upload_file


def test_load_uploaded_markdown_returns_knowledge_document() -> None:
    file_name = "guide.md"
    content = b"# CloudOps Guide"

    document = upload_file.load_uploaded_markdown(
        file_name,
        content,
    )

    source = "upload://guide.md"

    expected_document_id = sha256(
        source.encode("utf-8")
    ).hexdigest()

    assert isinstance(
        document,
        KnowledgeDocument,
    )

    assert document.document_id == expected_document_id
    assert document.content == "# CloudOps Guide"

    assert document.metadata == {
        "document_id": expected_document_id,
        "source": source,
        "file_name": "guide.md",
        "source_type": "upload",
    }


def test_load_uploaded_markdown_accepts_uppercase_extension() -> None:
    document = upload_file.load_uploaded_markdown(
        "guide.MD",
        b"Markdown content",
    )

    assert document.content == "Markdown content"


def test_load_uploaded_markdown_raises_when_file_is_not_markdown() -> None:
    with pytest.raises(ValueError):
        upload_file.load_uploaded_markdown(
            "guide.txt",
            b"Plain text",
        )


def test_load_uploaded_markdown_decodes_utf8_content() -> None:
    content = "Guía técnica con acentos".encode(
        "utf-8"
    )

    document = upload_file.load_uploaded_markdown(
        "guide.md",
        content,
    )

    assert document.content == "Guía técnica con acentos"


def test_load_uploaded_markdown_generates_same_id_for_same_file_name() -> None:
    first_document = upload_file.load_uploaded_markdown(
        "guide.md",
        b"First version",
    )

    second_document = upload_file.load_uploaded_markdown(
        "guide.md",
        b"Second version",
    )

    assert (
        first_document.document_id
        == second_document.document_id
    )


def test_load_uploaded_markdown_stores_only_file_name_in_metadata() -> None:
    document = upload_file.load_uploaded_markdown(
        "folder/guide.md",
        b"Markdown content",
    )

    assert document.metadata["file_name"] == "guide.md"