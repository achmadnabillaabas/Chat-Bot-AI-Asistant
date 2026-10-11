"""
Telegram bot configuration model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base


class TelegramConfig(Base):
    """Telegram bot configuration and status."""
    
    __tablename__ = "telegram_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Bot information
    bot_token = Column(String, nullable=False)
    bot_id = Column(BigInteger, nullable=True)  # Telegram bot user ID
    bot_username = Column(String, nullable=True)
    bot_name = Column(String, nullable=True)  # Bot display name
    
    # Configuration
    combo_id = Column(String, nullable=True)  # Selected AI Combo
    webhook_url = Column(String, nullable=True)  # For future webhook support
    
    # Status
    is_active = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=False)
    
    # Polling state
    last_update_id = Column(BigInteger, default=0)  # Last processed update ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_connected_at = Column(DateTime(timezone=True), nullable=True)

