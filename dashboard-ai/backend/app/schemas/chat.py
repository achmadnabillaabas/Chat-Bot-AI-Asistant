"""
Pydantic schemas for chat API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message content")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID")
    model: Optional[str] = Field(None, description="AI model to use")
    knowledge_base_id: Optional[int] = Field(None, description="Knowledge base ID for RAG")
    rag_enabled: bool = Field(False, description="Enable RAG retrieval")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how are you?",
                "conversation_id": None,
                "model": "claude-3-5-sonnet",
                "knowledge_base_id": None,
                "rag_enabled": False
            }
        }


class TokenUsageResponse(BaseModel):
    """Token usage information."""
    input_tokens: int
    output_tokens: int
    total_tokens: int


class MessageResponse(BaseModel):
    """Single message response."""
    id: int
    role: str
    content: str
    model: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: int
    message: MessageResponse
    usage: TokenUsageResponse
    model: str
    sources: Optional[List['SourceInfo']] = None


class ConversationListItem(BaseModel):
    """Conversation list item."""
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: int = 0
    
    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Detailed conversation with messages."""
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True


class ComboInfo(BaseModel):
    """AI Combo information."""
    id: str
    name: str
    type: str = "combo"



class SourceInfo(BaseModel):
    """Source information for RAG responses."""
    document_id: int
    document_name: str
    pages: Optional[List[int]] = None
