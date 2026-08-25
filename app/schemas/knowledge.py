from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    document_id: str
    content: str
    metadata: dict

class FailedDocument(BaseModel):
    document_id: str
    source: str
    error: str

class IngestionResult(BaseModel):
    documents_processed: int
    chunks_stored: int
    failed_documents: list[FailedDocument]

class UploadKnowledgeResponse(BaseModel):
    file_name: str
    chunks_stored: int

class NotionIngestionRequest(BaseModel):
    page_id: str = Field(
        min_length=1,
        max_length=200,
        pattern=r"\S",
    )

class NotionIngestionResponse(BaseModel):
    page_id: str
    chunks_stored: int