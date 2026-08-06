from pydantic import BaseModel, Field

class RAGRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Question answered using the internal knowledge base",
    )

class RAGSource(BaseModel):
    file_name: str
    chunk_index: int

class RAGResponse(BaseModel):
    answer: str
    sources: list[RAGSource]