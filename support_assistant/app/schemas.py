from pydantic import BaseModel, Field
from typing import List

class QueryRequest(BaseModel):
    query: str = Field(..., description="Customer support input query")

class SupportResponse(BaseModel):
    answer: str = Field(..., description="The generated response text")
    sources: List[str] = Field(default_factory=list, description="Document or chunk IDs used to ground the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")