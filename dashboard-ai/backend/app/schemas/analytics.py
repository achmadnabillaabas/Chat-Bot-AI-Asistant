"""
Pydantic schemas for analytics API.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class UsageSummary(BaseModel):
    """Overall token usage summary."""
    total_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int


class DailyUsage(BaseModel):
    """Token usage for a specific day."""
    date: date
    input_tokens: int
    output_tokens: int
    total_tokens: int
    requests: int


class ComboUsage(BaseModel):
    """Token usage by AI Combo."""
    combo_id: str
    requests: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    avg_input_tokens: float
    avg_output_tokens: float


class ConversationUsage(BaseModel):
    """Token usage by conversation."""
    conversation_id: int
    conversation_title: str
    requests: int
    input_tokens: int
    output_tokens: int
    total_tokens: int


class RequestDetail(BaseModel):
    """Individual request detail."""
    id: int
    created_at: datetime
    conversation_id: Optional[int]
    conversation_title: Optional[str]
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    request_type: str
    rag_enabled: bool
    knowledge_base_id: Optional[int] = None
    latency_ms: Optional[int]
    
    class Config:
        from_attributes = True


class RequestHistory(BaseModel):
    """Paginated request history."""
    items: List[RequestDetail]
    total: int
    page: int
    page_size: int
    pages: int
