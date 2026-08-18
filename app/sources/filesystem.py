from hashlib import sha256
from pathlib import Path

from app.core.logging import get_logger
from app.schemas.knowledge import KnowledgeDocument
from app.services.file_reader import read_file

logger = get_logger(__name__)

def load_markdown_document(path: str | Path) -> KnowledgeDocument:
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

    return KnowledgeDocument(
        document_id=document_id,
        content=content,
        metadata=metadata
    )

def load_markdown_documents(paths: list[str | Path]) -> list[KnowledgeDocument]:
    documents = []
    for path in paths:
        document = load_markdown_document(path)
        documents.append(document)
    return documents

def load_markdown_directory(path: str | Path) -> list[KnowledgeDocument]:
    directory_path = Path(path)

    if not directory_path.exists():
        raise FileNotFoundError(
            f"Directory not found: {directory_path}"
        )
    
    if not directory_path.is_dir():
        raise ValueError(
            f"Path is not a directory: {directory_path}"
        )
    
    markdown_paths = list(directory_path.rglob("*.md"))

    return load_markdown_documents(markdown_paths)

def load_markdown_file(path: str | Path) -> str:
    file_path = Path(path)

    if file_path.suffix.lower() != ".md":
        raise ValueError(f"File is not a Markdown file: {file_path}")

    return read_file(file_path)