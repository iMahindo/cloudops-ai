from pydantic import BaseModel, Field


class RAGRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Question answered using the internal knowledge base",
    )

class RAGSource(BaseModel):
    name: str
    chunk_index: int

class RAGResponse(BaseModel):
    answer: str
    sources: list[RAGSource]

class RAGQuestionClassification(BaseModel):
    requires_retrieval: bool