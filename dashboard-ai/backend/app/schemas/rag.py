"""
Pydantic schemas for RAG API.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class RAGSearchRequest(BaseModel):
    """Schema for RAG search request."""
    query: str = Field(..., min_length=1, description="Search query")
    knowledge_base_id: int = Field(..., description="Knowledge base ID to search in")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")


class RAGSourceResponse(BaseModel):
    """Schema for a single source document."""
    document_id: int
    document_name: str
    pages: Optional[List[int]] = None


class RAGResultItem(BaseModel):
    """Schema for a single RAG search result."""
    document_id: int
    document_name: str
    chunk_id: int
    page_number: Optional[int]
    text: str
    score: float


class RAGSearchResponse(BaseModel):
    """Schema for RAG search response."""
    query: str
    knowledge_base_id: int
    results: List[RAGResultItem]
    sources: List[RAGSourceResponse]
