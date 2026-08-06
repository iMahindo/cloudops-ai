from typing import Any
from pydantic import BaseModel, Field

# Request model
class KnowledgeSearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Text used to search the knowledge base",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results to return",
    )

# Individual search result
# metadata={"document_id", "source"},
class KnowledgeSearchResult(BaseModel):
    content: str
    metadata: dict[str, Any]

# Complete search response
class KnowledgeSearchResponse(BaseModel):
    results: list[KnowledgeSearchResult]