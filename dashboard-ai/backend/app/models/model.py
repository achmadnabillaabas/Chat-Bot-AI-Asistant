"""
AI Model configuration model.
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Model(Base):
    """AI Model configuration and management."""
    
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model identification
    name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    provider = Column(String, nullable=False)  # e.g., 'openai', 'anthropic', 'meta'
    
    # Model type
    model_type = Column(String, default="chat")  # 'chat' or 'embedding'
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Pricing (per 1M tokens)
    input_cost_per_million = Column(Float, nullable=True)
    output_cost_per_million = Column(Float, nullable=True)
    
    # Performance
    max_tokens = Column(Integer, nullable=True)
    context_window = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
