"""
Pydantic schemas for Knowledge Base API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KnowledgeBaseCreate(BaseModel):
    """Schema for creating a knowledge base."""
    name: str = Field(..., min_length=1, max_length=255, description="Knowledge base name")
    description: Optional[str] = Field(None, description="Optional description")


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a knowledge base."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base response."""
    id: int
    name: str
    description: Optional[str]
    collection_name: str
    document_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class KnowledgeBaseListResponse(BaseModel):
    """Schema for knowledge base list response."""
    items: List[KnowledgeBaseResponse]
    total: int
