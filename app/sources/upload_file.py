from hashlib import sha256
from pathlib import Path

from app.schemas.knowledge import KnowledgeDocument


def load_uploaded_markdown(file_name: str, content: bytes) -> KnowledgeDocument:
    file_path = Path(file_name)
    
    #validate the extension
    if file_path.suffix.lower() != ".md":
        raise ValueError(f"File is not a Markdown file: {file_path}")
    
    source = f"upload://{file_name}"

    #document_id is a hash to create a better id
    document_id = sha256(source.encode("utf-8")).hexdigest()

    content_str = content.decode("utf-8")

    #create the metadata
    metadata = {
        "document_id": document_id,
        "source": source,
        "file_name": file_path.name,
        "source_type": "upload"
    }

    return KnowledgeDocument(
        document_id=document_id,
        content=content_str,
        metadata=metadata
    )