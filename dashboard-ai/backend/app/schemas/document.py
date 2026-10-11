"""
Pydantic schemas for Document API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    knowledge_base_id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str]
    chunk_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list response."""
    items: List[DocumentResponse]
    total: int


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    id: int
    filename: str
    status: str
    message: str
