"""
Token usage tracking model for analytics.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TokenUsage(Base):
    """Token usage tracking for each AI request."""
    
    __tablename__ = "token_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)
    
    # Model information
    model = Column(String, nullable=False)
    
    # Token counts
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    
    # Request metadata
    request_type = Column(String, nullable=False, default="chat")  # 'chat', 'embedding', etc.
    rag_enabled = Column(Integer, default=False)  # Changed from Boolean to Integer for SQLite compatibility
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="SET NULL"), nullable=True)
    
    # Performance metrics
    latency_ms = Column(Integer, nullable=True)  # Request latency in milliseconds
    
    # Cost estimation (optional)
    estimated_cost = Column(Float, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="token_usage")
    message = relationship("Message", back_populates="token_usage")
    knowledge_base = relationship("KnowledgeBase")
