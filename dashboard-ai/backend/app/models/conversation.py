"""
Conversation and Message models for chat history.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Conversation(Base):
    """Conversation (chat session) model."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False, default="New Conversation")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """Message model for individual chat messages."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    
    # Role: 'user' or 'assistant'
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    # Model used for this message (if assistant)
    model = Column(String, nullable=True)
    
    # RAG context
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=True)
    rag_enabled = Column(Boolean, default=False)
    rag_context = Column(Text, nullable=True)  # JSON string of retrieved chunks
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    knowledge_base = relationship("KnowledgeBase")
    token_usage = relationship("TokenUsage", back_populates="message", uselist=False, cascade="all, delete-orphan")
