from typing import NotRequired, TypedDict

from app.schemas.rag import RAGSource


class RAGState(TypedDict):
    question: str
    requires_retrieval: NotRequired[bool]
    context: NotRequired[str]
    sources: NotRequired[list[RAGSource]]
    answer: NotRequired[str]
    is_valid: NotRequired[bool]
    